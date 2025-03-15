"""
Integration tests for the OCSF schema handling.
"""
import os
import json
import pytest
import tempfile
from jsonschema import ValidationError

from src.schemas.ocsf_schema import OCSFSchema
from src.schemas import ocsf_schema


class TestOCSFSchema:
    """Tests for the OCSF schema handling."""
    
    def test_load_schemas(self, tmp_path):
        """Test loading OCSF schemas from a directory."""
        # Create temporary schema files
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        
        # Create a JSON schema file
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Test JSON Schema",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "integer"}
            }
        }
        
        with open(schema_dir / "test_json.json", "w") as f:
            json.dump(json_schema, f)
        
        # Create a YAML schema file
        yaml_schema = """
        $schema: http://json-schema.org/draft-07/schema#
        type: object
        title: Test YAML Schema
        properties:
          field1:
            type: string
          field2:
            type: integer
        """
        
        with open(schema_dir / "test_yaml.yaml", "w") as f:
            f.write(yaml_schema)
        
        # Create a new OCSF schema instance with the temporary directory
        test_schema = OCSFSchema(schema_path=str(schema_dir), auto_load=False)
        test_schema.load_schemas()
        
        # Verify the schemas were loaded
        assert "test_json" in test_schema.schemas
        assert "test_yaml" in test_schema.schemas
        assert test_schema.schemas["test_json"]["title"] == "Test JSON Schema"
        assert test_schema.schemas["test_yaml"]["title"] == "Test YAML Schema"
    
    def test_validate_event(self, tmp_path):
        """Test validating an event against a schema."""
        # Create a temporary schema file
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        
        event_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Test Event Schema",
            "required": ["class_uid", "time"],
            "properties": {
                "class_uid": {"type": "string"},
                "time": {"type": "string", "format": "date-time"},
                "severity": {"type": "integer", "minimum": 0, "maximum": 10},
                "message": {"type": "string"}
            }
        }
        
        with open(schema_dir / "event.json", "w") as f:
            json.dump(event_schema, f)
        
        # Create a new OCSF schema instance with the temporary directory
        test_schema = OCSFSchema(schema_path=str(schema_dir), auto_load=False)
        test_schema.load_schemas()
        
        # Valid event
        valid_event = {
            "class_uid": "0001",
            "time": "2023-01-01T12:00:00Z",
            "severity": 5,
            "message": "Test event"
        }
        
        # Invalid event (missing required field)
        invalid_event_1 = {
            "severity": 5,
            "message": "Test event"
        }
        
        # Invalid event (invalid severity)
        invalid_event_2 = {
            "class_uid": "0001",
            "time": "2023-01-01T12:00:00Z",
            "severity": 15,
            "message": "Test event"
        }
        
        # Validate events
        assert test_schema.validate_event(valid_event, "event") is True
        assert test_schema.validate_event(invalid_event_1, "event") is False
        assert test_schema.validate_event(invalid_event_2, "event") is False
    
    def test_map_to_ocsf(self):
        """Test mapping events to OCSF format."""
        # Test mapping a syslog event
        syslog_event = {
            "timestamp": "2023-01-01T12:00:00Z",
            "severity": 3,
            "facility": 1,
            "hostname": "test-host",
            "message": "Test syslog message"
        }
        
        ocsf_syslog = ocsf_schema.map_to_ocsf(syslog_event, "syslog")
        
        assert "class_uid" in ocsf_syslog
        assert "category_uid" in ocsf_syslog
        assert ocsf_syslog["time"] == "2023-01-01T12:00:00Z"
        assert ocsf_syslog["message"] == "Test syslog message"
        assert "metadata" in ocsf_syslog
        assert ocsf_syslog["metadata"]["product"]["name"] == "Syslog"
        assert ocsf_syslog["metadata"]["product"]["vendor_name"] == "test-host"
        
        # Test mapping a CEF event
        cef_event = {
            "deviceVendor": "Test Vendor",
            "deviceProduct": "Test Product",
            "deviceVersion": "1.0",
            "deviceEventClassId": "100",
            "name": "Test Event",
            "severity": "5",
            "deviceReceiptTime": "2023-01-01T12:00:00Z",
            "message": "Test CEF message"
        }
        
        ocsf_cef = ocsf_schema.map_to_ocsf(cef_event, "cef")
        
        assert "class_uid" in ocsf_cef
        assert "category_uid" in ocsf_cef
        assert ocsf_cef["time"] == "2023-01-01T12:00:00Z"
        assert ocsf_cef["message"] == "Test CEF message"
        assert "metadata" in ocsf_cef
        assert ocsf_cef["metadata"]["product"]["name"] == "Test Product"
        assert ocsf_cef["metadata"]["product"]["vendor_name"] == "Test Vendor"
        
        # Test mapping a LEEF event
        leef_event = {
            "devname": "Test Device",
            "devtime": "2023-01-01T12:00:00Z",
            "devtype": "Test Type",
            "severity": 5,
            "message": "Test LEEF message"
        }
        
        ocsf_leef = ocsf_schema.map_to_ocsf(leef_event, "leef")
        
        assert "class_uid" in ocsf_leef
        assert "category_uid" in ocsf_leef
        assert ocsf_leef["time"] == "2023-01-01T12:00:00Z"
        assert ocsf_leef["message"] == "Test LEEF message"
        assert "metadata" in ocsf_leef
        assert ocsf_leef["metadata"]["product"]["name"] == "Test Device"
        assert ocsf_leef["metadata"]["product"]["vendor_name"] == "Test Type"
    
    def test_map_syslog_severity(self):
        """Test mapping syslog severity to OCSF severity."""
        # Create a schema instance for testing the static method
        schema = OCSFSchema()
        
        # Test all syslog severity levels
        for syslog_severity in range(8):
            ocsf_severity = schema._map_syslog_severity(syslog_severity)
            assert isinstance(ocsf_severity, int)
            assert 0 <= ocsf_severity <= 10
        
        # Test emergency (0) maps to critical (10)
        assert schema._map_syslog_severity(0) == 10
        
        # Test informational (6) maps to low (4)
        assert schema._map_syslog_severity(6) == 4
        
        # Test debug (7) maps to informational (3)
        assert schema._map_syslog_severity(7) == 3 