"""
Integration tests for the data ingestion pipeline.
"""
import json
import pytest
from neo4j import GraphDatabase

from src.pipelines.ingest import ParseEvent, DetectSourceFormat, MapToOCSF, StoreInGraph
from src.utils import settings


class TestPipelineComponents:
    """Tests for individual pipeline components."""
    
    def test_parse_event(self, clean_database):
        """Test the ParseEvent component."""
        # Create a test event
        event_json = json.dumps({
            "timestamp": "2023-01-01T12:00:00Z",
            "severity": 3,
            "facility": 1,
            "hostname": "test-host",
            "message": "Test syslog message"
        })
        
        # Process the event
        parse_event = ParseEvent()
        results = list(parse_event.process(event_json))
        
        # Verify the results
        assert len(results) == 1
        assert results[0]["timestamp"] == "2023-01-01T12:00:00Z"
        assert results[0]["severity"] == 3
        assert results[0]["facility"] == 1
        assert results[0]["hostname"] == "test-host"
        assert results[0]["message"] == "Test syslog message"
    
    def test_detect_source_format(self, clean_database):
        """Test the DetectSourceFormat component."""
        # Create test events
        syslog_event = {
            "timestamp": "2023-01-01T12:00:00Z",
            "severity": 3,
            "facility": 1,
            "hostname": "test-host",
            "message": "Test syslog message"
        }
        
        cef_event = {
            "deviceVendor": "Test Vendor",
            "deviceProduct": "Test Product",
            "deviceVersion": "1.0",
            "deviceEventClassId": "100",
            "name": "Test Event",
            "severity": "5"
        }
        
        leef_event = {
            "devname": "Test Device",
            "devtime": "2023-01-01T12:00:00Z",
            "devtype": "Test Type",
            "sev": 5,
            "msg": "Test LEEF message"
        }
        
        ocsf_event = {
            "class_uid": "0001",
            "category_uid": "0002",
            "time": "2023-01-01T12:00:00Z",
            "severity": 5,
            "message": "Test OCSF event",
            "metadata": {
                "version": "1.0.0",
                "product": {
                    "name": "Test Product"
                }
            }
        }
        
        unknown_event = {
            "field1": "value1",
            "field2": "value2"
        }
        
        # Process the events
        detect_format = DetectSourceFormat()
        
        syslog_results = list(detect_format.process(syslog_event))
        cef_results = list(detect_format.process(cef_event))
        leef_results = list(detect_format.process(leef_event))
        ocsf_results = list(detect_format.process(ocsf_event))
        unknown_results = list(detect_format.process(unknown_event))
        
        # Verify the results
        assert len(syslog_results) == 1
        assert syslog_results[0][1] == "syslog"
        
        assert len(cef_results) == 1
        assert cef_results[0][1] == "cef"
        
        assert len(leef_results) == 1
        assert leef_results[0][1] == "leef"
        
        assert len(ocsf_results) == 1
        assert ocsf_results[0][1] == "ocsf"
        
        assert len(unknown_results) == 1
        assert unknown_results[0][1] == "unknown"
    
    def test_map_to_ocsf(self, clean_database):
        """Test the MapToOCSF component."""
        # Create test events with formats
        syslog_event = ({
            "timestamp": "2023-01-01T12:00:00Z",
            "severity": 3,
            "facility": 1,
            "hostname": "test-host",
            "message": "Test syslog message"
        }, "syslog")
        
        cef_event = ({
            "deviceVendor": "Test Vendor",
            "deviceProduct": "Test Product",
            "deviceVersion": "1.0",
            "deviceEventClassId": "100",
            "name": "Test Event",
            "severity": "5",
            "deviceReceiptTime": "2023-01-01T12:00:00Z",
            "message": "Test CEF message"
        }, "cef")
        
        ocsf_event = ({
            "class_uid": "0001",
            "category_uid": "0002",
            "time": "2023-01-01T12:00:00Z",
            "severity": 5,
            "message": "Test OCSF event",
            "metadata": {
                "version": "1.0.0",
                "product": {
                    "name": "Test Product"
                }
            }
        }, "ocsf")
        
        # Process the events
        map_to_ocsf = MapToOCSF()
        
        syslog_results = list(map_to_ocsf.process(syslog_event))
        cef_results = list(map_to_ocsf.process(cef_event))
        ocsf_results = list(map_to_ocsf.process(ocsf_event))
        
        # Verify the results
        assert len(syslog_results) == 1
        assert "class_uid" in syslog_results[0]
        assert "metadata" in syslog_results[0]
        assert syslog_results[0]["message"] == "Test syslog message"
        
        assert len(cef_results) == 1
        assert "class_uid" in cef_results[0]
        assert "metadata" in cef_results[0]
        assert cef_results[0]["message"] == "Test CEF message"
        
        assert len(ocsf_results) == 1
        assert ocsf_results[0]["class_uid"] == "0001"
        assert ocsf_results[0]["category_uid"] == "0002"
        assert ocsf_results[0]["message"] == "Test OCSF event"
    
    def test_store_in_graph(self, neo4j_connection, clean_database):
        """Test the StoreInGraph component."""
        # Create a test OCSF event
        ocsf_event = {
            "class_uid": "0001",
            "category_uid": "0002",
            "time": "2023-01-01T12:00:00Z",
            "severity": 5,
            "message": "Test OCSF event",
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
            },
            "dst": {
                "id": "dst-001",
                "type": "IP",
                "ip": "8.8.8.8"
            },
            "principal": {
                "id": "user-001",
                "type": "User",
                "name": "testuser",
                "domain": "testdomain"
            }
        }
        
        # Process the event
        store_in_graph = StoreInGraph()
        results = list(store_in_graph.process(ocsf_event))
        
        # Verify the results
        assert len(results) == 1
        assert "_id" in results[0]
        
        # Verify the event was stored in the database
        with neo4j_connection.session() as session:
            # Check Event node
            result = session.run("MATCH (e:Event) RETURN count(e) as count")
            assert result.single()["count"] == 1
            
            # Check source entity
            result = session.run("MATCH (s:IP {id: 'src-001'}) RETURN s.ip as ip")
            record = result.single()
            assert record["ip"] == "192.168.1.100"
            
            # Check destination entity
            result = session.run("MATCH (d:IP {id: 'dst-001'}) RETURN d.ip as ip")
            record = result.single()
            assert record["ip"] == "8.8.8.8"
            
            # Check principal entity
            result = session.run("MATCH (p:User {id: 'user-001'}) RETURN p.name as name, p.domain as domain")
            record = result.single()
            assert record["name"] == "testuser"
            assert record["domain"] == "testdomain"
            
            # Check relationships
            result = session.run("""
            MATCH (s:IP {id: 'src-001'})-[:GENERATED]->(e:Event)
            MATCH (e)-[:TARGETS]->(d:IP {id: 'dst-001'})
            MATCH (p:User {id: 'user-001'})-[:PERFORMED]->(e)
            RETURN count(e) as count
            """)
            assert result.single()["count"] == 1


