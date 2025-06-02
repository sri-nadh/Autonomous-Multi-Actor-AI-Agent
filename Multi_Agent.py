import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Literal, Annotated, Sequence
from typing_extensions import TypedDict
from langgraph.graph import MessagesState, START, END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command
from SQL_Query_Agent import nl2sql_tool
from RAG_Agent import retriever_tool
from WebSearch_Agent import web_search_tool_func
from langchain_core.messages import BaseMessage, HumanMessage


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

llm = ChatOpenAI(model=model, api_key=api_key)


# Define available agents
members = ["web_researcher", "rag", "nl2sql"]

# Add FINISH as an option for task completion
options = members + ["FINISH"]

# Create system prompt for supervisor
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)


#------------------------------------------------Supervisor Node ------------------------------------------------------#

# Define router type for structured output
class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["web_researcher", "rag", "nl2sql", "FINISH"]

# Create supervisor node function
def supervisor_node(state: MessagesState) -> Command[Literal["web_researcher", "rag", "nl2sql", "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    
    try:
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        print(f"Next Worker: {goto}")
        
        if goto == "FINISH":
            goto = END
        
        return Command(goto=goto)
    except Exception as e:
        print(f"Error in supervisor: {str(e)}")
        return Command(goto=END)


#------------------------------------------------Agent Container for all Specialised Agents------------------------------------------------------#

class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_agent(llm, tools):
    """Create an agent with tools."""
    llm_with_tools = llm.bind_tools(tools)
    
    def chatbot(state: AgentState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    graph_builder.add_edge("tools", "agent")
    graph_builder.set_entry_point("agent")
    return graph_builder.compile()


#------------------------------------------------Web Search AGENT------------------------------------------------------#

websearch_agent = create_agent(llm, [web_search_tool_func])

def web_research_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    try:
        result = websearch_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="web_researcher")
                ]
            },
            goto="supervisor",
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    HumanMessage(content=f"Web search error: {str(e)}", name="web_researcher")
                ]
            },
            goto="supervisor",
        )


#------------------------------------------------RAG AGENT------------------------------------------------------#

rag_agent = create_agent(llm, [retriever_tool])

def rag_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    try:
        result = rag_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="rag")
                ]
            },
            goto="supervisor",
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    HumanMessage(content=f"RAG error: {str(e)}", name="rag")
                ]
            },
            goto="supervisor",
        )
    
    
#------------------------------------------------SQL QUERY AGENT------------------------------------------------------#

nl2sql_agent = create_agent(llm, [nl2sql_tool])

def nl2sql_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    try:
        result = nl2sql_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="nl2sql")
                ]
            },
            goto="supervisor",
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    HumanMessage(content=f"SQL error: {str(e)}", name="nl2sql")
                ]
            },
            goto="supervisor",
        )


#------------------------------------------------Building Structure of the Workflow------------------------------------------------------#

builder = StateGraph(MessagesState)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("web_researcher", web_research_node)
builder.add_node("rag", rag_node)
builder.add_node("nl2sql", nl2sql_node)
graph = builder.compile()


#------------------------------------------------ Testing the Agent------------------------------------------------------#

def run_agent(question: str):
    """Run the multi-agent system with a question."""
    print(f"\n🤖 Processing question: {question}")
    print("=" * 50)
    
    try:
        for s in graph.stream(
            {"messages": [("user", question)]}, 
            subgraphs=True
        ):
            print(s)
            print("----")
    except Exception as e:
        print(f"Error running agent: {str(e)}")


if __name__ == "__main__":
    # Example: Complex Query Using Multiple Agents
    input_question = "Find the founder of FutureSmart AI and then do a web research on him"
    run_agent(input_question)
