"""
Kafka producer module for Blueprint Graph.

This module provides a Kafka producer for sending events to Kafka topics.
"""
import json
from typing import Dict, Any, Optional
from confluent_kafka import Producer
from src.utils import settings, log


class KafkaProducer:
    """Kafka producer for sending events to Kafka topics."""
    
    def __init__(self, bootstrap_servers: Optional[str] = None, topic: Optional[str] = None):
        """
        Initialize the Kafka producer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Default topic to send events to
        """
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.topic = topic or settings.kafka_topic_input
        
        if not self.bootstrap_servers:
            raise ValueError("Kafka bootstrap servers not configured")
        
        self.producer = Producer({
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'blueprintgraph-producer',
            'acks': 'all'
        })
        
        log.info(f"Initialized Kafka producer with bootstrap servers: {self.bootstrap_servers}")
    
    def send_event(self, event: Dict[str, Any], topic: Optional[str] = None) -> bool:
        """
        Send an event to a Kafka topic.
        
        Args:
            event: Event data to send
            topic: Topic to send the event to (defaults to self.topic)
            
        Returns:
            bool: True if the event was sent successfully, False otherwise
        """
        try:
            # Convert event to JSON string
            event_json = json.dumps(event)
            
            # Use the provided topic or the default topic
            target_topic = topic or self.topic
            
            if not target_topic:
                raise ValueError("No topic specified for sending event")
            
            # Send the event to Kafka
            self.producer.produce(
                topic=target_topic,
                value=event_json.encode('utf-8'),
                callback=self._delivery_callback
            )
            
            # Flush to ensure the message is sent
            self.producer.flush(timeout=10)
            
            log.debug(f"Sent event to Kafka topic {target_topic}")
            return True
            
        except Exception as e:
            log.error(f"Failed to send event to Kafka: {str(e)}")
            return False
    
    def _delivery_callback(self, err, msg):
        """
        Callback function for message delivery reports.
        
        Args:
            err: Error (if any)
            msg: Message that was delivered
        """
        if err:
            log.error(f"Message delivery failed: {str(err)}")
        else:
            log.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def close(self):
        """Close the Kafka producer."""
        if hasattr(self, 'producer'):
            self.producer.flush()
            log.info("Kafka producer closed")


# Create a global producer instance
producer = None

def get_producer() -> KafkaProducer:
    """
    Get the global Kafka producer instance.
    
    Returns:
        KafkaProducer: The global Kafka producer instance
    """
    global producer
    
    if producer is None and settings.use_kafka and settings.kafka_bootstrap_servers:
        try:
            producer = KafkaProducer()
        except Exception as e:
            log.error(f"Failed to initialize Kafka producer: {str(e)}")
    
    return producer 