"""
Main API module for the Blueprint Graph application.

This module provides a FastAPI application for interacting with the detection engine.
"""
import os
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from src.utils import settings, log, db
from src.core import DetectionRule, DetectionAlert, detection_engine
from src.schemas import ocsf_schema
import time


# Create FastAPI application
app = FastAPI(
    title="Blueprint Graph API",
    description="API for the Blueprint Graph OCSF Detection Engine",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class RuleCreate(BaseModel):
    """Model for creating a detection rule."""
    name: str = Field(..., description="Human-readable name for the rule")
    description: str = Field(..., description="Description of what the rule detects")
    severity: int = Field(..., ge=1, le=10, description="Severity level (1-10)")
    query: str = Field(..., description="Cypher query to execute for detection")
    tags: List[str] = Field(default_factory=list, description="List of tags for categorization")
    mitre_techniques: List[str] = Field(default_factory=list, description="List of MITRE ATT&CK techniques")
    enabled: bool = Field(True, description="Whether the rule is enabled")


class RuleResponse(BaseModel):
    """Model for rule response."""
    rule_id: str = Field(..., description="Unique identifier for the rule")
    name: str = Field(..., description="Human-readable name for the rule")
    description: str = Field(..., description="Description of what the rule detects")
    severity: int = Field(..., description="Severity level (1-10)")
    query: str = Field(..., description="Cypher query to execute for detection")
    tags: List[str] = Field(default_factory=list, description="List of tags for categorization")
    mitre_techniques: List[str] = Field(default_factory=list, description="List of MITRE ATT&CK techniques")
    enabled: bool = Field(..., description="Whether the rule is enabled")


class AlertResponse(BaseModel):
    """Model for alert response."""
    alert_id: str = Field(..., description="Unique identifier for the alert")
    rule_id: str = Field(..., description="ID of the rule that generated the alert")
    timestamp: str = Field(..., description="Timestamp when the alert was generated")
    severity: int = Field(..., description="Severity level (1-10)")
    entities: List[Dict[str, Any]] = Field(..., description="List of entities involved in the alert")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context information")


class EventCreate(BaseModel):
    """Model for creating an event."""
    event: Dict[str, Any] = Field(..., description="Event data")
    source_format: str = Field("unknown", description="Source format of the event")


class EventResponse(BaseModel):
    """Model for event response."""
    id: str = Field(..., description="Unique identifier for the event")
    event: Dict[str, Any] = Field(..., description="Event data")


class GraphQueryRequest(BaseModel):
    query: str


# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Blueprint Graph API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Check database connection
        result = db.execute_query("RETURN 1 as test")
        if result and result[0]["test"] == 1:
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "error"}
    except Exception as e:
        log.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/health/kafka", response_model=Dict[str, Any])
async def kafka_health():
    """
    Check Kafka health.
    
    Returns:
        Kafka health status
    """
    try:
        if not settings.use_kafka:
            return {"status": "disabled", "message": "Kafka is disabled in configuration"}
        
        from src.kafka.producer import get_producer
        
        # Get the Kafka producer
        producer = get_producer()
        
        if producer:
            # Try to send a test message
            test_message = {
                "event": {"test": True, "time": time.time()},
                "source_format": "test"
            }
            
            success = producer.send_event(test_message)
            
            if success:
                return {
                    "status": "healthy",
                    "bootstrap_servers": settings.kafka_bootstrap_servers,
                    "topic": settings.kafka_topic_input
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Failed to send test message to Kafka",
                    "bootstrap_servers": settings.kafka_bootstrap_servers
                }
        else:
            return {
                "status": "unhealthy",
                "message": "Kafka producer not available",
                "bootstrap_servers": settings.kafka_bootstrap_servers
            }
    
    except Exception as e:
        log.error(f"Failed to check Kafka health: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e),
            "bootstrap_servers": settings.kafka_bootstrap_servers
        }


@app.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """
    Get all detection rules.
    
    Args:
        enabled: Filter by enabled status
        tag: Filter by tag
        
    Returns:
        List of detection rules
    """
    rules = []
    
    for rule_id, rule in detection_engine.rules.items():
        if enabled is not None and rule.enabled != enabled:
            continue
        
        if tag is not None and tag not in rule.tags:
            continue
        
        rules.append(RuleResponse(**rule.to_dict()))
    
    return rules


