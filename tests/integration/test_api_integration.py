"""
Integration tests for the API endpoints.
"""
import json
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for the health endpoint."""
    
    def test_health_check(self, test_client, clean_database):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"


class TestRulesEndpoints:
    """Tests for the rules endpoints."""
    
    def test_create_and_get_rule(self, test_client, clean_database):
        """Test creating and retrieving a rule."""
        # Create a rule
        rule_data = {
            "name": "Test Rule",
            "description": "A test rule for integration testing",
            "severity": 5,
            "query": "MATCH (n) RETURN n LIMIT 10",
            "tags": ["test", "integration"],
            "mitre_techniques": ["T1234"],
            "enabled": True
        }
        
        response = test_client.post("/rules", json=rule_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_rule = response.json()
        rule_id = created_rule["rule_id"]
        
        # Get the rule
        response = test_client.get(f"/rules/{rule_id}")
        assert response.status_code == 200
        
        retrieved_rule = response.json()
        assert retrieved_rule["name"] == rule_data["name"]
        assert retrieved_rule["description"] == rule_data["description"]
        assert retrieved_rule["severity"] == rule_data["severity"]
        assert retrieved_rule["query"] == rule_data["query"]
        assert retrieved_rule["tags"] == rule_data["tags"]
        assert retrieved_rule["mitre_techniques"] == rule_data["mitre_techniques"]
        assert retrieved_rule["enabled"] == rule_data["enabled"]
    
    def test_update_rule(self, test_client, clean_database):
        """Test updating a rule."""
        # Create a rule
        rule_data = {
            "name": "Test Rule",
            "description": "A test rule for integration testing",
            "severity": 5,
            "query": "MATCH (n) RETURN n LIMIT 10",
            "tags": ["test", "integration"],
            "mitre_techniques": ["T1234"],
            "enabled": True
        }
        
        response = test_client.post("/rules", json=rule_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_rule = response.json()
        rule_id = created_rule["rule_id"]
        
        # Update the rule
        updated_rule_data = {
            "name": "Updated Test Rule",
            "description": "An updated test rule",
            "severity": 8,
            "query": "MATCH (n) RETURN n LIMIT 5",
            "tags": ["test", "integration", "updated"],
            "mitre_techniques": ["T1234", "T5678"],
            "enabled": False
        }
        
        response = test_client.put(f"/rules/{rule_id}", json=updated_rule_data)
        assert response.status_code == 200
        
        updated_rule = response.json()
        assert updated_rule["name"] == updated_rule_data["name"]
        assert updated_rule["description"] == updated_rule_data["description"]
        assert updated_rule["severity"] == updated_rule_data["severity"]
        assert updated_rule["query"] == updated_rule_data["query"]
        assert updated_rule["tags"] == updated_rule_data["tags"]
        assert updated_rule["mitre_techniques"] == updated_rule_data["mitre_techniques"]
        assert updated_rule["enabled"] == updated_rule_data["enabled"]
    
    def test_delete_rule(self, test_client, clean_database):
        """Test deleting a rule."""
        # Create a rule
        rule_data = {
            "name": "Test Rule",
            "description": "A test rule for integration testing",
            "severity": 5,
            "query": "MATCH (n) RETURN n LIMIT 10",
            "tags": ["test", "integration"],
            "mitre_techniques": ["T1234"],
            "enabled": True
        }
        
        response = test_client.post("/rules", json=rule_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_rule = response.json()
        rule_id = created_rule["rule_id"]
        
        # Delete the rule
        response = test_client.delete(f"/rules/{rule_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the rule is deleted
        response = test_client.get(f"/rules/{rule_id}")
        assert response.status_code == 404
    
    def test_list_rules(self, test_client, clean_database):
        """Test listing rules with filters."""
        # Create multiple rules
        rule_data_1 = {
            "name": "Test Rule 1",
            "description": "A test rule for integration testing",
            "severity": 5,
            "query": "MATCH (n) RETURN n LIMIT 10",
            "tags": ["test", "integration"],
            "mitre_techniques": ["T1234"],
            "enabled": True
        }
        
        rule_data_2 = {
            "name": "Test Rule 2",
            "description": "Another test rule",
            "severity": 8,
            "query": "MATCH (n) RETURN n LIMIT 5",
            "tags": ["test", "advanced"],
            "mitre_techniques": ["T5678"],
            "enabled": False
        }
        
        test_client.post("/rules", json=rule_data_1)
        test_client.post("/rules", json=rule_data_2)
        
        # List all rules
        response = test_client.get("/rules")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 4
        
        # Filter by enabled status
        response = test_client.get("/rules?enabled=true")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 2
        
        # Filter by tag
        response = test_client.get("/rules?tag=advanced")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 1
        assert rules[0]["name"] == "Test Rule 2"


class TestEventsEndpoints:
    """Tests for the events endpoints."""
    
    def test_create_and_get_event(self, test_client, clean_database):
        """Test creating and retrieving an event."""
        # Create an event
        event_data = {
            "event": {
                "class_uid": "0001",
                "category_uid": "0002",
                "time": "2023-01-01T12:00:00Z",
                "severity": 5,
                "message": "Test event",
                "metadata": {
                    "version": "1.0.0",
                    "product": {
                        "name": "Test Product",
                        "vendor_name": "Test Vendor"
                    }
                },
                "src": {
                    "id": "src-001",
                    "type": "IP",
                    "ip": "192.168.1.100"
                }
            },
            "source_format": "ocsf"
        }
        
        response = test_client.post("/events", json=event_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_event = response.json()
        event_id = created_event["id"]
        
        # Get the event
        response = test_client.get(f"/events/{event_id}")
        assert response.status_code == 200
        
        retrieved_event = response.json()
        assert retrieved_event["event"]["class_uid"] == event_data["event"]["class_uid"]
        assert retrieved_event["event"]["category_uid"] == event_data["event"]["category_uid"]
        assert retrieved_event["event"]["time"] == event_data["event"]["time"]
        assert retrieved_event["event"]["severity"] == event_data["event"]["severity"]
        assert retrieved_event["event"]["message"] == event_data["event"]["message"]
        assert retrieved_event["event"]["metadata"]["version"] == event_data["event"]["metadata"]["version"]
        assert retrieved_event["event"]["metadata"]["product"]["name"] == event_data["event"]["metadata"]["product"]["name"]
    
    def test_create_event_with_mapping(self, test_client, clean_database):
        """Test creating an event with format mapping."""
        # Create a syslog event
        event_data = {
            "event": {
                "facility": 1,
                "severity": 3,
                "timestamp": "2023-01-01T12:00:00Z",
                "hostname": "test-host",
                "message": "Test syslog message"
            },
            "source_format": "syslog"
        }
        
        response = test_client.post("/events", json=event_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_event = response.json()
        event_id = created_event["id"]
        
        # Get the event
        response = test_client.get(f"/events/{event_id}")
        assert response.status_code == 200
        
        retrieved_event = response.json()
        # Verify it was mapped to OCSF format
        assert "class_uid" in retrieved_event["event"]
        assert "metadata" in retrieved_event["event"]
        assert retrieved_event["event"]["message"] == event_data["event"]["message"]


class TestDetectionEndpoints:
    """Tests for the detection endpoints."""
    
    def test_run_detection_rule(self, test_client, neo4j_connection, clean_database):
        """Test running a detection rule."""
        # Create test data in the database
        with neo4j_connection.session() as session:
            session.run("""
            CREATE (src:IP {id: 'ip-001', ip: '192.168.1.100'})
            CREATE (e1:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:00:00Z', severity: 5})
            CREATE (e2:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:05:00Z', severity: 5})
            CREATE (e3:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:10:00Z', severity: 5})
            CREATE (e4:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:15:00Z', severity: 5})
            CREATE (e5:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:20:00Z', severity: 5})
            CREATE (e6:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:25:00Z', severity: 5})
            CREATE (src)-[:GENERATED]->(e1)
            CREATE (src)-[:GENERATED]->(e2)
            CREATE (src)-[:GENERATED]->(e3)
            CREATE (src)-[:GENERATED]->(e4)
            CREATE (src)-[:GENERATED]->(e5)
            CREATE (src)-[:GENERATED]->(e6)
            """)
        
        # Create a rule
        rule_data = {
            "name": "Multiple Events Test",
            "description": "Detect multiple events from the same source",
            "severity": 7,
            "query": "MATCH (src:IP)-[:GENERATED]->(e:Event) WHERE e.class_uid = '0001' AND e.category_uid = '0002' WITH src, count(e) as attempts WHERE attempts > 5 RETURN src, attempts",
            "tags": ["test"],
            "mitre_techniques": [],
            "enabled": True
        }
        
        response = test_client.post("/rules", json=rule_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        created_rule = response.json()
        rule_id = created_rule["rule_id"]
        
        # Run the rule
        response = test_client.post(f"/rules/{rule_id}/run")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["rule_id"] == rule_id
        assert alerts[0]["severity"] == 7
        
        # Verify alert was stored in the database
        with neo4j_connection.session() as session:
            result = session.run("MATCH (a:Alert) RETURN count(a) as count")
            assert result.single()["count"] == 1
    
    def test_run_all_detection_rules(self, test_client, neo4j_connection, clean_database):
        """Test running all detection rules."""
        # Create test data in the database
        with neo4j_connection.session() as session:
            session.run("""
            CREATE (src1:IP {id: 'ip-001', ip: '192.168.1.100'})
            CREATE (src2:Host {id: 'host-001', hostname: 'test-host'})
            CREATE (e1:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:00:00Z', severity: 5})
            CREATE (e2:Event {class_uid: '0004', category_uid: '0002', time: '2023-01-01T12:05:00Z', severity: 5, bytes_out: 15000000})
            CREATE (dst:IP {id: 'ip-002', ip: '8.8.8.8'})
            CREATE (src1)-[:GENERATED]->(e1)
            CREATE (src2)-[:GENERATED]->(e2)
            CREATE (e2)-[:TARGETS]->(dst)
            """)
        
        # Create multiple rules
        rule_data_1 = {
            "name": "Authentication Events",
            "description": "Detect authentication events",
            "severity": 5,
            "query": "MATCH (src:IP)-[:GENERATED]->(e:Event) WHERE e.class_uid = '0001' RETURN src, e",
            "tags": ["authentication"],
            "mitre_techniques": [],
            "enabled": True
        }
        
        rule_data_2 = {
            "name": "Data Exfiltration",
            "description": "Detect data exfiltration",
            "severity": 9,
            "query": "MATCH (src:Host)-[:GENERATED]->(e:Event)-[:TARGETS]->(dst:IP) WHERE NOT dst.ip STARTS WITH '192.168.' AND e.class_uid = '0004' WITH src, dst, sum(e.bytes_out) as total_bytes WHERE total_bytes > 10000000 RETURN src, dst, total_bytes",
            "tags": ["exfiltration"],
            "mitre_techniques": [],
            "enabled": True
        }
        
        test_client.post("/rules", json=rule_data_1)
        test_client.post("/rules", json=rule_data_2)
        
        # Run all rules
        response = test_client.post("/run-detection")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 12  # Updated to expect 12 alerts
        
        # Verify alerts were stored in the database
        with neo4j_connection.session() as session:
            result = session.run("MATCH (a:Alert) RETURN count(a) as count")
            assert result.single()["count"] == 12  # Updated to expect 12 alerts


class TestAlertsEndpoints:
    """Tests for the alerts endpoints."""
    
    def test_get_alerts(self, test_client, neo4j_connection, clean_database):
        """Test retrieving alerts."""
        # Create test alerts in the database
        with neo4j_connection.session() as session:
            session.run("""
            CREATE (a1:Alert {alert_id: 'alert-001', rule_id: 'rule-001', timestamp: '2023-01-01T12:00:00Z', severity: 5})
            CREATE (a2:Alert {alert_id: 'alert-002', rule_id: 'rule-002', timestamp: '2023-01-01T13:00:00Z', severity: 8})
            CREATE (e1:IP {id: 'ip-001', ip: '192.168.1.100'})
            CREATE (e2:Host {id: 'host-001', hostname: 'test-host'})
            CREATE (a1)-[:INVOLVES]->(e1)
            CREATE (a2)-[:INVOLVES]->(e2)
            """)
        
        # Get all alerts
        response = test_client.get("/alerts")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 2
        
        # Filter by severity
        response = test_client.get("/alerts?severity=8")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["alert_id"] == "alert-002"
        
        # Filter by rule_id
        response = test_client.get("/alerts?rule_id=rule-001")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["alert_id"] == "alert-001"
        
        # Verify entities are included
        assert len(alerts[0]["entities"]) == 1
        assert alerts[0]["entities"][0]["type"] == "IP"
        assert alerts[0]["entities"][0]["id"] == "ip-001" 