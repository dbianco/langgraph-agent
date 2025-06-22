from typing import Dict, Any, Optional, List
import json
from pydantic import BaseModel, ValidationError
from langchain.schema import BaseMessage, AIMessage

class StructuredResponse(BaseModel):
    """Base model for structured responses."""
    type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ToolCall(BaseModel):
    """Model for tool calls in responses."""
    name: str
    parameters: Dict[str, Any]

class ActionResponse(StructuredResponse):
    """Model for responses that include actions."""
    actions: List[Dict[str, Any]]
    result: Optional[str] = None

class ErrorResponse(StructuredResponse):
    """Model for error responses."""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None

class InfoResponse(StructuredResponse):
    """Model for informational responses."""
    info_type: str
    data: Dict[str, Any]

def parse_response(response: str) -> Dict[str, Any]:
    """
    Parse the agent's response into a structured format.
    
    Args:
        response: The raw response string from the agent
        
    Returns:
        A dictionary containing the parsed response
    """
    try:
        # First try to parse as JSON
        parsed = json.loads(response)
        
        # Try to determine the type of response
        if isinstance(parsed, dict):
            if "error" in parsed:
                return ErrorResponse(
                    type="error",
                    content=parsed.get("error", ""),
                    error_type=parsed.get("error_type", "unknown"),
                    message=parsed.get("message", ""),
                    details=parsed.get("details")
                ).dict()
            
            if "actions" in parsed:
                return ActionResponse(
                    type="action",
                    content=parsed.get("content", ""),
                    actions=parsed["actions"],
                    result=parsed.get("result")
                ).dict()
                
            if "info_type" in parsed:
                return InfoResponse(
                    type="info",
                    content=parsed.get("content", ""),
                    info_type=parsed["info_type"],
                    data=parsed.get("data", {})
                ).dict()
                
            # Default case
            return StructuredResponse(
                type="text",
                content=response
            ).dict()
            
    except (json.JSONDecodeError, ValidationError):
        # If JSON parsing fails, treat as plain text
        return StructuredResponse(
            type="text",
            content=response
        ).dict()

def format_response_for_display(response: Dict[str, Any]) -> str:
    """
    Format the structured response for display in the chat interface.
    
    Args:
        response: The parsed response dictionary
        
    Returns:
        A formatted string suitable for display
    """
    response_type = response.get("type", "text")
    
    if response_type == "error":
        return f"⚠️ Error: {response.get('message', '')}"
    
    if response_type == "action":
        actions = response.get("actions", [])
        action_text = "\n".join([
            f"- {action.get('name', '')}: {action.get('parameters', {})}"
            for action in actions
        ])
        return f"💡 Actions:\n{action_text}"
    
    if response_type == "info":
        return f"ℹ️ {response.get('content', '')}"
    
    # Default case for text responses
    return response.get("content", "")
