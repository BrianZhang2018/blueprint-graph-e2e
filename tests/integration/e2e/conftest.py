"""
Pytest fixtures for E2E integration tests.

This module provides fixtures for setting up and tearing down the services
required for E2E testing, such as Neo4j, Kafka, and the API.
"""
import os
import time
import subprocess
import pytest
import docker
import requests
import yaml
import tempfile
from pathlib import Path
from neo4j import GraphDatabase

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
TEST_NETWORK_NAME = "blueprintgraph_test_network"
TEST_PROJECT_NAME = "blueprintgraph_test"
TEST_CONTAINER_PREFIX = "e2e_test_"  # Prefix for test container names

# Test-specific ports (different from development ports to avoid conflicts)
API_PORT = 18001
KAFKA_PORT = 19092
KAFKA_INTERNAL_PORT = 29093
NEO4J_HTTP_PORT = 17475
NEO4J_BOLT_PORT = 17688
ZOOKEEPER_PORT = 12181
KAFKA_UI_PORT = 18080

# Neo4j credentials
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "blueprintgraph"


@pytest.fixture(scope="session")
def docker_client():
    """
    Create a Docker client for managing containers.
    """
    return docker.from_env()


@pytest.fixture(scope="session")
def docker_network(docker_client):
    """
    Create a Docker network for test containers.
    """
    networks = docker_client.networks.list(names=[TEST_NETWORK_NAME])
    
    if networks:
        network = networks[0]
        print(f"Using existing network: {TEST_NETWORK_NAME}")
    else:
        network = docker_client.networks.create(
            TEST_NETWORK_NAME,
            driver="bridge"
        )
        print(f"Created network: {TEST_NETWORK_NAME}")
    
    yield network
    
    # Cleanup is handled by docker-compose down


@pytest.fixture(scope="session")
def docker_compose_override():
    """
    Create a temporary docker-compose override file with test-specific ports.
    """
    # Create a temporary file for the docker-compose override
    fd, path = tempfile.mkstemp(prefix="docker-compose-test-", suffix=".yml")
    override_path = Path(path)
    
    # Write the override configuration to the file
    with open(fd, "w") as f:
        f.write(f"""version: '3'
services:
  neo4j:
    container_name: {TEST_CONTAINER_PREFIX}neo4j
    ports:
      - "{NEO4J_HTTP_PORT}:7474"
      - "{NEO4J_BOLT_PORT}:7687"
    environment:
      - NEO4J_AUTH={NEO4J_USER}/{NEO4J_PASSWORD}

  zookeeper:
    container_name: {TEST_CONTAINER_PREFIX}zookeeper
    ports:
      - "{ZOOKEEPER_PORT}:2181"

  kafka:
    container_name: {TEST_CONTAINER_PREFIX}kafka
    ports:
      - "{KAFKA_PORT}:9092"
      - "{KAFKA_INTERNAL_PORT}:29092"
    environment:
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:{KAFKA_PORT}
      - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      - KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:29092
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181

  api:
    container_name: {TEST_CONTAINER_PREFIX}api
    ports:
      - "{API_PORT}:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER={NEO4J_USER}
      - NEO4J_PASSWORD={NEO4J_PASSWORD}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092

  kafka-consumer:
    container_name: {TEST_CONTAINER_PREFIX}kafka-consumer
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER={NEO4J_USER}
      - NEO4J_PASSWORD={NEO4J_PASSWORD}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092

  kafka-ui:
    container_name: {TEST_CONTAINER_PREFIX}kafka-ui
    ports:
      - "{KAFKA_UI_PORT}:8080"
    environment:
      - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:9092
""")
    
    print(f"Created docker-compose override file: {override_path}")
    
    yield override_path
    
    # Clean up the temporary file
    os.unlink(override_path)
    print(f"Removed docker-compose override file: {override_path}")


@pytest.fixture(scope="session")
def e2e_services(docker_client, docker_network, docker_compose_override):
    """
    Start all services required for E2E testing.

    This fixture uses docker-compose to start Neo4j, Kafka, Zookeeper,
    the API, and the Kafka consumer with test-specific ports to avoid conflicts.
    """
    try:
        print("Starting E2E test services...")

        # Use docker-compose with override file and test project name
        cmd = [
            "docker-compose",
            "-f", str(COMPOSE_FILE),
            "-f", str(docker_compose_override),
            "-p", TEST_PROJECT_NAME,
            "up",
            "-d",
            "neo4j", "zookeeper", "kafka", "api", "kafka-consumer", "kafka-ui"
        ]

        subprocess.run(cmd, check=True)

        # Wait for services to be healthy
        wait_for_api_health(f"http://localhost:{API_PORT}/health")
        wait_for_neo4j_health(f"bolt://localhost:{NEO4J_BOLT_PORT}", NEO4J_USER, NEO4J_PASSWORD)
        wait_for_kafka_health(f"http://localhost:{API_PORT}/health/kafka")

        yield
    except Exception as e:
        print(f"Error setting up E2E services: {e}")
        raise
    finally:
        print("Tearing down E2E test services...")
        
        # Use docker-compose to tear down all services
        cmd = [
            "docker-compose",
            "-f", str(COMPOSE_FILE),
            "-f", str(docker_compose_override),
            "-p", TEST_PROJECT_NAME,
            "down",
            "-v"  # Remove volumes
        ]
        
        subprocess.run(cmd)


def wait_for_api_health(health_url, max_retries=30, retry_interval=2):
    """
    Wait for the API to be healthy.
    """
    print(f"Waiting for API to be healthy at {health_url}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("API is healthy!")
                return True
        except requests.RequestException:
            pass
        
        print(f"API not healthy yet, retrying in {retry_interval}s... ({i+1}/{max_retries})")
        time.sleep(retry_interval)
    
    raise Exception(f"API health check failed after {max_retries} retries")


def wait_for_neo4j_health(bolt_uri, user, password, max_retries=30, retry_interval=2):
    """
    Wait for Neo4j to be healthy.
    """
    print(f"Waiting for Neo4j to be healthy at {bolt_uri}...")
    
    for i in range(max_retries):
        try:
            driver = GraphDatabase.driver(bolt_uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 as n")
                if result.single()["n"] == 1:
                    print("Neo4j is healthy!")
                    driver.close()
                    return True
            driver.close()
        except Exception:
            pass
        
        print(f"Neo4j not healthy yet, retrying in {retry_interval}s... ({i+1}/{max_retries})")
        time.sleep(retry_interval)
    
    raise Exception(f"Neo4j health check failed after {max_retries} retries")


def wait_for_kafka_health(health_url, max_retries=30, retry_interval=2):
    """
    Wait for Kafka to be healthy.
    """
    print(f"Waiting for Kafka to be healthy at {health_url}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("Kafka is healthy!")
                return True
        except requests.RequestException:
            pass
        
        print(f"Kafka not healthy yet, retrying in {retry_interval}s... ({i+1}/{max_retries})")
        time.sleep(retry_interval)
    
    raise Exception(f"Kafka health check failed after {max_retries} retries") 