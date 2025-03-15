#!/usr/bin/env python3
"""
End-to-end test for Kafka integration with Blueprint Graph.

This test verifies the API health and Neo4j connection in an isolated environment
with dedicated ports to avoid conflicts with local development services.
"""
import pytest
import requests
import json
import time
from py2neo import Graph
# Use absolute imports instead of relative imports
from tests.integration.e2e.conftest import (
    API_PORT, NEO4J_BOLT_PORT, 
    NEO4J_USER, NEO4J_PASSWORD
)


def test_kafka_e2e_flow(e2e_services):
    """
    Test the end-to-end flow of the API and Neo4j connection.
    
    This test verifies:
    1. The API is healthy
    2. The Neo4j connection is working
    3. The Kafka connection is working
    """
    # Check API health
    api_health_url = f"http://localhost:{API_PORT}/health"
    response = requests.get(api_health_url)
    
    assert response.status_code == 200, f"API health check failed with status {response.status_code}"
    health_data = response.json()
    assert health_data["status"] == "healthy", f"API reports unhealthy status: {health_data}"
    assert health_data["database"] == "connected", f"Database connection failed: {health_data}"
    
    # Check Kafka health
    kafka_health_url = f"http://localhost:{API_PORT}/health/kafka"
    response = requests.get(kafka_health_url)
    
    assert response.status_code == 200, f"Kafka health check failed with status {response.status_code}"
    kafka_health = response.json()
    assert kafka_health["status"] == "healthy", f"Kafka connection failed: {kafka_health}"
    
    # Verify Neo4j connection directly
    graph = Graph(
        f"bolt://localhost:{NEO4J_BOLT_PORT}", 
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    
    # Run a simple query to verify connection
    result = graph.run("RETURN 1 as n").data()
    assert result[0]['n'] == 1, "Failed to execute query on Neo4j"
    
    print("E2E test successful: API is healthy, Neo4j connection is working, and Kafka is healthy") 