# Testing the Kafka Integration

This document provides step-by-step instructions for testing the Kafka integration in Blueprint Graph.

## Prerequisites

Ensure you have the following installed:

- Docker and Docker Compose
- curl or another HTTP client

## Step 1: Start the Services

First, start all the required services using Docker Compose:

```bash
docker-compose up -d
```

This will start:

- Neo4j database
- Zookeeper
- Kafka broker
- Kafka UI
- FastAPI backend
- Kafka consumer

## Step 2: Verify Services are Running

Check that all services are running:

```bash
docker-compose ps
```

All services should show as "Up" in the status column.

## Step 3: Check Kafka Health

Verify that the Kafka integration is healthy:

```bash
curl http://localhost:8001/health/kafka
```

You should see a response like:

```json
{
  "status": "healthy",
  "bootstrap_servers": "kafka:9092",
  "topic": "security-events"
}
```

## Step 4: Send a Test Event

Send a test event to the API:

```bash
curl -X POST http://localhost:8001/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "class_uid": "1001",
      "category_uid": "1",
      "time": "2024-03-14T10:00:00Z",
      "severity": 5,
      "message": "Test event via Kafka",
      "src": {
        "type": "User",
        "id": "user123",
        "name": "john.doe"
      }
    },
    "source_format": "ocsf"
  }'
```

You should receive a response with a temporary ID:

```json
{
  "id": "some-uuid",
  "event": {
    "class_uid": "1001",
    "category_uid": "1",
    "time": "2024-03-14T10:00:00Z",
    "severity": 5,
    "message": "Test event via Kafka",
    "src": {
      "type": "User",
      "id": "user123",
      "name": "john.doe"
    }
  }
}
```

## Step 5: Check Kafka UI

Open the Kafka UI in your browser:

```
http://localhost:8080
```

Navigate to the "Topics" section and click on the "security-events" topic. You should see the message you just sent.

## Step 6: Verify Event in Neo4j

Check that the event was processed and stored in Neo4j:

```bash
curl http://localhost:8001/events
```

This should return a list of events, including the one you just sent.

You can also check directly in Neo4j by opening the Neo4j browser:

```
http://localhost:7474
```

Log in with username `neo4j` and password `blueprintgraph`, then run the following Cypher query:

```cypher
MATCH (e:Event {message: "Test event via Kafka"})
RETURN e
```

## Step 7: Test Direct Database Write

To test the direct database write mode:

1. Stop the current services:

```bash
docker-compose down
```

2. Start the services with Kafka disabled:

```bash
USE_KAFKA=false docker-compose up -d api neo4j
```

3. Send a test event:

```bash
curl -X POST http://localhost:8001/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "class_uid": "1001",
      "category_uid": "1",
      "time": "2024-03-14T10:00:00Z",
      "severity": 5,
      "message": "Test event direct write",
      "src": {
        "type": "User",
        "id": "user123",
        "name": "john.doe"
      }
    },
    "source_format": "ocsf"
  }'
```

4. Verify the event in Neo4j:

```bash
curl http://localhost:8001/events
```

## Troubleshooting

### Kafka Consumer Not Processing Events

Check the Kafka consumer logs:

```bash
docker-compose logs kafka-consumer
```

Look for any error messages or exceptions.

### Events Not Appearing in Neo4j

1. Check that the Kafka consumer is running:

```bash
docker-compose ps kafka-consumer
```

2. Check the Kafka consumer logs for errors:

```bash
docker-compose logs kafka-consumer
```

3. Verify that the event was sent to Kafka using the Kafka UI.

### Kafka Health Check Failing

If the Kafka health check is failing:

1. Check that Kafka and Zookeeper are running:

```bash
docker-compose ps kafka zookeeper
```

2. Check the Kafka logs:

```bash
docker-compose logs kafka
```

3. Verify the `KAFKA_BOOTSTRAP_SERVERS` setting in your `.env` file.
