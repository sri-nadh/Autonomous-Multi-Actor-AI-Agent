import re
import os
import urllib.request
import hashlib
import json
from datetime import datetime, timedelta
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from pydantic import BaseModel
from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase


def ensure_chinook_db():
    """Download Chinook database if it doesn't exist."""
    db_path = "Chinook.db"
    if not os.path.exists(db_path):
        print("Chinook.db not found. Downloading...")
        try:
            url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
            urllib.request.urlretrieve(url, db_path)
            print("Chinook.db downloaded successfully.")
        except Exception as e:
            print(f"Error downloading Chinook.db: {str(e)}")
            print("Please manually download Chinook.db and place it in the project directory.")
            return False
    return True


# Ensure database exists before creating connection
if ensure_chinook_db():
    try:
        db = SQLDatabase.from_uri("sqlite:///Chinook.db")
        print("Connected to Chinook database successfully.")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        db = None
else:
    db = None


llm = ChatOpenAI(model="gpt-4o")


# Query Cache Implementation
class QueryCache:
    def __init__(self, cache_file="query_cache.json", max_age_hours=24):
        self.cache_file = cache_file
        self.max_age_hours = max_age_hours
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _get_cache_key(self, question):
        """Generate a cache key for the question."""
        return hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    def _is_expired(self, timestamp):
        """Check if cache entry is expired."""
        cache_time = datetime.fromisoformat(timestamp)
        return datetime.now() - cache_time > timedelta(hours=self.max_age_hours)
    
    def get(self, question):
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(question)
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not self._is_expired(entry['timestamp']):
                print("📋 Using cached result")
                return entry['result']
            else:
                # Remove expired entry
                del self.cache[cache_key]
                self._save_cache()
        return None
    
    def set(self, question, result):
        """Cache the result."""
        cache_key = self._get_cache_key(question)
        self.cache[cache_key] = {
            'question': question,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
        print("💾 Result cached for future use")


# Initialize cache
query_cache = QueryCache()


def explain_sql_query(query: str) -> str:
    """Generate a human-readable explanation of the SQL query."""
    explanation_prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        Explain the following SQL query in simple, human-readable language:
        
        SQL Query: {query}
        
        Please provide:
        1. What this query does in one sentence
        2. Which tables it accesses
        3. What data it returns
        4. Any important filtering or sorting applied
        
        Keep the explanation concise and user-friendly.
        """
    )
    
    try:
        explanation_chain = explanation_prompt | llm | StrOutputParser()
        explanation = explanation_chain.invoke({"query": query})
        return f"\n🔍 **Query Explanation:**\n{explanation}\n"
    except Exception as e:
        return f"\n⚠️ Could not generate query explanation: {str(e)}\n"


def clean_sql_query(text: str) -> str:
    """
    Clean SQL query by removing code block syntax, various SQL tags, backticks,
    prefixes, and unnecessary whitespace while preserving the core SQL query.

    Args:
        text (str): Raw SQL query text that may contain code blocks, tags, and backticks

    Returns:
        str: Cleaned SQL query
    """
    # Step 1: Remove code block syntax and any SQL-related tags
    # This handles variations like ```sql, ```SQL, ```SQLQuery, etc.
    block_pattern = r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\s*(.*?)\s*```"
    text = re.sub(block_pattern, r"\1", text, flags=re.DOTALL)

    # Step 2: Handle "SQLQuery:" prefix and similar variations
    # This will match patterns like "SQLQuery:", "SQL Query:", "MySQL:", etc.
    prefix_pattern = r"^(?:SQL\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\s*:\s*"
    text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)

    # Step 3: Extract the first SQL statement if there's random text after it
    # Look for a complete SQL statement ending with semicolon
    sql_statement_pattern = r"(SELECT.*?;)"
    sql_match = re.search(sql_statement_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if sql_match:
        text = sql_match.group(1)

    # Step 4: Remove backticks around identifiers
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # Step 5: Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Step 6: Preserve newlines for main SQL keywords to maintain readability
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
               'LIMIT', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN',
               'OUTER JOIN', 'UNION', 'VALUES', 'INSERT', 'UPDATE', 'DELETE']

    # Case-insensitive replacement for keywords
    pattern = '|'.join(r'\b{}\b'.format(k) for k in keywords)
    text = re.sub(f'({pattern})', r'\n\1', text, flags=re.IGNORECASE)

    # Step 7: Final cleanup
    # Remove leading/trailing whitespace and extra newlines
    text = text.strip()
    text = re.sub(r'\n\s*\n', '\n', text)

    return text


class SQLToolSchema(BaseModel):
    question: str


@tool(args_schema=SQLToolSchema)
def nl2sql_tool(question):
    """Tool to Generate and Execute SQL Query to answer User Questions related to chinook DB"""
    print("INSIDE NL2SQL TOOL")
    
    if db is None:
        return "Error: Database connection not available. Please ensure Chinook.db is properly set up."
    
    # Check cache first
    cached_result = query_cache.get(question)
    if cached_result:
        return cached_result
    
    try:
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)

        # Generate the SQL query
        raw_query = write_query.invoke({"question": question})
        cleaned_query = clean_sql_query(raw_query)
        
        # Generate explanation for the query
        explanation = explain_sql_query(cleaned_query)
        
        # Execute the query
        result = execute_query.invoke(cleaned_query)
        
        # Format the final response
        final_response = f"""{explanation}

📊 **Query Results:**
{result}

🔧 **SQL Query Used:**
```sql
{cleaned_query}
```
"""
        
        # Cache the result
        query_cache.set(question, final_response)
        
        return final_response
        
    except Exception as e:
        error_msg = f"Error executing SQL query: {str(e)}"
        return error_msg
