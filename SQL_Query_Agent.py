import re
import os
import urllib.request
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from pydantic import BaseModel
from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.utilities import SQLDatabase


llm = ChatOpenAI(model="gpt-4o")


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


# Define clean_sql_query function
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
    
    try:
        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)

        chain = (
            RunnablePassthrough.assign(query=write_query | RunnableLambda(clean_sql_query)).assign(
                result=itemgetter("query") | execute_query
            )
        )

        response = chain.invoke({"question": question})
        return response['result']
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"
