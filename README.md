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

Copy `env_example.txt` to `.env` and fill in your API keys:

```bash
cp env_example.txt .env
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
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables template
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
- Updated to latest LangGraph patterns
- Structured output routing
- Parallel tool execution
- Comprehensive error handling

### Flexibility
- Easy to add new agents
- Configurable model selection
- Customizable routing logic

## 🔧 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are installed with `pip install -r requirements.txt`

2. **API Key Errors**: Ensure your `.env` file has valid API keys

3. **Web Search Not Working**: Check that `TAVILY_API_KEY` is set correctly

4. **RAG Agent No Results**: Add documents to the `docs` folder and restart

5. **SQL Agent Errors**: The Chinook database should download automatically. If not, manually download from the Chinook database repository.

### Debug Mode

For detailed logging, you can modify the print statements in each agent file or add:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Customization

### Adding New Agents

1. Create a new agent file (e.g., `New_Agent.py`)
2. Define a tool using the `@tool` decorator
3. Add the agent to `Multi_Agent.py`:
   - Import the tool
   - Add to `members` list
   - Create agent node function
   - Update routing logic

### Modifying Routing Logic

Edit the `route_after_supervisor` function in `Multi_Agent.py` to customize how the supervisor routes questions to different agents.

## 📊 Performance

- **Parallel Processing**: Multiple agents can work simultaneously
- **Caching**: ChromaDB provides efficient vector similarity search
- **Streaming**: Real-time output streaming for better user experience

## 🤝 Contributing

Feel free to submit issues, feature requests, and pull requests to improve the system.

## 📄 License

This project is open-source and available under the MIT License. 