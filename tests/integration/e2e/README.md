# End-to-End (E2E) Testing

This directory contains end-to-end tests for the Blueprint Graph project. These tests verify the complete flow of data through the system, from ingestion to storage and retrieval.

## Automated Testing with Pytest Fixtures

The E2E tests use pytest fixtures to automatically set up and tear down the required services. This approach provides several benefits:

1. **Isolation**: Tests run in an isolated environment with dedicated ports to avoid conflicts with local development services
2. **Automation**: No manual setup required - the fixtures handle everything
3. **Reliability**: Tests are consistent and repeatable
4. **Cleanup**: All resources are automatically cleaned up after tests complete

## Complete Isolation from Local Development

The E2E tests are designed to run alongside local development services without conflicts. This is achieved through:

1. **Different Ports**: Test services use different ports than development services
2. **Different Container Names**: Test containers use a prefix (`e2e_test_`) to avoid name conflicts
3. **Separate Docker Compose Project**: Tests use a different project name (`blueprintgraph_test`)

This means you can run the E2E tests while your local development services are running, and they won't interfere with each other.

## Port Conflict Resolution

To avoid conflicts between test services and any locally running development services, the test environment uses different ports:

| Service    | Development Port | Test Port |
| ---------- | ---------------- | --------- |
| API        | 8001             | 18001     |
| Kafka      | 9092             | 19092     |
| Neo4j HTTP | 7475             | 17475     |
| Neo4j Bolt | 7688             | 17688     |
| Kafka UI   | 8080             | 18080     |

This is implemented using:

1. A dynamic Docker Compose override file created at test time
2. A separate Docker Compose project name (`blueprintgraph_test`)

## Implementation Details

The port conflict resolution is implemented in `conftest.py` with the following key components:

1. **Port Constants**: Defines separate ports for testing
2. **Container Name Prefixes**: Uses a prefix (`e2e_test_`) for test container names
3. **Docker Compose Override**: Creates a temporary YAML file with port mappings and container names
4. **Project Isolation**: Uses a separate Docker Compose project name
5. **Service Management**: Starts and stops services with the override file
6. **Health Checking**: Verifies services are ready before tests run

## Running the Tests

You can run the E2E tests using pytest:

```bash
# Run all E2E tests
pytest tests/integration/e2e/

# Run a specific E2E test
pytest tests/integration/e2e/test_kafka_e2e.py
```

## Available Tests

- `test_kafka_e2e.py`: Tests the API health and Neo4j connection

## Test Structure

Each E2E test follows this general structure:

1. **Setup**: The `e2e_services` fixture starts all required services with test-specific ports
2. **Test Execution**: The test performs actions like checking service health
3. **Verification**: The test verifies that services are working correctly
4. **Cleanup**: The fixture automatically stops and removes all services

## Adding New E2E Tests

To add a new E2E test:

1. Create a new test file in this directory
2. Use the `e2e_services` fixture to set up the required services
3. Import port constants from `conftest.py` to ensure you're using the test-specific ports
4. Follow the pattern in existing tests for producing data and verifying results

## Troubleshooting

If you encounter issues with the E2E tests:

1. **Port Conflicts**: Ensure no other services are using the test ports (18001, 19092, 17475, 17688, 18080)
2. **Service Health**: Check the logs for any service startup issues
3. **Test Timeouts**: Increase the timeout values in the health check functions if services take longer to start

For more detailed logs, run pytest with the `-v` (verbose) flag.
