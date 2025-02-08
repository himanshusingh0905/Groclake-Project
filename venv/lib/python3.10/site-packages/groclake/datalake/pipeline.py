# pipeline.py

from .connection import SQLConnection, RedisConnection, ESConnection, GCPConnection, S3Connection, MongoDBConnection
import threading

class Pipeline:
    def __init__(self, name):
        self.name = name
        self.connections = {}

    def add_connection(self, name, config):
        """
        Adds a connection to the pipeline using the configuration provided.
        The connection type is extracted from the 'connection_type' key in the config.
        """
        if name in self.connections:
            raise ValueError(f"Connection name '{name}' already exists in pipeline '{self.name}'.")

        # Extract connection_type from config
        connection_type = config.pop("connection_type", None)
        if not connection_type:
            raise ValueError(f"'connection_type' must be specified in the configuration for connection '{name}'.")

        # Create connection based on type
        if connection_type.lower() == "sql":
            connection = SQLConnection(config)
        elif connection_type.lower() == "redis":
            connection = RedisConnection(config)
        elif connection_type.lower() == "es":
            connection = ESConnection(config["host"], config["port"])
        elif connection_type == "gcp_storage":
            connection = GCPConnection(config)
        elif connection_type == "aws_s3":
            connection = S3Connection(config)
        elif connection_type == "mongo":
            connection = MongoDBConnection(config)
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")

        # Store connection
        self.connections[name] = connection

    def get_connection_by_name(self, name):
        return self.connections.get(name)

    def execute(self):
        threads = []
        for connection in self.connections.values():
            thread = threading.Thread(target=connection.connect)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