@app.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(rule_id: str):
    """
    Get a detection rule by ID.
    
    Args:
        rule_id: ID of the rule to get
        
    Returns:
        Detection rule
    """
    if rule_id not in detection_engine.rules:
        raise HTTPException(status_code=404, detail=f"Rule not found: {rule_id}")
    
    rule = detection_engine.rules[rule_id]
    return RuleResponse(**rule.to_dict())


@app.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate):
    """
    Create a new detection rule.
    
    Args:
        rule: Rule to create
        
    Returns:
        Created rule
    """
    import uuid
    
    rule_id = f"RULE-{str(uuid.uuid4())[:8]}"
    
    detection_rule = DetectionRule(
        rule_id=rule_id,
        name=rule.name,
        description=rule.description,
        severity=rule.severity,
        query=rule.query,
        tags=rule.tags,
        mitre_techniques=rule.mitre_techniques,
        enabled=rule.enabled
    )
    
    detection_engine.load_rule(detection_rule)
    
    return RuleResponse(**detection_rule.to_dict())


@app.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str, rule: RuleCreate):
    """
    Update a detection rule.
    
    Args:
        rule_id: ID of the rule to update
        rule: Updated rule data
        
    Returns:
        Updated rule
    """
    if rule_id not in detection_engine.rules:
        raise HTTPException(status_code=404, detail=f"Rule not found: {rule_id}")
    
    detection_rule = DetectionRule(
        rule_id=rule_id,
        name=rule.name,
        description=rule.description,
        severity=rule.severity,
        query=rule.query,
        tags=rule.tags,
        mitre_techniques=rule.mitre_techniques,
        enabled=rule.enabled
    )
    
    detection_engine.rules[rule_id] = detection_rule
    
    return RuleResponse(**detection_rule.to_dict())


@app.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: str):
    """
    Delete a detection rule.
    
    Args:
        rule_id: ID of the rule to delete
    """
    if rule_id not in detection_engine.rules:
        raise HTTPException(status_code=404, detail=f"Rule not found: {rule_id}")
    
    del detection_engine.rules[rule_id]


@app.post("/rules/{rule_id}/run", response_model=List[AlertResponse])
async def run_rule(rule_id: str):
    """
    Run a detection rule.
    
    Args:
        rule_id: ID of the rule to run
        
    Returns:
        List of alerts generated by the rule
    """
    if rule_id not in detection_engine.rules:
        raise HTTPException(status_code=404, detail=f"Rule not found: {rule_id}")
    
    alerts = detection_engine.run_detection(rule_id)
    
    # Store alerts in the database
    for alert in alerts:
        detection_engine.store_alert(alert)
    
    return [AlertResponse(**alert.to_dict()) for alert in alerts]


@app.post("/run-detection", response_model=List[AlertResponse])
async def run_detection():
    """
    Run all enabled detection rules.
    
    Returns:
        List of alerts generated by all rules
    """
    alerts = detection_engine.run_detection()
    
    # Store alerts in the database
    for alert in alerts:
        detection_engine.store_alert(alert)
    
    return [AlertResponse(**alert.to_dict()) for alert in alerts]


