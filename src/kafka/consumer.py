"""
Kafka consumer module for Blueprint Graph.

This module provides a Kafka consumer for processing events from Kafka topics.
"""
import json
import time
import signal
import sys
from typing import Dict, Any, Optional, List, Callable
from confluent_kafka import Consumer, KafkaError
from src.utils import settings, log, db
from src.schemas import ocsf_schema


class KafkaConsumer:
    """Kafka consumer for processing events from Kafka topics."""
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        auto_offset_reset: str = "latest"
    ):
        """
        Initialize the Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Topic to consume events from
            group_id: Consumer group ID
            auto_offset_reset: Auto offset reset strategy ('earliest' or 'latest')
        """
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.topic = topic or settings.kafka_topic_input
        self.group_id = group_id or settings.kafka_consumer_group
        self.auto_offset_reset = auto_offset_reset
        self.running = False
        
        if not self.bootstrap_servers:
            raise ValueError("Kafka bootstrap servers not configured")
        
        if not self.topic:
            raise ValueError("Kafka topic not configured")
        
        if not self.group_id:
            raise ValueError("Kafka consumer group ID not configured")
        
        self.consumer = Consumer({
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': self.auto_offset_reset,
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 5000
        })
        
        log.info(f"Initialized Kafka consumer with bootstrap servers: {self.bootstrap_servers}")
        log.info(f"Consuming from topic: {self.topic}")
        log.info(f"Consumer group ID: {self.group_id}")
    
    def start(self, process_func: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Start consuming events from Kafka.
        
        Args:
            process_func: Function to process events (defaults to self.process_event)
        """
        self.running = True
        
        # Subscribe to the topic
        self.consumer.subscribe([self.topic])
        
        log.info(f"Started consuming from topic: {self.topic}")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Process events
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        log.debug(f"Reached end of partition {msg.partition()}")
                    else:
                        log.error(f"Kafka error: {msg.error()}")
                else:
                    try:
                        # Parse the message value
                        value = msg.value().decode('utf-8')
                        event = json.loads(value)
                        
                        # Process the event
                        if process_func:
                            process_func(event)
                        else:
                            self.process_event(event)
                            
                    except Exception as e:
                        log.error(f"Failed to process message: {str(e)}")
        
        except Exception as e:
            log.error(f"Error in Kafka consumer: {str(e)}")
        
        finally:
            self.close()
    
    def process_event(self, event: Dict[str, Any]):
        """
        Process an event from Kafka.
        
        Args:
            event: Event data to process
        """
        try:
            log.debug(f"Processing event: {event}")
            
            # Extract event data and source format
            event_data = event.get('event', {})
            source_format = event.get('source_format', 'unknown')
            
            # Map to OCSF if not already in OCSF format
            if source_format != "ocsf":
                ocsf_event = ocsf_schema.map_to_ocsf(event_data, source_format)
            else:
                ocsf_event = event_data
            
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
                
                log.info(f"Successfully processed event with ID: {event_id}")
            else:
                log.error("Failed to create event in database")
        
        except Exception as e:
            log.error(f"Failed to process event: {str(e)}")
    
    def _signal_handler(self, sig, frame):
        """
        Signal handler for graceful shutdown.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        log.info(f"Received signal {sig}, shutting down...")
        self.running = False
    
    def close(self):
        """Close the Kafka consumer."""
        if hasattr(self, 'consumer'):
            self.consumer.close()
            log.info("Kafka consumer closed")


def main():
    """Main entry point for the Kafka consumer."""
    try:
        log.info("Starting Kafka consumer...")
        consumer = KafkaConsumer()
        consumer.start()
    except Exception as e:
        log.error(f"Failed to start Kafka consumer: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 