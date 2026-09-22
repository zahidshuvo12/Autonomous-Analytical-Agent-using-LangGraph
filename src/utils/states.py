from typing_extensions import TypedDict, NotRequired
from typing import Optional, List, Annotated
from langgraph.graph.message import add_messages
from .objects import Analyst
from langgraph.graph import MessagesState
import operator

#state
class GenerateAnalystState(TypedDict):
    topic:str #research topic
    max_analysts:int #number of analysts
    human_analyst_feedback:NotRequired[Optional[str]] #human feedback for what is generated
    analyst: NotRequired[List[Analyst]] #list of all analysts
    messages: Annotated[List, add_messages]

class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[list, operator.add] # Source docs
    analyst: Analyst # Analyst asking questions
    interview: str # Interview transcript
    sections: list # Final key we duplicate in outer state for Send() API