@app.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate):
    """
    Create a new event.
    
    Args:
        event_data: Event data to create
        
    Returns:
        Created event
    """
    try:
        # Map to OCSF if not already in OCSF format
        if event_data.source_format != "ocsf":
            ocsf_event = ocsf_schema.map_to_ocsf(event_data.event, event_data.source_format)
        else:
            ocsf_event = event_data.event
        
        # Check if we should use Kafka
        if settings.use_kafka:
            from src.kafka.producer import get_producer
            
            # Get the Kafka producer
            producer = get_producer()
            
            if producer:
                # Send the event to Kafka
                kafka_message = {
                    "event": ocsf_event,
                    "source_format": "ocsf"  # Already mapped to OCSF
                }
                
                success = producer.send_event(kafka_message)
                
                if success:
                    # For Kafka mode, we generate a temporary ID since the actual DB ID will be created by the consumer
                    # In a production system, you might want to use a more robust ID generation strategy
                    import uuid
                    temp_id = str(uuid.uuid4())
                    
                    log.info(f"Event sent to Kafka with temporary ID: {temp_id}")
                    return EventResponse(id=temp_id, event=ocsf_event)
                else:
                    raise HTTPException(status_code=500, detail="Failed to send event to Kafka")
            else:
                log.warning("Kafka producer not available, falling back to direct database write")
        
        # If not using Kafka or Kafka producer not available, store directly in the database
        # Store in graph database
        query = """
        CREATE (e:Event {
            class_uid: $class_uid,
            category_uid: $category_uid,
            time: $time,
            severity: $severity,
            message: $message,
            metadata: $metadata
        })
        RETURN id(e) as id
        """
        
        params = {
            "class_uid": ocsf_event.get("class_uid", "unknown"),
            "category_uid": ocsf_event.get("category_uid", "unknown"),
            "time": ocsf_event.get("time", ""),
            "severity": ocsf_event.get("severity", 0),
            "message": ocsf_event.get("message", ""),
            "metadata": json.dumps(ocsf_event.get("metadata", {}))
        }
        
        result = db.execute_query(query, params)
        
        if result and len(result) > 0:
            event_id = str(result[0]["id"])
            
            # Process source entity if present
            if "src" in ocsf_event:
                src = ocsf_event["src"]
                src_type = src.get("type", "Unknown")
                src_query = f"""
                MERGE (s:{src_type} {{id: $src_id}})
                ON CREATE SET s += $src_props
                WITH s
                MATCH (e:Event) WHERE id(e) = toInteger($event_id)
                CREATE (s)-[:GENERATED]->(e)
                """
                
                src_params = {
                    "src_id": src.get("id", str(hash(json.dumps(src)))),
                    "src_props": {k: v for k, v in src.items() if k not in ["id", "type"]},
                    "event_id": event_id
                }
                
                db.execute_query(src_query, src_params)
            
            # Process destination entity if present
            if "dst" in ocsf_event:
                dst = ocsf_event["dst"]
                dst_type = dst.get("type", "Unknown")
                dst_query = f"""
                MERGE (d:{dst_type} {{id: $dst_id}})
                ON CREATE SET d += $dst_props
                WITH d
                MATCH (e:Event) WHERE id(e) = toInteger($event_id)
                CREATE (e)-[:TARGETS]->(d)
                """
                
                dst_params = {
                    "dst_id": dst.get("id", str(hash(json.dumps(dst)))),
                    "dst_props": {k: v for k, v in dst.items() if k not in ["id", "type"]},
                    "event_id": event_id
                }
                
                db.execute_query(dst_query, dst_params)
            
            return EventResponse(id=event_id, event=ocsf_event)
        else:
            raise HTTPException(status_code=500, detail="Failed to create event")
    
    except Exception as e:
        log.error(f"Failed to create event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """
    Get an event by ID.
    
    Args:
        event_id: ID of the event to get
        
    Returns:
        Event
    """
    try:
        query = """
        MATCH (e:Event) WHERE id(e) = toInteger($event_id)
        RETURN e
        """
        
        result = db.execute_query(query, {"event_id": event_id})
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
        
        event_node = result[0]["e"]
        
        # Convert metadata from JSON string to dict
        metadata = json.loads(event_node.get("metadata", "{}"))
        
        event = {
            "class_uid": event_node.get("class_uid", "unknown"),
            "category_uid": event_node.get("category_uid", "unknown"),
            "time": event_node.get("time", ""),
            "severity": event_node.get("severity", 0),
            "message": event_node.get("message", ""),
            "metadata": metadata
        }
        
        return EventResponse(id=event_id, event=event)
    
    except Exception as e:
        log.error(f"Failed to get event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    severity: Optional[int] = Query(None, ge=1, le=10, description="Filter by severity"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts to return")
):
    """
    Get alerts.
    
    Args:
        severity: Filter by severity
        rule_id: Filter by rule ID
        limit: Maximum number of alerts to return
        
    Returns:
        List of alerts
    """
    try:
        # Build query
        query = "MATCH (a:Alert)"
        where_clauses = []
        
        if severity is not None:
            where_clauses.append("a.severity = $severity")
        
        if rule_id is not None:
            where_clauses.append("a.rule_id = $rule_id")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " RETURN a ORDER BY a.timestamp DESC LIMIT $limit"
        
        # Build parameters
        params = {"limit": limit}
        
        if severity is not None:
            params["severity"] = severity
        
        if rule_id is not None:
            params["rule_id"] = rule_id
        
        # Execute query
        result = db.execute_query(query, params)
        
        # Convert to alerts
        alerts = []
        
        for record in result:
            alert_node = record["a"]
            
            # Get entities involved in the alert
            entities_query = """
            MATCH (a:Alert {alert_id: $alert_id})-[:INVOLVES]->(e)
            RETURN e, labels(e) as labels
            """
            
            entities_result = db.execute_query(entities_query, {"alert_id": alert_node["alert_id"]})
            entities = []
            
            for entity_record in entities_result:
                entity = entity_record["e"]
                entity_type = "Unknown"
                
                # Try to get the entity type from the labels result
                if "labels" in entity_record and entity_record["labels"]:
                    entity_type = entity_record["labels"][0]
                # Handle Neo4j node objects
                elif hasattr(entity, "labels") and entity.labels:
                    entity_type = list(entity.labels)[0]
                # Try to determine the entity type from the dictionary
                elif "type" in entity:
                    entity_type = entity["type"]
                elif "entity_type" in entity:
                    entity_type = entity["entity_type"]
                
                # Extract properties, excluding metadata fields
                if hasattr(entity, "items"):
                    properties = {k: v for k, v in entity.items() if k not in ["id", "type", "entity_type"]}
                else:
                    properties = {}
                
                entities.append({
                    "type": entity_type,
                    "id": entity.get("id", "unknown"),
                    "properties": properties
                })
            
            alert = AlertResponse(
                alert_id=alert_node["alert_id"],
                rule_id=alert_node["rule_id"],
                timestamp=alert_node["timestamp"],
                severity=alert_node["severity"],
                entities=entities,
                context={}
            )
            
            alerts.append(alert)
        
        return alerts
    
    except Exception as e:
        log.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph/query", response_model=Dict[str, Any])
async def execute_graph_query(request: GraphQueryRequest):
    """Execute a Neo4j query and return nodes and relationships."""
    try:
        # Execute the query
        result = db.execute_query(request.query)
        
        # Log the raw result for debugging
        log.info(f"Graph query result: {result}")
        
        # Transform the result into nodes and relationships
        nodes = []
        relationships = []
        
        for record in result:
            log.info(f"Processing record: {record}")
            for key, value in record.items():
                log.info(f"Processing key: {key}, value type: {type(value)}")
                
                # Handle Neo4j Node objects
                if hasattr(value, 'labels') and hasattr(value, 'items'):
                    nodes.append({
                        "id": str(value.id),
                        "labels": list(value.labels),
                        "properties": dict(value)
                    })
                # Handle Neo4j Relationship objects
                elif hasattr(value, 'type') and hasattr(value, 'start_node') and hasattr(value, 'end_node'):
                    relationships.append({
                        "id": str(value.id),
                        "type": value.type,
                        "start": str(value.start_node.id),
                        "end": str(value.end_node.id),
                        "properties": dict(value)
                    })
                # Handle dictionary values that might be nodes or relationships
                elif isinstance(value, dict):
                    if 'labels' in value:
                        nodes.append({
                            "id": str(value.get('id', '')),
                            "labels": value.get('labels', []),
                            "properties": {k: v for k, v in value.items() if k not in ['id', 'labels']}
                        })
                    elif 'type' in value and 'start' in value and 'end' in value:
                        relationships.append({
                            "id": str(value.get('id', '')),
                            "type": value['type'],
                            "start": str(value['start']),
                            "end": str(value['end']),
                            "properties": {k: v for k, v in value.items() if k not in ['id', 'type', 'start', 'end']}
                        })
        
        return {
            "nodes": nodes,
            "relationships": relationships
        }
    except Exception as e:
        log.error(f"Failed to execute graph query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Load detection rules on startup
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    log.info("Starting Blueprint Graph API")
    
    # Load detection rules
    rules_file = os.path.join("config", "detection_rules.json")
    if os.path.exists(rules_file):
        detection_engine.load_rules_from_file(rules_file)
    else:
        log.warning(f"Detection rules file not found: {rules_file}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    ) 