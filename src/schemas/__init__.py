"""
Schema modules for the application.
"""
from .ocsf_schema import OCSFSchema

# Create a singleton instance of the OCSFSchema class
ocsf_schema = OCSFSchema()

__all__ = ["ocsf_schema", "OCSFSchema"] 