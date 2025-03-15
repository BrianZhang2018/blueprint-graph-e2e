# Blueprint Graph - OCSF Detection Engine

A graph-based detection engine for cybersecurity events that maps to the Open Cybersecurity Schema Framework (OCSF).

## Overview

Blueprint Graph is a detection engine built on Neo4j graph database that ingests, processes, and analyzes security events according to the OCSF schema. It provides:

- Real-time security event ingestion and processing
- Graph-based detection rules for complex attack patterns
- OCSF schema mapping and compliance
- API for integration with security platforms
- Visualization of security events and their relationships

## Architecture

The system consists of several components:

- **Graph Database**: Neo4j for storing and querying security events and their relationships
- **Pipelines**: Data ingestion and processing pipelines using Apache Beam
- **API**: FastAPI-based REST API for interacting with the system
- **OCSF Mapping**: Utilities for mapping security events to OCSF schema
- **Detection Engine**: Core detection logic for identifying security threats

## Setup

### Prerequisites

- Python 3.9+
- Neo4j 5.x
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/blueprintgraph.git
   cd blueprintgraph
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start Neo4j (if not using Docker):
   ```
   # Follow Neo4j installation instructions for your platform
   ```

### Running with Docker

```
docker-compose up -d
```

## Usage

### Starting the API

```
python -m src.api.main
```

### Running the Pipelines

```
python -m src.pipelines.ingest --config config/pipeline.yaml
```

### Testing

#### Running Unit Tests

```
pytest tests/unit
```

#### Running Integration Tests

Integration tests verify that all components work together correctly. They require Docker to be running.

```
./run_integration_tests.sh
```

Or manually:

```
python -m pytest tests/integration -v
```

#### Manual Testing

For manual testing and verification, you can use the provided test scripts:

1. Generate test data:

   ```
   ./tests/generate_test_data.py --count 10 --format ocsf --api http://localhost:8000
   ```

   Options:

   - `--count`: Number of events to generate (default: 10)
   - `--format`: Event format (ocsf, syslog, cef, leef, all)
   - `--output`: Save events to a file
   - `--api`: Send events to the API

2. Run a complete test scenario:

   ```
   ./tests/run_manual_test.sh
   ```

   This script:

   - Verifies the API is running
   - Generates and sends test events
   - Creates a detection rule
   - Runs detection
   - Verifies alerts are generated
   - Cleans up test data

#### End-to-End (E2E) Testing

The project includes an automated end-to-end testing framework that uses pytest fixtures to set up and tear down all required services. The E2E tests run in an isolated environment with dedicated ports to avoid conflicts with local development services.

Key features:

- **Port Conflict Resolution**: Uses different ports for test services to avoid conflicts with local development
- **Isolation**: Each test runs in an isolated environment with a dedicated Docker Compose project
- **Automation**: No manual setup required - the fixtures handle everything
- **Cleanup**: All resources are automatically cleaned up after tests complete

To run the E2E tests:

```bash
# Run all E2E tests
pytest tests/integration/e2e/

# Run a specific E2E test
pytest tests/integration/e2e/test_kafka_e2e.py
```

For more details, see the [E2E Testing README](tests/integration/e2e/README.md).

## Development

### Project Structure

- `src/`: Source code
  - `api/`: FastAPI application
  - `core/`: Core detection engine logic
  - `pipelines/`: Data ingestion and processing pipelines
  - `schemas/`: OCSF schema definitions and mapping
  - `utils/`: Utility functions
- `config/`: Configuration files
- `docs/`: Documentation
- `tests/`: Test cases
  - `unit/`: Unit tests
  - `integration/`: Integration tests

## License

MIT

## Event Ingestion

Blueprint Graph supports two modes for event ingestion:

1. **Direct Database Write**: Events are written directly to the Neo4j database (default mode)
2. **Kafka-based Processing**: Events are sent to Kafka and then processed asynchronously by a consumer

To enable Kafka-based processing, set `USE_KAFKA=true` in your `.env` file or environment.

For more details on the Kafka integration, see [Kafka Integration](docs/kafka_integration.md).
