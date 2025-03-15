# Kafka Integration for Blueprint Graph

This document explains how to use the Kafka integration for event processing in Blueprint Graph.

## Overview

Blueprint Graph now supports two modes for event ingestion:

1. **Direct Database Write**: Events are written directly to the Neo4j database (default mode)
2. **Kafka-based Processing**: Events are sent to Kafka and then processed asynchronously by a consumer

The Kafka-based approach provides several benefits:

- Decoupling of event ingestion from processing
- Better handling of high-volume event streams
- Improved resilience to database outages
- Ability to replay events if needed

## Configuration

### Environment Variables

To configure Kafka integration, set the following environment variables:

```
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_INPUT=security-events
KAFKA_CONSUMER_GROUP=blueprintgraph-consumer
USE_KAFKA=true  # Set to false to use direct database write
```

These can be set in your `.env` file or directly in the environment.

### Docker Compose

The `docker-compose.yml` file includes all necessary services:

- `zookeeper`: Zookeeper service for Kafka
- `kafka`: Kafka broker
- `kafka-ui`: Web UI for Kafka management (optional)
- `api`: FastAPI service that can send events to Kafka
- `kafka-consumer`: Service that consumes events from Kafka and writes to Neo4j

## Usage

### Starting the Services

To start all services:

```bash
docker-compose up -d
```

To start without the Kafka consumer (direct database write mode):

```bash
USE_KAFKA=false docker-compose up -d api neo4j
```

### Sending Events

Events are sent to the same API endpoint regardless of the mode:

```bash
curl -X POST http://localhost:8001/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "class_uid": "1001",
      "category_uid": "1",
      "time": "2024-03-14T10:00:00Z",
      "severity": 5,
      "message": "Failed login attempt",
      "src": {
        "type": "User",
        "id": "user123",
        "name": "john.doe"
      }
    },
    "source_format": "ocsf"
  }'
```

### Checking Kafka Health

You can check the health of the Kafka integration:

```bash
curl http://localhost:8001/health/kafka
```

Example response when Kafka is healthy:

```json
{
  "status": "healthy",
  "bootstrap_servers": "kafka:9092",
  "topic": "security-events"
}
```

### Kafka UI

A web-based Kafka UI is available at http://localhost:8080. You can use it to:

- View topics and messages
- Monitor consumer groups
- Check broker status

## Architecture

### Event Flow

1. **API Endpoint**: The `/events` endpoint receives event data
2. **Kafka Producer**: If `USE_KAFKA=true`, events are sent to Kafka
3. **Kafka Consumer**: Consumes events from Kafka and processes them
4. **Neo4j Database**: Events are stored in the graph database

### Components

- **KafkaProducer**: Handles sending events to Kafka
- **KafkaConsumer**: Processes events from Kafka and stores them in Neo4j

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**:

   - Check that Kafka and Zookeeper are running
   - Verify the `KAFKA_BOOTSTRAP_SERVERS` setting
   - Check network connectivity between services

2. **Consumer Not Processing Events**:

   - Check the consumer logs: `docker-compose logs kafka-consumer`
   - Verify the consumer is subscribed to the correct topic
   - Check for errors in the consumer logs

3. **Events Not Appearing in Neo4j**:
   - Check that the consumer is running and processing events
   - Verify Neo4j connection settings
   - Check for database errors in the consumer logs

### Viewing Logs

```bash
# View API logs
docker-compose logs api

# View Kafka consumer logs
docker-compose logs kafka-consumer

# View Kafka broker logs
docker-compose logs kafka
```
