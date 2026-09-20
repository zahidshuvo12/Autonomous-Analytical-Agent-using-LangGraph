from src.utils.nodes import create_analysts
from langgraph.graph import START, END, StateGraph
from src.utils.states import GenerateAnalystState
from dotenv import load_dotenv

load_dotenv()

# creating our graph
# GenerateAnalystsState state
# nodes create_analysts
# edge no need / simple

# building our graph
builder = StateGraph(GenerateAnalystState)
builder.add_node("create_analysts", create_analysts)

builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", END)

graph = builder.compile()