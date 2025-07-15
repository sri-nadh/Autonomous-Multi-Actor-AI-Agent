# Multi-Actor AI Agent System

An autonomous multi-actor AI agent system built with LangGraph that coordinates three specialized agents. Now includes a FastAPI server for easy frontend integration and chatbot functionality.

## 🤖 Agents

1. **Web Search Agent** - Uses Tavily Search for real-time web information
2. **RAG Agent** - Retrieval Augmented Generation using ChromaDB and Sentence Transformers
3. **NL2SQL Agent** - Natural Language to SQL queries using the Chinook database

## 🚀 Setup

### 1. Install Dependencies

**For Core System:**
```bash
pip install -r requirements.txt
```

**For FastAPI Server (Optional):**
```bash
pip install fastapi uvicorn pydantic python-multipart
```

### 2. Environment Variables

Create a `.env` file in the project root and add your API keys:

```bash
# OpenAI API Key (required for all agents)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Key (required for web search agent)
TAVILY_API_KEY=your_tavily_api_key_here

```

Required API keys:
- `OPENAI_API_KEY` - Get from [OpenAI](https://platform.openai.com/api-keys)
- `TAVILY_API_KEY` - Get from [Tavily](https://tavily.com/)

### 3. Set up Document Storage (Optional)

For the RAG agent to work with your documents:

1. Create a `docs` folder in the project directory
2. Add PDF or DOCX files to the `docs` folder
3. The system will automatically process and index these documents

### 4. Database Setup

The Chinook SQLite database will be automatically downloaded when you first run the SQL agent. No manual setup required.

## 📁 Project Structure

```
Multi-Actor-AI-Agent/
├── Multi_Agent.py          # Main orchestrator with StateGraph
├── SQL_Query_Agent.py      # NL2SQL agent
├── RAG_Agent.py           # Document retrieval agent
├── WebSearch_Agent.py     # Web search agent
├── app.py                 # FastAPI server for chatbot interface
├── index.html             # Web frontend interface
├── styles.css             # Frontend styling
├── script.js              # Frontend JavaScript
├── requirements.txt       # Core system dependencies
├── README.md             # This file
├── docs/                 # Place your documents here (auto-created)
├── chroma_db/           # Vector database (auto-created)
└── Chinook.db          # SQLite database (auto-downloaded)
```

## 🎯 Usage

### Option 1: Direct Python Usage

```python
from Multi_Agent import run_agent

# Ask a question that might require multiple agents
question = "Find information about Tesla's latest earnings and compare it with data from our documents"
run_agent(question)
```

**Running Directly:**
```bash
python Multi_Agent.py
```

### Option 2: FastAPI Chatbot Server

**Start the server:**
```bash
python app.py
```

The server will start on `http://localhost:8000`

**API Endpoints:**
- **POST** `/chat` - Main chatbot endpoint
- **GET** `/` - API information
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/capabilities` - Agent capabilities
- **GET** `/history/{session_id}` - Chat history
- **GET** `/sessions` - List active sessions
- **DELETE** `/sessions/{session_id}` - Delete session

### Option 3: Web Frontend

A modern web interface is included for easy interaction:

**To use the frontend:**
1. Start the FastAPI server: `python app.py`
2. Open `index.html` in your browser or serve it locally:
   ```bash
   python -m http.server 3000
   ```
3. Chat with your AI agents through the beautiful web interface

**Frontend Features:**
- Modern, responsive design with agent status indicators
- Real-time chat with typing animations
- Visual feedback showing which agents are active
- Session management and chat history
- Mobile-friendly interface


### Example Queries

- **Web Search**: "What are the latest developments in AI?"
- **RAG**: "What does our company document say about the founder?"
- **SQL**: "Show me the top 5 customers by total purchase amount"
- **Multi-Agent**: "Research the current stock price of Apple and find any mentions in our documents"

### FastAPI Usage Examples

**Using curl:**
```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are the latest AI developments?"}'

# Check agent capabilities
curl http://localhost:8000/capabilities
```

**Using Python requests:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Find Tesla's latest earnings"}
)
print(response.json())
```

## 🛠 Features

### FastAPI Integration
- **RESTful API**: Clean REST endpoints for chatbot functionality
- **Session Management**: Persistent chat sessions with automatic UUID generation
- **CORS Enabled**: Ready for frontend integration
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
- **Agent Transparency**: Response includes which agents were used
- **Error Handling**: Graceful API error responses

### Error Handling
- Graceful fallbacks when services are unavailable
- Automatic database download for SQL agent
- Document folder auto-creation for RAG agent

### Modern Architecture
- Updated to latest LangGraph patterns with Command-based routing
- Structured output routing
- Parallel tool execution
- Comprehensive error handling
- Modular agent design

### Enhanced SQL Agent
- **Query Explanation**: Human-readable explanations of SQL queries before execution
- **Smart Caching**: 24-hour query result caching for improved performance and reduced API costs
- **Automatic Query Cleaning**: Removes code blocks and formatting artifacts
- **Result Formatting**: Clear presentation of query results with explanations

### Flexibility
- Easy to add new agents
- Configurable model selection
- Customizable routing logic
- Separated agent files for better maintainability

## 🔧 Agent Architecture

Each agent is implemented as a separate module:

### WebSearch_Agent.py
- Handles real-time web searches using Tavily
- Returns formatted search results with titles, content, and URLs
- Includes error handling for missing API keys

### RAG_Agent.py
- Document loading from PDF and DOCX files
- Vector storage using ChromaDB and Sentence Transformers (Model : multi-qa-mpnet-base-dot-v1)
- Semantic similarity search for document retrieval

### SQL_Query_Agent.py
- Natural language to SQL query conversion
- Automatic Chinook database setup
- SQL query cleaning and execution
- **NEW**: Query explanation with human-readable descriptions
- **NEW**: Intelligent caching system with 24-hour expiration
- Persistent cache storage in JSON format

### Multi_Agent.py
- Supervisor-based routing using Command pattern
- Dynamic agent selection based on query type
- State management across agent interactions

### app.py (FastAPI Server)
- **Chat API**: RESTful endpoints for chatbot interactions
- **Session Management**: Maintains conversation context across requests
- **Agent Integration**: Seamlessly wraps the multi-agent system
- **Frontend Ready**: CORS enabled with JSON responses
- **Documentation**: Auto-generated API docs

## 🧪 Testing

**Core System Testing:**
- Individual agent functionality tests
- Integration testing of the complete system
- API key validation
- Error handling verification

**FastAPI Testing:**
- Visit `http://localhost:8000/docs` for interactive API testing
- Use the provided curl commands or Python examples
- Test endpoints with different query types to see agent routing

## 🤝 Contributing

Feel free to submit issues, feature requests, and pull requests to improve the system.

## 📄 License

This project is open-source and available under the MIT License. 