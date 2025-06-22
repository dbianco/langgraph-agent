import pytest
import os
import sys
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Import main after setting env variables
from main import app
from utils.structured_output import parse_response

# Load environment variables from .env.example
load_dotenv("../.env.example")

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "LangGraph Agent API is running"}

def test_chat_endpoint(client):
    """Test the chat endpoint with a simple message."""
    response = client.post("/chat", json={"message": "Hola, ¿cómo estás?"})
    assert response.status_code == 200
    data = response.json()
    assert "raw" in data
    assert "parsed" in data
    assert "display" in data
    
    # Verify parsed response structure
    parsed = data["parsed"]
    assert "type" in parsed
    assert "content" in parsed

def test_clear_conversation(client):
    """Test clearing the conversation."""
    response = client.post("/clear")
    assert response.status_code == 200
    assert response.json() == {"message": "Conversation cleared successfully"}

def test_status_endpoint(client):
    """Test the status endpoint."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "llm_model" in data
    assert "memory_type" in data
    assert "session_id" in data
    assert "system_prompt" in data
    assert "llm_settings" in data
    
    llm_settings = data["llm_settings"]
    assert "model" in llm_settings
    assert "temperature" in llm_settings
    assert "max_tokens" in llm_settings

def test_error_handling(client):
    """Test error handling with invalid input."""
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    assert "error" in error_data["detail"]
    assert "type" in error_data["detail"]
    assert "message" in error_data["detail"]

def test_structured_output():
    """Test structured output parsing."""
    # Test error response
    error_response = parse_response('{"error": "test error"}')
    assert error_response["type"] == "error"
    assert error_response["content"] == "test error"
    
    # Test action response
    action_response = parse_response('{"actions": [{"name": "test", "parameters": {}}]}')
    assert action_response["type"] == "action"
    assert action_response["actions"] == [{"name": "test", "parameters": {}}]
    
    # Test info response
    info_response = parse_response('{"info_type": "test", "data": {}}')
    assert info_response["type"] == "info"
    assert info_response["info_type"] == "test"
    assert info_response["data"] == {}

def test_format_response():
    """Test response formatting for display."""
    from utils.structured_output import format_response_for_display
    
    # Test error format
    error_response = {
        "type": "error",
        "error_type": "test",
        "message": "test error"
    }
    assert format_response_for_display(error_response).startswith("⚠️ Error:")
    
    # Test action format
    action_response = {
        "type": "action",
        "actions": [{"name": "test", "parameters": {"value": 1}}]
    }
    assert format_response_for_display(action_response).startswith("💡 Actions:")
    
    # Test info format
    info_response = {
        "type": "info",
        "info_type": "test",
        "data": {"key": "value"}
    }
    assert format_response_for_display(info_response).startswith("ℹ️")
