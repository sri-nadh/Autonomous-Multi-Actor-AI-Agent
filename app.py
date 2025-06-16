from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime
import json

# Import the multi-agent system
from Multi_Agent import graph, run_agent

app = FastAPI(
    title="Multi-Agent Chatbot API",
    description="A chatbot API powered by specialized AI agents (Web Search, RAG, SQL Query)",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for chat sessions (use a database in production)
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    agents_used: List[str]
    message_id: str

class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

class AgentCapabilities(BaseModel):
    web_search: str = "Search the web for real-time information and current events"
    rag: str = "Retrieve information from your knowledge base and documents"
    sql_query: str = "Execute natural language queries on your database"

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Agent Chatbot API",
        "version": "1.0.0",
        "capabilities": {
            "web_search": "Real-time web search using Tavily",
            "rag": "Document retrieval and Q&A",
            "sql_query": "Natural language to SQL conversion and execution"
        },
        "endpoints": {
            "chat": "/chat",
            "capabilities": "/capabilities",
            "history": "/history/{session_id}",
            "sessions": "/sessions"
        }
    }

@app.get("/capabilities", response_model=AgentCapabilities)
async def get_capabilities():
    """Get information about agent capabilities."""
    return AgentCapabilities()

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Main chat endpoint that processes user messages using the multi-agent system.
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Initialize session if it doesn't exist
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Add user message to session history
        user_message = {
            "id": message_id,
            "role": "user",
            "content": chat_message.message,
            "timestamp": timestamp
        }
        chat_sessions[session_id].append(user_message)
        
        # Process the message through the multi-agent system
        agents_used = []
        response_content = ""
        
        try:
            # Capture the multi-agent system output
            responses = []
            for s in graph.stream(
                {"messages": [("user", chat_message.message)]}, 
                subgraphs=True
            ):
                responses.append(s)
                # Extract agent information from the stream
                if isinstance(s, dict):
                    for key, value in s.items():
                        if key in ["web_researcher", "rag", "nl2sql"] and key not in agents_used:
                            agents_used.append(key)
            
            # Extract the final response from the last agent
            if responses:
                last_response = responses[-1]
                if isinstance(last_response, dict):
                    # Try to extract the content from the last response
                    for key, value in last_response.items():
                        if isinstance(value, dict) and "messages" in value:
                            if value["messages"] and len(value["messages"]) > 0:
                                last_message = value["messages"][-1]
                                if hasattr(last_message, 'content'):
                                    response_content = last_message.content
                                elif isinstance(last_message, dict) and 'content' in last_message:
                                    response_content = last_message['content']
            
            # Fallback: if no content extracted, provide a general response
            if not response_content:
                response_content = "I've processed your request using my specialized agents. How else can I help you?"
                
        except Exception as e:
            response_content = f"I encountered an issue while processing your request: {str(e)}. Please try again."
            print(f"Error in multi-agent processing: {str(e)}")
        
        # Add assistant response to session history
        assistant_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat(),
            "agents_used": agents_used
        }
        chat_sessions[session_id].append(assistant_message)
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            timestamp=timestamp,
            agents_used=agents_used,
            message_id=message_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """Get chat history for a specific session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ChatHistory(
        session_id=session_id,
        messages=chat_sessions[session_id]
    )

@app.get("/sessions")
async def get_sessions():
    """Get all active chat sessions."""
    sessions = []
    for session_id, messages in chat_sessions.items():
        if messages:
            sessions.append({
                "session_id": session_id,
                "last_message": messages[-1]["timestamp"],
                "message_count": len(messages)
            })
    return {"sessions": sessions}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del chat_sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 