"""
Pytest configuration for integration tests.
"""
import os
import time
import pytest
import docker
import requests
from fastapi.testclient import TestClient
from neo4j import GraphDatabase

from src.api.main import app
from src.utils import settings


@pytest.fixture(scope="session")
def neo4j_container():
    """Start a Neo4j container for testing."""
    client = docker.from_env()
    
    # Check if container already exists and remove it
    try:
        container = client.containers.get("blueprintgraph-test-neo4j")
        container.remove(force=True)
    except docker.errors.NotFound:
        pass
    
    # Start a new container
    container = client.containers.run(
        "neo4j:5.13.0",
        name="blueprintgraph-test-neo4j",
        ports={"7474/tcp": 7475, "7687/tcp": 7688},
        environment={
            "NEO4J_AUTH": "neo4j/testpassword",
            "NEO4J_dbms_memory_heap_initial__size": "512m",
            "NEO4J_dbms_memory_heap_max__size": "1G",
        },
        detach=True,
    )
    
    # Wait for Neo4j to start
    time.sleep(10)
    
    yield container
    
    # Cleanup
    container.remove(force=True)


@pytest.fixture(scope="session")
def neo4j_connection(neo4j_container):
    """Create a Neo4j connection for testing."""
    uri = "bolt://localhost:7688"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "testpassword"))
    
    # Test the connection
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        assert result.single()["test"] == 1
    
    yield driver
    
    # Cleanup
    driver.close()


@pytest.fixture(scope="function")
def test_client(neo4j_connection):
    """Create a FastAPI test client."""
    # Override settings for testing
    settings.neo4j_uri = "bolt://localhost:7688"
    settings.neo4j_user = "neo4j"
    settings.neo4j_password = "testpassword"
    
    # Create test client
    client = TestClient(app)
    
    yield client


@pytest.fixture(scope="function")
def clean_database(neo4j_connection):
    """Clean the database before each test."""
    with neo4j_connection.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    
    yield 