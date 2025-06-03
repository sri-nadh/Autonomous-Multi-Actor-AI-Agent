
import os
from dotenv import load_dotenv

load_dotenv()

def test_sql_agent():
    """Test the SQL agent."""
    print("🧪 Testing SQL Agent...")
    try:
        from SQL_Query_Agent import nl2sql_tool
        
        # Test basic SQL query
        result = nl2sql_tool.invoke({"question": "How many customers are there in the database?"})
        print(f"✅ SQL Agent test result: {result}")
        return True
    except Exception as e:
        print(f"❌ SQL Agent test failed: {str(e)}")
        return False


def test_rag_agent():
    """Test the RAG agent."""
    print("\n🧪 Testing RAG Agent...")
    try:
        from RAG_Agent import retriever_tool
        
        # Test document retrieval
        result = retriever_tool.invoke({"question": "Tell me about the founder"})
        print(f"✅ RAG Agent test result: {result}")
        return True
    except Exception as e:
        print(f"❌ RAG Agent test failed: {str(e)}")
        return False


def test_web_search_agent():
    """Test the web search agent."""
    print("\n🧪 Testing Web Search Agent...")
    try:
        if not os.getenv("TAVILY_API_KEY"):
            print("⚠️  Skipping web search test - TAVILY_API_KEY not set")
            return True
            
        from WebSearch_Agent import web_search_tool_func
        
        result = web_search_tool_func.invoke({"query": "latest AI news"})
        print(f"✅ Web Search Agent test result: {len(result.split())} words returned")
        return True
    except Exception as e:
        print(f"❌ Web Search Agent test failed: {str(e)}")
        return False


def test_multi_agent():
    """Test the complete multi-agent system."""
    print("\n🧪 Testing Multi-Agent System...")
    try:
        from Multi_Agent import run_agent
        
        # Test with a simple question
        print("Running test query...")
        run_agent("How many customers are in the database?")
        print("✅ Multi-Agent system test completed")
        return True
    except Exception as e:
        print(f"❌ Multi-Agent system test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing Multi-Actor AI Agent System")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please update your .env file.")
        return
    
    # Run individual agent tests
    sql_ok = test_sql_agent()
    rag_ok = test_rag_agent()
    web_ok = test_web_search_agent()
    
    # Run integrated test if individual tests pass
    if sql_ok and rag_ok:
        multi_ok = test_multi_agent()
    else:
        print("\n⚠️  Skipping multi-agent test due to individual agent failures")
        multi_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"SQL Agent: {'✅' if sql_ok else '❌'}")
    print(f"RAG Agent: {'✅' if rag_ok else '❌'}")
    print(f"Web Search Agent: {'✅' if web_ok else '❌'}")
    print(f"Multi-Agent System: {'✅' if multi_ok else '❌'}")
    
    if all([sql_ok, rag_ok, web_ok, multi_ok]):
        print("\n🎉 All tests passed! Your system is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main() 