"""
Data ingestion pipeline module.

This module provides a pipeline for ingesting security events from various sources,
mapping them to OCSF, and storing them in the Neo4j graph database.
"""
import os
import json
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.kafka import ReadFromKafka
from confluent_kafka import Consumer, KafkaError
from typing import Dict, Any, List, Optional
from src.utils import settings, log, db
from src.schemas import ocsf_schema


class ParseEvent(beam.DoFn):
    """Parse raw event data into a structured format."""
    
    def process(self, element):
        """
        Process a raw event.
        
        Args:
            element: Raw event data
            
        Yields:
            dict: Parsed event
        """
        try:
            # Parse the raw event data
            if isinstance(element, bytes):
                element = element.decode('utf-8')
            
            if isinstance(element, str):
                event = json.loads(element)
            else:
                event = element
            
            log.debug(f"Parsed event: {event}")
            yield event
        except Exception as e:
            log.error(f"Failed to parse event: {str(e)}")


class DetectSourceFormat(beam.DoFn):
    """Detect the source format of an event."""
    
    def process(self, element):
        """
        Detect the source format of an event.
        
        Args:
            element: Parsed event
            
        Yields:
            tuple: (event, source_format)
        """
        try:
            # Detect the source format based on event structure
            source_format = "unknown"
            
            # Check if already in OCSF format (check first to avoid misclassification)
            if isinstance(element, dict) and 'class_uid' in element and 'category_uid' in element:
                source_format = "ocsf"
            
            # Check for CEF format
            elif isinstance(element, dict) and any(k in element for k in ['deviceVendor', 'deviceProduct', 'deviceVersion']):
                source_format = "cef"
            
            # Check for LEEF format
            elif isinstance(element, dict) and any(k in element for k in ['devname', 'devtime', 'devtype']):
                source_format = "leef"
            
            # Check for syslog format
            elif isinstance(element, dict) and any(k in element for k in ['facility', 'severity', 'timestamp', 'hostname']):
                source_format = "syslog"
            
            log.debug(f"Detected source format: {source_format}")
            yield (element, source_format)
        except Exception as e:
            log.error(f"Failed to detect source format: {str(e)}")


class MapToOCSF(beam.DoFn):
    """Map events to OCSF schema."""
    
    def process(self, element):
        """
        Map an event to OCSF schema.
        
        Args:
            element: Tuple of (event, source_format)
            
        Yields:
            dict: OCSF-formatted event
        """
        try:
            event, source_format = element
            
            # If already in OCSF format, pass through
            if source_format == "ocsf":
                yield event
                return
            
            # Map to OCSF using the schema mapper
            ocsf_event = ocsf_schema.map_to_ocsf(event, source_format)
            
            log.debug(f"Mapped event to OCSF: {ocsf_event}")
            yield ocsf_event
        except Exception as e:
            log.error(f"Failed to map event to OCSF: {str(e)}")


class StoreInGraph(beam.DoFn):
    """Store events in the Neo4j graph database."""
    
    def process(self, element):
        """
        Store an event in the graph database.
        
        Args:
            element: OCSF-formatted event
            
        Yields:
            dict: Stored event with database ID
        """
        try:
            # Extract event class and category
            class_uid = element.get('class_uid')
            category_uid = element.get('category_uid')
            
            # Create a node for the event
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
                "class_uid": class_uid,
                "category_uid": category_uid,
                "time": element.get('time'),
                "severity": element.get('severity', 0),
                "message": element.get('message', ''),
                "metadata": json.dumps(element.get('metadata', {}))
            }
            
            result = db.execute_query(query, params)
            
            if result and len(result) > 0:
                event_id = result[0]['id']
                element['_id'] = event_id
                log.info(f"Stored event in graph database with ID: {event_id}")
                
                # Process additional entities based on event class
                self._process_entities(element, event_id)
                
                yield element
            else:
                log.error("Failed to store event in graph database")
        except Exception as e:
            log.error(f"Failed to store event in graph database: {str(e)}")
    
    def _process_entities(self, event, event_id):
        """
        Process additional entities from the event.
        
        Args:
            event: OCSF-formatted event
            event_id: Database ID of the event node
        """
        try:
            # Extract and create nodes for entities based on event class
            # This is a simplified example - in a real implementation, this would be more complex
            
            # Process source entity if present
            if 'src' in event:
                src = event['src']
                src_type = src.get('type', 'Unknown')
                src_query = f"""
                MERGE (s:{src_type} {{id: $src_id}})
                ON CREATE SET s += $src_props
                WITH s
                MATCH (e:Event) WHERE id(e) = $event_id
                CREATE (s)-[:GENERATED]->(e)
                """
                
                src_params = {
                    "src_id": src.get('id', str(hash(json.dumps(src)))),
                    "src_props": {k: v for k, v in src.items() if k not in ['id', 'type']},
                    "event_id": event_id
                }
                
                db.execute_query(src_query, src_params)
            
            # Process destination entity if present
            if 'dst' in event:
                dst = event['dst']
                dst_type = dst.get('type', 'Unknown')
                dst_query = f"""
                MERGE (d:{dst_type} {{id: $dst_id}})
                ON CREATE SET d += $dst_props
                WITH d
                MATCH (e:Event) WHERE id(e) = $event_id
                CREATE (e)-[:TARGETS]->(d)
                """
                
                dst_params = {
                    "dst_id": dst.get('id', str(hash(json.dumps(dst)))),
                    "dst_props": {k: v for k, v in dst.items() if k not in ['id', 'type']},
                    "event_id": event_id
                }
                
                db.execute_query(dst_query, dst_params)
            
            # Process principal (user) entity if present
            if 'principal' in event:
                principal = event['principal']
                principal_type = principal.get('type', 'User')
                principal_query = f"""
                MERGE (p:{principal_type} {{id: $principal_id}})
                ON CREATE SET p += $principal_props
                WITH p
                MATCH (e:Event) WHERE id(e) = $event_id
                CREATE (p)-[:PERFORMED]->(e)
                """
                
                principal_params = {
                    "principal_id": principal.get('id', str(hash(json.dumps(principal)))),
                    "principal_props": {k: v for k, v in principal.items() if k not in ['id', 'type']},
                    "event_id": event_id
                }
                
                db.execute_query(principal_query, principal_params)
        
        except Exception as e:
            log.error(f"Failed to process entities for event {event_id}: {str(e)}")


