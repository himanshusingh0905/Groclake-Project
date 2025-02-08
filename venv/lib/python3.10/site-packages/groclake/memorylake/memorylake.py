import base64
from dotenv import load_dotenv
import os
from groclake.datalake import Datalake

load_dotenv()

class Config:
    # Redis Configuration
    REDIS_CONFIG = {
        "host": os.getenv("REDIS_HOST", "localhost"),  # Default to localhost if not set
        "port": int(os.getenv("REDIS_PORT", 6379)),  # Default to 6379 if not set
    }

class Memorylake(Datalake):
    def __init__(self):
        super().__init__()

        # Define the configuration for Redis connection
        REDIS_CONFIG = Config.REDIS_CONFIG
        REDIS_CONFIG['connection_type'] = 'redis'

        # Create and add Redis connection to the pipeline
        self.test_pipeline = self.create_pipeline(name="redis_pipeline")
        self.test_pipeline.add_connection(name="redis_connection", config=REDIS_CONFIG)

        # Execute all connections at once
        self.execute_all()

        # Initialize Redis connection
        self.connections = {
            "redis_connection": self.get_connection("redis_connection"),
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.test_pipeline.get_connection_by_name(connection_name)

    @staticmethod
    def generate_key(user_uuid, context_entity_id, context_id, memory_id):
        """Generates a unique key by concatenating user_uuid, context_entity_id, context_id, and memory_id."""
        return f"{user_uuid}:{context_entity_id}:{context_id}:{memory_id}"

    def short_memory_create(self, user_uuid, memory_context, memory):
        """Creates or updates a key-value pair in Redis."""
        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'], 
            memory_context['context_id'], 
            memory_context['memory_id']
        )

        value = {
            "query_text": memory['query_text'],
            "response_text": memory['response_text'],
            "entities": [
                {
                    "time": memory['time'], 
                    "memory_id": memory_context['memory_id'], 
                    "context_id": memory_context['context_id'],
                    "memory_quality": 1  # Default memory quality
                }
            ],
            "metadata": {"context_entity_id": memory_context['context_entity_id'], "user_uuid": user_uuid}
        }

        ttl = memory.get('cache_ttl', 3600)
        connection = self.connections.get("redis_connection")
        if connection:
            connection.set(key, str(value), ttl)  # Store as string to ensure compatibility with Redis
            return f"Key '{key}' created/updated with value '{value}' and TTL {ttl}s."
        else:
            raise ConnectionError("Redis connection is not available.")

    def short_memory_read(self, user_uuid, memory_context):
        """Reads a value from Redis or performs wildcard searches based on input parameters."""
        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        context_entity_id = memory_context['context_entity_id']
        context_id = memory_context.get('context_id')
        memory_id = memory_context.get('memory_id')

        if context_id is None and memory_id is None:
            pattern = f"{user_uuid}-{context_entity_id}-*-*"
        elif memory_id is None:
            pattern = f"{user_uuid}-{context_entity_id}-{context_id}-*"
        else:
            key = self.generate_key(user_uuid, context_entity_id, context_id, memory_id)
            value = connection.get(key)
            if value:
                return eval(value)
            else:
                return f"Key '{key}' not found."

        cursor = 0
        matching_keys = []
        while True:
            cursor, keys = connection.connection.scan(cursor=cursor, match=pattern)
            matching_keys.extend(keys)
            if cursor == 0:
                break

        results = {}
        for key in matching_keys:
            value = connection.connection.get(key)
            if value:
                results[key.decode('utf-8')] = eval(value)

        return results

    def short_memory_update_quality(self, user_uuid, memory_context, quality):
        """Updates the quality of a memory in Redis."""
        key = self.generate_key(
            user_uuid,
            memory_context['context_entity_id'],
            memory_context['context_id'],
            memory_context['memory_id']
        )

        connection = self.connections.get("redis_connection")
        if not connection:
            raise ConnectionError("Redis connection is not available.")

        value = connection.get(key)
        if not value:
            return f"Memory '{key}' not found."

        memory_data = eval(value)

        # Update memory quality inside the entities list
        for entity in memory_data["entities"]:
            if entity["memory_id"] == memory_context["memory_id"] and entity["context_id"] == memory_context["context_id"]:
                entity["memory_quality"] = quality
                break

        # Update memory in Redis
        ttl = memory_data.get('cache_ttl', 3600)
        connection.set(key, str(memory_data), ttl)
        return f"Memory quality for key '{key}' updated to '{quality}'."

    def short_memory_update(self, user_uuid, memory_context, memory):
        """Updates a key-value pair in Redis."""
        return self.short_memory_create(user_uuid, memory_context, memory)