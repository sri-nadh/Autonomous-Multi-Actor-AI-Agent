import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.tools import tool
from langchain_tavily import TavilySearch
import time

load_dotenv()


def create_web_search_tool():
    """Create web search tool with proper error handling."""
    try:
        # Check if API key is available
        if not os.getenv("TAVILY_API_KEY"):
            print("⚠️  Warning: TAVILY_API_KEY not set. Web search will not be available.")
            return None
        
        return TavilySearch(max_results=2, topic="news")
    except Exception as e:
        print(f"Warning: Could not initialize Tavily Search: {str(e)}")
        print("Make sure TAVILY_API_KEY is set in your environment variables.")
        return None


# Initialize the web search tool
web_search_tool = create_web_search_tool()


class WebSearchToolSchema(BaseModel):
    query: str


@tool(args_schema=WebSearchToolSchema)
def web_search_tool_func(query):
    """Tool to search the web for real-time information using Tavily Search"""
    print("🔍 Searching the web...")
    
    if web_search_tool is None:
        return "❌ Error: Web search not available. Please ensure TAVILY_API_KEY is properly set up."
    
    try:
        # Use the TavilySearch tool to get results
        results = web_search_tool.invoke({"query": query})
        
        if not results:
            return "ℹ️ No search results found for the given query."
        
        # Format the results for better readability
        formatted_results = []
        for i, result in enumerate(results[:3], 1):  # Limit to top 3 results
            if isinstance(result, dict):
                title = result.get('title', 'No title')
                content = result.get('content', result.get('snippet', 'No content'))
                url = result.get('url', 'No URL')
                formatted_results.append(
                    f"📌 Result {i}:\n"
                    f"📑 Title: {title}\n"
                    f"📝 Content: {content}\n"
                    f"🔗 Source: {url}\n"
                    f"{'─' * 50}\n"
                )
            else:
                formatted_results.append(f"📌 Result {i}: {str(result)}\n{'─' * 50}\n")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"❌ Error during web search: {str(e)}"


# Test the web search tool if available
if web_search_tool and os.getenv("TAVILY_API_KEY"):
    try:
        test_result = web_search_tool_func.invoke({"query": "latest AI news"})
        print("Web search tool test successful")
    except Exception as e:
        print(f"Web search tool test failed: {str(e)}")
else:
    print("Web search tool not available - TAVILY_API_KEY not set") 