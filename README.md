# Multi-Actor AI Agent System

An autonomous multi-actor AI agent system built with LangGraph that coordinates three specialized agents:

## 🤖 Agents

1. **Web Search Agent** - Uses Tavily Search for real-time web information
2. **RAG Agent** - Retrieval Augmented Generation using ChromaDB and Sentence Transformers
3. **NL2SQL Agent** - Natural Language to SQL queries using the Chinook database

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root and add your API keys:

```bash
# OpenAI API Key (required for all agents)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily API Key (required for web search agent)
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Custom model names
OPENAI_MODEL=gpt-4o

# Optional: Custom paths
DOCS_FOLDER=./docs
CHROMA_DB_PATH=./chroma_db
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
├── test_agents.py         # Testing script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── docs/                 # Place your documents here (auto-created)
├── chroma_db/           # Vector database (auto-created)
└── Chinook.db          # SQLite database (auto-downloaded)
```

## 🎯 Usage

### Basic Usage

```python
from Multi_Agent import run_agent

# Ask a question that might require multiple agents
question = "Find information about Tesla's latest earnings and compare it with data from our documents"
run_agent(question)
```

### Running Directly

```bash
python Multi_Agent.py
```

### Testing the System

Run the test script to verify all agents are working:

```bash
python test_agents.py
```

### Example Queries

- **Web Search**: "What are the latest developments in AI?"
- **RAG**: "What does our company document say about the founder?"
- **SQL**: "Show me the top 5 customers by total purchase amount"
- **Multi-Agent**: "Research the current stock price of Apple and find any mentions in our documents"

## 🛠 Features

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
- Vector storage using ChromaDB and Sentence Transformers
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

## 🧪 Testing

The `test_agents.py` script provides comprehensive testing:

- Individual agent functionality tests
- Integration testing of the complete system
- API key validation
- Error handling verification

## 🤝 Contributing

Feel free to submit issues, feature requests, and pull requests to improve the system.

## 📄 License

This project is open-source and available under the MIT License. 