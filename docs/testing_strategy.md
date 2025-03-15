# Blueprint Graph Testing Strategy

This document outlines the testing strategy for the Blueprint Graph OCSF Detection Engine project.

## Testing Levels

### Unit Testing

Unit tests focus on testing individual components in isolation. They are fast, reliable, and provide immediate feedback on code changes.

**Key areas covered:**

- Core detection engine logic
- OCSF schema mapping
- Data parsing and transformation
- Database operations (mocked)
- API endpoint handlers (mocked)

**Location:** `tests/unit/`

### Integration Testing

Integration tests verify that components work together correctly. They test the interaction between different parts of the system.

**Key areas covered:**

- API endpoints with real database connections
- Pipeline components working together
- Detection engine with database integration
- OCSF schema validation with real data

**Location:** `tests/integration/`

### Manual Testing

Manual testing provides a way to verify the system's behavior in a real-world scenario. It's useful for exploratory testing and verifying end-to-end functionality.

**Tools provided:**

- Test data generator (`tests/generate_test_data.py`)
- Manual test scenario script (`tests/run_manual_test.sh`)

## Test Data

### Test Data Generation

The project includes a test data generator that can create events in different formats:

- OCSF (Open Cybersecurity Schema Framework)
- Syslog
- CEF (Common Event Format)
- LEEF (Log Event Extended Format)

This allows testing of the system's ability to ingest, parse, and map different event formats to OCSF.

### Test Fixtures

Integration tests use pytest fixtures to set up the test environment:

- Neo4j database container
- Database connection
- FastAPI test client

These fixtures ensure that tests run in a consistent environment and that the database is cleaned between tests.

## Test Execution

### Continuous Integration

Tests should be run as part of the CI/CD pipeline to ensure code quality and prevent regressions.

Recommended CI workflow:

1. Run unit tests
2. Run integration tests
3. Generate code coverage report
4. Fail the build if coverage is below threshold or tests fail

### Local Development

For local development, the following commands are available:

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
./run_integration_tests.sh

# Generate test data
./tests/generate_test_data.py --count 10 --format ocsf

# Run manual test scenario
./tests/run_manual_test.sh
```

## Test Coverage

The project aims for high test coverage, with a focus on critical components:

- Detection engine
- OCSF schema mapping
- API endpoints
- Data ingestion pipeline

Coverage reports can be generated using pytest-cov:

```bash
pytest --cov=src tests/
```

## Test Scenarios

### API Integration Tests

- Health check endpoint
- CRUD operations for detection rules
- Event ingestion and retrieval
- Running detection rules
- Alert generation and retrieval

### Pipeline Integration Tests

- Event parsing from different formats
- Source format detection
- Mapping to OCSF schema
- Storing events in the graph database
- End-to-end pipeline processing

### Detection Engine Integration Tests

- Loading detection rules
- Running specific detection rules
- Running all detection rules
- Alert generation and storage

### OCSF Schema Integration Tests

- Loading schema definitions
- Validating events against schema
- Mapping events from different formats to OCSF
- Handling schema validation errors

## Best Practices

1. **Test isolation:** Each test should be independent and not rely on the state from other tests.
2. **Clean setup and teardown:** Ensure the test environment is clean before and after each test.
3. **Meaningful assertions:** Test assertions should be clear and meaningful.
4. **Test edge cases:** Include tests for edge cases and error conditions.
5. **Mocking external dependencies:** Use mocks for external dependencies in unit tests.
6. **Real dependencies in integration tests:** Use real dependencies in integration tests to verify actual behavior.
7. **Test documentation:** Document the purpose and expectations of each test.
8. **Regular test maintenance:** Keep tests up to date with code changes.

## Future Improvements

- Performance testing for large-scale event ingestion
- Security testing (e.g., penetration testing, SAST)
- Chaos testing for resilience verification
- User acceptance testing with real-world scenarios
- Benchmark testing for detection rule performance
