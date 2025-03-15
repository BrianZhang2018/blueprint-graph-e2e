"""
Kafka integration module for Blueprint Graph.

This module provides Kafka producer and consumer functionality for event processing.
"""

from src.kafka.producer import KafkaProducer
from src.kafka.consumer import KafkaConsumer

__all__ = ["KafkaProducer", "KafkaConsumer"] 