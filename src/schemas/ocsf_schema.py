"""
OCSF Schema handling module.

This module provides utilities for working with the Open Cybersecurity Schema Framework (OCSF).
"""
import os
import json
import yaml
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError
from src.utils import settings, log


class OCSFSchema:
    """
    OCSF Schema manager.
    
    This class provides methods for loading, validating, and working with OCSF schemas.
    """
    
    def __init__(self, schema_path=None, schema_version=None, auto_load=True):
        """
        Initialize the OCSF Schema manager.
        
        Args:
            schema_path (str, optional): Path to schema directory. Defaults to settings.ocsf_schema_path.
            schema_version (str, optional): Schema version. Defaults to settings.ocsf_schema_version.
            auto_load (bool, optional): Whether to load schemas automatically. Defaults to True.
        """
        self.schema_path = schema_path or settings.ocsf_schema_path
        self.schema_version = schema_version or settings.ocsf_schema_version
        self.schemas = {}
        if auto_load:
            self.load_schemas()
    
    def load_schemas(self):
        """Load all OCSF schemas from the schema directory."""
        try:
            if not os.path.exists(self.schema_path):
                log.warning(f"OCSF schema path does not exist: {self.schema_path}")
                return
            
            # Load all schema files
            for root, _, files in os.walk(self.schema_path):
                for file in files:
                    if file.endswith(('.json', '.yaml', '.yml')):
                        file_path = os.path.join(root, file)
                        schema_name = os.path.splitext(file)[0]
                        
                        try:
                            if file.endswith('.json'):
                                with open(file_path, 'r') as f:
                                    schema = json.load(f)
                            else:
                                with open(file_path, 'r') as f:
                                    schema = yaml.safe_load(f)
                            
                            self.schemas[schema_name] = schema
                            log.debug(f"Loaded OCSF schema: {schema_name}")
                        except Exception as e:
                            log.error(f"Failed to load schema {file_path}: {str(e)}")
            
            log.info(f"Loaded {len(self.schemas)} OCSF schemas")
        except Exception as e:
            log.error(f"Failed to load OCSF schemas: {str(e)}")
    
    def validate_event(self, event: Dict[str, Any], schema_type: str) -> bool:
        """
        Validate an event against an OCSF schema.
        
        Args:
            event (dict): The event to validate
            schema_type (str): The schema type to validate against
            
        Returns:
            bool: True if valid, False otherwise
        """
        if schema_type not in self.schemas:
            log.error(f"Schema type not found: {schema_type}")
            return False
        
        try:
            validate(instance=event, schema=self.schemas[schema_type])
            return True
        except ValidationError as e:
            log.error(f"Event validation failed: {str(e)}")
            return False
    
    def map_to_ocsf(self, event: Dict[str, Any], source_format: str) -> Dict[str, Any]:
        """
        Map an event from a source format to OCSF.
        
        Args:
            event (dict): The event to map
            source_format (str): The source format (e.g., 'syslog', 'cef', 'leef')
            
        Returns:
            dict: The mapped OCSF event
        """
        # This is a placeholder for actual mapping logic
        # In a real implementation, this would use mapping rules specific to the source format
        
        if source_format == 'syslog':
            return self._map_syslog_to_ocsf(event)
        elif source_format == 'cef':
            return self._map_cef_to_ocsf(event)
        elif source_format == 'leef':
            return self._map_leef_to_ocsf(event)
        else:
            log.warning(f"Unsupported source format: {source_format}")
            return event
    
    def _map_syslog_to_ocsf(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Map a syslog event to OCSF."""
        # Placeholder for syslog mapping logic
        ocsf_event = {
            "class_uid": "0001",  # Example class UID
            "category_uid": "0002",  # Example category UID
            "time": event.get("timestamp"),
            "severity": self._map_syslog_severity(event.get("severity", 0)),
            "message": event.get("message", ""),
            "metadata": {
                "version": self.schema_version,
                "product": {
                    "name": "Syslog",
                    "vendor_name": event.get("hostname", "Unknown")
                }
            }
        }
        return ocsf_event
    
    def _map_cef_to_ocsf(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Map a CEF event to OCSF."""
        # Placeholder for CEF mapping logic
        ocsf_event = {
            "class_uid": "0001",  # Example class UID
            "category_uid": "0002",  # Example category UID
            "time": event.get("deviceReceiptTime"),
            "severity": event.get("severity", 0),
            "message": event.get("message", ""),
            "metadata": {
                "version": self.schema_version,
                "product": {
                    "name": event.get("deviceProduct", "Unknown"),
                    "vendor_name": event.get("deviceVendor", "Unknown")
                }
            }
        }
        return ocsf_event
    
    def _map_leef_to_ocsf(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Map a LEEF event to OCSF."""
        # Placeholder for LEEF mapping logic
        ocsf_event = {
            "class_uid": "0001",  # Example class UID
            "category_uid": "0002",  # Example category UID
            "time": event.get("devtime"),  # Changed from devTime to devtime
            "severity": event.get("severity", 0),
            "message": event.get("message", ""),
            "metadata": {
                "version": self.schema_version,
                "product": {
                    "name": event.get("devname", "Unknown"),
                    "vendor_name": event.get("devtype", "Unknown")
                }
            }
        }
        return ocsf_event
    
    def _map_syslog_severity(self, severity: int) -> int:
        """Map syslog severity to OCSF severity."""
        # Syslog severity is 0-7, OCSF might use a different scale
        # This is a placeholder mapping
        syslog_to_ocsf = {
            0: 10,  # Emergency -> Critical
            1: 9,   # Alert -> High
            2: 8,   # Critical -> High
            3: 7,   # Error -> Medium
            4: 6,   # Warning -> Medium
            5: 5,   # Notice -> Low
            6: 4,   # Informational -> Low
            7: 3,   # Debug -> Informational
        }
        return syslog_to_ocsf.get(severity, 5)  # Default to Low if unknown


# Create a global OCSF schema instance
ocsf_schema = OCSFSchema() 