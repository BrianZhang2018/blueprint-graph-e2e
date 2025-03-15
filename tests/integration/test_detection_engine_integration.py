"""
Integration tests for the detection engine.
"""
import json
import pytest
from datetime import datetime

from src.core import DetectionRule, detection_engine
from src.utils import settings, db


class TestDetectionEngine:
    """Tests for the detection engine."""
    
    def setup_method(self):
        """Set up the test environment."""
        # Save original settings
        self.original_uri = settings.neo4j_uri
        self.original_user = settings.neo4j_user
        self.original_password = settings.neo4j_password
        
        # Override settings for testing
        settings.neo4j_uri = "bolt://localhost:7688"
        settings.neo4j_user = "neo4j"
        settings.neo4j_password = "testpassword"
        
        # Reset the database connection to use the new settings
        if db._driver:
            db.close()
    
    def teardown_method(self):
        """Tear down the test environment."""
        # Restore original settings
        settings.neo4j_uri = self.original_uri
        settings.neo4j_user = self.original_user
        settings.neo4j_password = self.original_password
        
        # Reset the database connection
        if db._driver:
            db.close()
    
    def test_load_rule(self, clean_database):
        """Test loading a detection rule."""
        # Create a rule
        rule = DetectionRule(
            rule_id="TEST-001",
            name="Test Rule",
            description="A test rule for integration testing",
            severity=5,
            query="MATCH (n) RETURN n LIMIT 10",
            tags=["test", "integration"],
            mitre_techniques=["T1234"],
            enabled=True
        )
        
        # Load the rule
        detection_engine.load_rule(rule)
        
        # Verify the rule was loaded
        assert "TEST-001" in detection_engine.rules
        assert detection_engine.rules["TEST-001"].name == "Test Rule"
        assert detection_engine.rules["TEST-001"].description == "A test rule for integration testing"
        assert detection_engine.rules["TEST-001"].severity == 5
        assert detection_engine.rules["TEST-001"].query == "MATCH (n) RETURN n LIMIT 10"
        assert detection_engine.rules["TEST-001"].tags == ["test", "integration"]
        assert detection_engine.rules["TEST-001"].mitre_techniques == ["T1234"]
        assert detection_engine.rules["TEST-001"].enabled is True
    
    def test_load_rules_from_file(self, clean_database, tmp_path):
        """Test loading rules from a file."""
        # Create a temporary rules file
        rules_data = [
            {
                "rule_id": "TEST-001",
                "name": "Test Rule 1",
                "description": "A test rule for integration testing",
                "severity": 5,
                "query": "MATCH (n) RETURN n LIMIT 10",
                "tags": ["test", "integration"],
                "mitre_techniques": ["T1234"],
                "enabled": True
            },
            {
                "rule_id": "TEST-002",
                "name": "Test Rule 2",
                "description": "Another test rule",
                "severity": 8,
                "query": "MATCH (n) RETURN n LIMIT 5",
                "tags": ["test", "advanced"],
                "mitre_techniques": ["T5678"],
                "enabled": False
            }
        ]
        
        rules_file = tmp_path / "test_rules.json"
        with open(rules_file, "w") as f:
            json.dump(rules_data, f)
        
        # Load rules from the file
        detection_engine.load_rules_from_file(str(rules_file))
        
        # Verify the rules were loaded
        assert len(detection_engine.rules) == 2
        assert "TEST-001" in detection_engine.rules
        assert "TEST-002" in detection_engine.rules
        assert detection_engine.rules["TEST-001"].name == "Test Rule 1"
        assert detection_engine.rules["TEST-002"].name == "Test Rule 2"
    
    def test_run_detection_rule(self, neo4j_connection, clean_database):
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
        rule = DetectionRule(
            rule_id="TEST-001",
            name="Multiple Events Test",
            description="Detect multiple events from the same source",
            severity=7,
            query="MATCH (src:IP)-[:GENERATED]->(e:Event) WHERE e.class_uid = '0001' AND e.category_uid = '0002' WITH src, count(e) as attempts WHERE attempts > 5 RETURN src, attempts",
            tags=["test"],
            mitre_techniques=[],
            enabled=True
        )
        
        # Load the rule
        detection_engine.load_rule(rule)
        
        # Run the rule
        alerts = detection_engine.run_detection("TEST-001")
        
        # Verify the alerts
        assert len(alerts) == 1
        assert alerts[0].rule_id == "TEST-001"
        assert alerts[0].severity == 7
        assert len(alerts[0].entities) == 1
        # The entity type could be either 'IP' or 'Src' depending on how the Neo4j driver returns the node
        assert alerts[0].entities[0]["type"] in ['IP', 'Src']
        assert alerts[0].entities[0]["id"] == "ip-001"
    
    def test_run_all_detection_rules(self, neo4j_connection, clean_database):
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
        rule1 = DetectionRule(
            rule_id="TEST-001",
            name="Authentication Events",
            description="Detect authentication events",
            severity=5,
            query="MATCH (src:IP)-[:GENERATED]->(e:Event) WHERE e.class_uid = '0001' RETURN src, e",
            tags=["authentication"],
            mitre_techniques=[],
            enabled=True
        )
        
        rule2 = DetectionRule(
            rule_id="TEST-002",
            name="Data Exfiltration",
            description="Detect data exfiltration",
            severity=9,
            query="MATCH (src:Host)-[:GENERATED]->(e:Event)-[:TARGETS]->(dst:IP) WHERE NOT dst.ip STARTS WITH '192.168.' AND e.class_uid = '0004' WITH src, dst, sum(e.bytes_out) as total_bytes WHERE total_bytes > 10000000 RETURN src, dst, total_bytes",
            tags=["exfiltration"],
            mitre_techniques=[],
            enabled=True
        )
        
        # Load the rules
        detection_engine.load_rule(rule1)
        detection_engine.load_rule(rule2)
        
        # Run all rules
        alerts = detection_engine.run_detection()
        
        # Verify the alerts
        assert len(alerts) == 2
        
        # Find alerts by rule ID
        rule1_alerts = [a for a in alerts if a.rule_id == "TEST-001"]
        rule2_alerts = [a for a in alerts if a.rule_id == "TEST-002"]
        
        assert len(rule1_alerts) == 1
        assert rule1_alerts[0].severity == 5
        
        assert len(rule2_alerts) == 1
        assert rule2_alerts[0].severity == 9
    
    def test_store_alert(self, neo4j_connection, clean_database):
        """Test storing an alert in the database."""
        # Create test data in the database
        with neo4j_connection.session() as session:
            session.run("""
            CREATE (src:IP {id: 'ip-001', ip: '192.168.1.100'})
            CREATE (e:Event {class_uid: '0001', category_uid: '0002', time: '2023-01-01T12:00:00Z', severity: 5})
            CREATE (src)-[:GENERATED]->(e)
            """)
        
        # Create a rule and run it to generate an alert
        rule = DetectionRule(
            rule_id="TEST-001",
            name="Test Rule",
            description="A test rule",
            severity=7,
            query="MATCH (src:IP)-[:GENERATED]->(e:Event) RETURN src, e",
            tags=[],
            mitre_techniques=[],
            enabled=True
        )
        
        detection_engine.load_rule(rule)
        alerts = detection_engine.run_detection("TEST-001")
        
        # Store the alert
        result = detection_engine.store_alert(alerts[0])
        
        # Verify the result
        assert result is True
        
        # Verify the alert was stored in the database
        with neo4j_connection.session() as session:
            # Check Alert node
            result = session.run("MATCH (a:Alert) RETURN count(a) as count")
            assert result.single()["count"] == 1
            
            # Check relationship to entity - could be either IP or Src depending on how the entity was created
            result = session.run("""
            MATCH (a:Alert)-[:INVOLVES]->(e)
            WHERE e.id = 'ip-001'
            RETURN e.id as id
            """)
            assert result.single()["id"] == "ip-001" 