"""
Configuration module for the application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Neo4j Configuration
    neo4j_uri: str = Field(..., env="NEO4J_URI")
    neo4j_user: str = Field(..., env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_debug: bool = Field(False, env="API_DEBUG")
    api_log_level: str = Field("INFO", env="API_LOG_LEVEL")
    
    # Pipeline Configuration
    kafka_bootstrap_servers: Optional[str] = Field(None, env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic_input: Optional[str] = Field("security-events", env="KAFKA_TOPIC_INPUT")
    kafka_consumer_group: Optional[str] = Field("blueprintgraph-consumer", env="KAFKA_CONSUMER_GROUP")
    use_kafka: bool = Field(False, env="USE_KAFKA")
    
    # OCSF Configuration
    ocsf_schema_version: str = Field("1.0.0", env="OCSF_SCHEMA_VERSION")
    ocsf_schema_path: str = Field("src/schemas/ocsf", env="OCSF_SCHEMA_PATH")
    
    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    environment: str = Field("production", env="ENVIRONMENT")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a global settings instance
settings = Settings() 