class TestEndToEndPipeline:
    """End-to-end tests for the pipeline."""
    
    def test_pipeline_processing(self, neo4j_connection, clean_database):
        """Test the complete pipeline processing flow."""
        # Create test events
        events = [
            # Syslog event
            json.dumps({
                "timestamp": "2023-01-01T12:00:00Z",
                "severity": 3,
                "facility": 1,
                "hostname": "test-host-1",
                "message": "Test syslog message"
            }),
            
            # CEF event
            json.dumps({
                "deviceVendor": "Test Vendor",
                "deviceProduct": "Test Product",
                "deviceVersion": "1.0",
                "deviceEventClassId": "100",
                "name": "Test Event",
                "severity": "5",
                "deviceReceiptTime": "2023-01-01T13:00:00Z",
                "message": "Test CEF message"
            }),
            
            # OCSF event
            json.dumps({
                "class_uid": "0001",
                "category_uid": "0002",
                "time": "2023-01-01T14:00:00Z",
                "severity": 5,
                "message": "Test OCSF event",
                "metadata": {
                    "version": "1.0.0",
                    "product": {
                        "name": "Test Product"
                    }
                },
                "src": {
                    "id": "src-001",
                    "type": "IP",
                    "ip": "192.168.1.100"
                }
            })
        ]
        
        # Create pipeline components
        parse_event = ParseEvent()
        detect_format = DetectSourceFormat()
        map_to_ocsf = MapToOCSF()
        store_in_graph = StoreInGraph()
        
        # Process each event through the pipeline
        for event_json in events:
            for parsed_event in parse_event.process(event_json):
                for event_with_format in detect_format.process(parsed_event):
                    for ocsf_event in map_to_ocsf.process(event_with_format):
                        for _ in store_in_graph.process(ocsf_event):
                            pass
        
        # Verify the events were stored in the database
        with neo4j_connection.session() as session:
            # Check Event nodes
            result = session.run("MATCH (e:Event) RETURN count(e) as count")
            assert result.single()["count"] == 3
            
            # Check source entity
            result = session.run("MATCH (s:IP {id: 'src-001'}) RETURN s.ip as ip")
            record = result.single()
            assert record["ip"] == "192.168.1.100"
            
            # Check relationships
            result = session.run("""
            MATCH (s:IP {id: 'src-001'})-[:GENERATED]->(e:Event)
            RETURN count(e) as count
            """)
            assert result.single()["count"] == 1 