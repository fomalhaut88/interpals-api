import redis
import json
from typing import Optional, Any


class RedisClient:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
            self.client.ping()
            print("Connected to Redis successfully.")
        except redis.RedisError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Stores a key-value pair in Redis. Optionally set an expiration time (in seconds).
        Value will be stored as a JSON string.
        """
        try:
            json_value = json.dumps(value)
            self.client.set(name=key, value=json_value, ex=expire)
            return True
        except redis.RedisError as e:
            print(f"faled to set key in redis: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value by key from Redis. Returns the parsed JSON object or None if not found.
        """
        try:
            value = self.client.get(name=key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"failed to get key from redis: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete value of key from redis.
        """
        try:
            self.client.delete(*key)
            return True
        except redis.RedisError as e:
            print(f"failed to delete key from redis: {e}")
            return False

