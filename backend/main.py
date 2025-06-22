from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langchain.agents import initialize_agent
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from functools import partial
import tiktoken
from langchain.tools import BaseTool
from pydantic import Field

from datetime import datetime
from uuid import uuid4

from memory.redis_memory import RedisConversationBufferMemory
from utils.structured_output import parse_response, format_response_for_display

app = FastAPI()

# Load environment variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Initialize LLM
llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=0.7,
    max_tokens=1000,
    api_key=ANTHROPIC_API_KEY,
    streaming=True,
    verbose=True
)

# Create memory
memory = RedisConversationBufferMemory(
    session_id=str(uuid4()),
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    redis_password=REDIS_PASSWORD,
    memory_key="chat_history",
)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""You are a helpful AI assistant.

    {history}
    Human: {input}
    Assistant:"""
)

# Create a simple dummy tool for testing
class DummyTool(BaseTool):
    name: str = Field(default="dummy")
    description: str = Field(default="A dummy tool that always returns the input")

    def _run(self, query: str) -> str:
        return query

    async def _arun(self, query: str) -> str:
        return query

def count_tokens(text: str) -> int:
    """Counts the number of tokens in a given text."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

# Initialize agent with dummy tool
agent = initialize_agent(
    tools=[DummyTool()],
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True,
    handle_parsing_errors=True
)

@app.get("/")
async def root():
    return {"message": "LangGraph Agent API is running"}

@app.post("/chat")
async def chat(request: dict):
    try:
        message = request["message"]
        if message is None or message == "":
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Input message cannot be empty.",
                    "type": "input_error",
                    "message": "The message cannot be empty."
                }
            )
        num_tokens = count_tokens(message)
        if num_tokens > llm.max_tokens:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Input message exceeds the maximum token limit.",
                    "type": "token_limit_error",
                    "message": f"The message contains {num_tokens} tokens, but the maximum allowed is {llm.max_tokens}."
                }
            )

        # Get raw response from agent
        raw_response = agent.run(input=message)
        
        # Parse the response
        parsed_response = parse_response(raw_response)
        
        # Format for display
        display_response = format_response_for_display(parsed_response)
        
        return {
            "raw": raw_response,
            "parsed": parsed_response,
            "display": display_response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": "agent_error",
                "message": "Failed to process request"
            }
        )

@app.post("/clear")
async def clear_conversation():
    """Clear the conversation history."""
    try:
        memory.clear()
        return {"message": "Conversation cleared successfully"}
    except Exception as e:
        raise e

@app.get("/status")
async def get_status():
    """Get API status and configuration."""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "llm_model": "claude-2",
        "memory_type": "redis",
        "session_id": memory.session_id,
        "system_prompt": prompt.template,
        "llm_settings": {
            "model": llm.model,
            "temperature": llm.temperature,
            "max_tokens": llm.max_tokens
        }
    }