def run_pipeline(config_file=None):
    """
    Run the data ingestion pipeline.
    
    Args:
        config_file (str, optional): Path to the pipeline configuration file
    """
    # Load configuration
    config = {}
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    
    # Set up pipeline options
    pipeline_options = PipelineOptions([
        '--runner=DirectRunner',
        '--direct_running_mode=multi_processing',
        '--direct_num_workers=4'
    ])
    
    # Get Kafka configuration
    kafka_bootstrap_servers = config.get('kafka_bootstrap_servers', settings.kafka_bootstrap_servers)
    kafka_topic = config.get('kafka_topic', settings.kafka_topic_input)
    
    if not kafka_bootstrap_servers or not kafka_topic:
        log.error("Kafka configuration is missing")
        return
    
    # Create and run the pipeline
    with beam.Pipeline(options=pipeline_options) as pipeline:
        # Read from Kafka
        events = (
            pipeline
            | "Read from Kafka" >> ReadFromKafka(
                consumer_config={
                    'bootstrap.servers': kafka_bootstrap_servers,
                    'group.id': settings.kafka_consumer_group,
                    'auto.offset.reset': 'latest'
                },
                topics=[kafka_topic]
            )
            | "Parse Events" >> beam.ParDo(ParseEvent())
            | "Detect Source Format" >> beam.ParDo(DetectSourceFormat())
            | "Map to OCSF" >> beam.ParDo(MapToOCSF())
            | "Store in Graph" >> beam.ParDo(StoreInGraph())
        )
    
    log.info("Pipeline completed")


def run_standalone():
    """Run the pipeline in standalone mode using the Kafka Consumer directly."""
    # Get Kafka configuration
    kafka_bootstrap_servers = settings.kafka_bootstrap_servers
    kafka_topic = settings.kafka_topic_input
    
    if not kafka_bootstrap_servers or not kafka_topic:
        log.error("Kafka configuration is missing")
        return
    
    # Create Kafka consumer
    consumer = Consumer({
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': settings.kafka_consumer_group,
        'auto.offset.reset': 'latest'
    })
    
    # Subscribe to topic
    consumer.subscribe([kafka_topic])
    
    # Create pipeline steps
    parse_event = ParseEvent()
    detect_source_format = DetectSourceFormat()
    map_to_ocsf = MapToOCSF()
    store_in_graph = StoreInGraph()
    
    try:
        log.info(f"Starting standalone pipeline, consuming from {kafka_topic}")
        
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    log.debug(f"Reached end of partition {msg.partition()}")
                else:
                    log.error(f"Kafka error: {msg.error()}")
            else:
                # Process the message
                for parsed_event in parse_event.process(msg.value()):
                    for event_with_format in detect_source_format.process(parsed_event):
                        for ocsf_event in map_to_ocsf.process(event_with_format):
                            for stored_event in store_in_graph.process(ocsf_event):
                                log.info(f"Successfully processed event: {stored_event.get('_id')}")
    
    except KeyboardInterrupt:
        log.info("Stopping pipeline")
    finally:
        consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCSF Data Ingestion Pipeline")
    parser.add_argument("--config", help="Path to pipeline configuration file")
    parser.add_argument("--standalone", action="store_true", help="Run in standalone mode")
    args = parser.parse_args()
    
    if args.standalone:
        run_standalone()
    else:
        run_pipeline(args.config) 