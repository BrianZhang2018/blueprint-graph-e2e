"""
Database connection module for Neo4j.
"""
from neo4j import GraphDatabase
from py2neo import Graph
from .config import settings
from .logging import log


class Neo4jConnection:
    """
    Neo4j database connection manager.
    
    This class provides methods for connecting to Neo4j and executing queries.
    It supports both the official Neo4j Python driver and py2neo for different use cases.
    """
    
    def __init__(self, auto_connect=True):
        """Initialize the Neo4j connection."""
        self._driver = None
        self._graph = None
        if auto_connect:
            try:
                self._connect()
            except Exception as e:
                log.error(f"Failed to connect to Neo4j during initialization: {str(e)}")
    
    def _connect(self):
        """Establish connection to Neo4j database."""
        try:
            # Print connection details for debugging
            log.info(f"Connecting to Neo4j with URI: {settings.neo4j_uri}, User: {settings.neo4j_user}")
            
            # Connect using the official Neo4j Python driver
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            
            # Test the connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise ValueError("Connection test failed")
            
            # Connect using py2neo for higher-level operations
            self._graph = Graph(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            
            log.info("Successfully connected to Neo4j database")
        except Exception as e:
            log.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
        self._graph = None
        log.info("Neo4j connection closed")
    
    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query using the official driver.
        
        Args:
            query (str): The Cypher query to execute
            parameters (dict, optional): Query parameters
            
        Returns:
            list: Query results
        """
        if not self._driver:
            self._connect()
        
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            log.error(f"Query execution failed: {str(e)}")
            log.error(f"Query: {query}")
            log.error(f"Parameters: {parameters}")
            raise
    
    def execute_write_transaction(self, func, *args, **kwargs):
        """
        Execute a write transaction function.
        
        Args:
            func (callable): Function to execute within transaction
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Any: Result of the transaction function
        """
        if not self._driver:
            self._connect()
        
        with self._driver.session() as session:
            return session.execute_write(func, *args, **kwargs)
    
    def execute_read_transaction(self, func, *args, **kwargs):
        """
        Execute a read transaction function.
        
        Args:
            func (callable): Function to execute within transaction
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Any: Result of the transaction function
        """
        if not self._driver:
            self._connect()
        
        with self._driver.session() as session:
            return session.execute_read(func, *args, **kwargs)
    
    @property
    def graph(self):
        """
        Get the py2neo Graph object.
        
        Returns:
            Graph: py2neo Graph object
        """
        if not self._graph:
            self._connect()
        return self._graph


# Create a global database connection instance
db = Neo4jConnection(auto_connect=True) 