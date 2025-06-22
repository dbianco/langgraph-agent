from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import redis
from typing import List, Optional, Any
import json
from datetime import datetime
from pydantic import PrivateAttr, ConfigDict

class RedisChatMemory:
    def __init__(self, redis_client: redis.Redis, session_id: str):
        self.redis_client = redis_client
        self.session_id = session_id
        self.memory_key = f"chat_history:{session_id}"
        
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the Redis store."""
        message_data = {
            'role': message.type,
            'content': message.content,
            'created_at': datetime.now().isoformat()
        }
        
        # Store message with timestamp as key
        timestamp = datetime.now().isoformat()
        self.redis_client.hset(self.memory_key, timestamp, json.dumps(message_data))
        
        # Keep only last 10 messages
        messages = self.redis_client.hgetall(self.memory_key)
        if len(messages) > 10:
            # Get all keys and sort by timestamp
            keys = list(messages.keys())
            keys.sort()
            # Remove oldest messages
            for key in keys[:-10]:
                self.redis_client.hdel(self.memory_key, key)

    def get_messages(self) -> List[BaseMessage]:
        """Retrieve messages from Redis."""
        messages = self.redis_client.hgetall(self.memory_key)
        if not messages:
            return []
            
        # Convert Redis messages back to BaseMessage objects
        message_list = []
        for timestamp, message_json in messages.items():
            message_data = json.loads(message_json)
            if message_data['role'] == 'human':
                message_list.append(HumanMessage(content=message_data['content']))
            else:
                message_list.append(AIMessage(content=message_data['content']))
                
        # Sort messages by timestamp
        message_list.sort(key=lambda x: x.additional_kwargs.get('created_at', ''))
        return message_list

    def clear(self) -> None:
        """Clear all messages from Redis."""
        self.redis_client.delete(self.memory_key)

class RedisConversationBufferMemory(ConversationBufferMemory):
    model_config = ConfigDict(extra='allow')
    _redis_client: redis.Redis = PrivateAttr()
    
    def __init__(self, session_id: str, **kwargs):
        redis_client = redis.Redis(
            host=kwargs.get('redis_host', 'localhost'),
            port=kwargs.get('redis_port', 6379),
            password=kwargs.get('redis_password', None)
        )
        super().__init__(**kwargs)
        self._redis_client = redis_client
        self.session_id = session_id
        self.redis_memory = RedisChatMemory(self._redis_client, session_id)

    def save_context(self, inputs: dict, outputs: dict) -> None:
        """Save context from a conversation to buffer."""
        human_message = HumanMessage(content=inputs["input"])
        ai_message = AIMessage(content=outputs.get("response", "No response"))
        
        self.redis_memory.add_message(human_message)
        self.redis_memory.add_message(ai_message)

    def load_memory_variables(self, inputs: dict) -> dict:
        """Return history."""
        messages = self.redis_memory.get_messages()
        history = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                history += f"Human: {message.content}\n"
            else:
                history += f"AI: {message.content}\n"
        return {"history": history}

    def clear(self) -> None:
        """Clear session history."""
        self.redis_memory.clear()
