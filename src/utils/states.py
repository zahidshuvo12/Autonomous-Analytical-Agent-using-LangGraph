from typing_extensions import TypedDict, NotRequired
from typing import Optional, List, Annotated
from langgraph.graph.message import add_messages
from .objects import Analyst

#state
class GenerateAnalystState(TypedDict):
    topic:str #research topic
    max_analysts:int #number of analysts
    human_analyst_feedback:NotRequired[Optional[str]] #human feedback for what is generated
    analyst: NotRequired[List[Analyst]] #list of all analysts
    messages: Annotated[List, add_messages]

