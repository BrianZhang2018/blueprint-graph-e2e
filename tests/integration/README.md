# Integration Tests for Blueprint Graph

This directory contains integration tests for the Blueprint Graph OCSF Detection Engine. These tests verify that the different components of the system work together correctly.

## Test Structure

The integration tests are organized into the following files:

- `conftest.py`: Contains pytest fixtures for setting up the test environment, including a Neo4j database container.
- `test_api_integration.py`: Tests for the API endpoints.
- `test_pipeline_integration.py`: Tests for the data ingestion pipeline.
- `test_detection_engine_integration.py`: Tests for the detection engine.
- `test_ocsf_schema_integration.py`: Tests for the OCSF schema handling.
- `e2e/`: End-to-end tests that verify complete application flows:
  - `e2e/test_kafka_e2e.py`: Tests the Kafka integration flow.
  - `e2e/conftest.py`: Fixtures for automatically setting up and tearing down services for E2E tests.

## Running the Tests

You can run the integration tests using the provided script:

```bash
./run_integration_tests.sh
```

This script will:

1. Create a virtual environment if it doesn't exist
2. Install the required dependencies
3. Run the integration tests
4. Generate a coverage report

Alternatively, you can run the tests manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov docker

# Run all integration tests
python -m pytest tests/integration -v

# Run only E2E tests (with automatic service setup)
python -m pytest tests/integration/e2e -v

# Run with coverage
python -m pytest tests/integration --cov=src -v
```

## Test Requirements

The integration tests require:

- Docker: For running containers (Neo4j, Kafka, etc.)
- Docker Python SDK: For programmatically managing Docker containers
- pytest: For running the tests
- pytest-cov: For generating coverage reports

## Test Scenarios

The integration tests cover the following scenarios:

### API Integration Tests

- Health check endpoint
- Creating, retrieving, updating, and deleting detection rules
- Listing rules with filters
- Creating and retrieving events
- Running detection rules
- Retrieving alerts

### Pipeline Integration Tests

- Parsing events from different formats
- Detecting source formats
- Mapping events to OCSF format
- Storing events in the graph database
- End-to-end pipeline processing

### Detection Engine Integration Tests

- Loading detection rules
- Running detection rules
- Storing alerts in the database

### OCSF Schema Integration Tests

- Loading OCSF schemas
- Validating events against schemas
- Mapping events to OCSF format

### End-to-End (E2E) Integration Tests

- Verifying complete application flows from end to end
- Testing the Kafka event processing flow
- Sending events to the API
- API producing messages to Kafka
- Kafka consumer processing the messages
- Events being stored in Neo4j with proper relationships

The E2E tests use pytest fixtures to automatically set up and tear down the required services, ensuring tests run in a clean, isolated environment.

For more details on the E2E integration tests, see the [E2E integration tests README](e2e/README.md).

# Integration Tests

This directory contains integration tests for the Blueprint Graph project. Integration tests verify that different components of the system work together correctly.

## Test Categories

The integration tests are organized into the following categories:

### End-to-End (E2E) Tests

Located in the `e2e/` directory, these tests verify complete flows through the system, from data ingestion to storage and retrieval. They use automated pytest fixtures to set up and tear down all required services.

Key features of the E2E testing approach:

- **Automated Environment**: Tests automatically set up all required services using Docker
- **Port Conflict Resolution**: Uses different ports for test services to avoid conflicts with local development
- **Isolation**: Each test runs in an isolated environment with a dedicated Docker Compose project
- **Cleanup**: All resources are automatically cleaned up after tests complete

See the [E2E Testing README](./e2e/README.md) for more details.

### API Tests

Located in the `api/` directory, these tests verify the API endpoints and their integration with the database.

### Database Tests

Located in the `db/` directory, these tests verify the database operations and schema.

## Running the Tests

You can run all integration tests or specific categories:

```bash
# Run all integration tests
pytest tests/integration/

# Run only E2E tests
pytest tests/integration/e2e/

# Run only API tests
pytest tests/integration/api/

# Run only database tests
pytest tests/integration/db/
```

## Test Dependencies

The integration tests require the following dependencies:

- pytest
- requests
- docker (Python SDK)
- confluent-kafka
- py2neo

These dependencies are included in the project's `requirements.txt` file.

## CI/CD Integration

The integration tests are designed to run in CI/CD pipelines. The E2E tests in particular use Docker-in-Docker to create isolated test environments that don't conflict with other services.
