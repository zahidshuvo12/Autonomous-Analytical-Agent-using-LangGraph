from dotenv import load_dotenv
from .states import GenerateAnalystState, InterviewState
from typing import Literal
from langgraph.graph import END
from langchain.messages import AIMessage

load_dotenv()

# conditional_edges 
def should_continue(state: GenerateAnalystState):
    """ Return the next node to execute """

    # Check if human feedback
    human_analyst_feedback=state.get('human_analyst_feedback', None) 

    if human_analyst_feedback:
        if human_analyst_feedback:
            return "create_analysts"
    
    # Otherwise end
    return END

def route_messages(state: InterviewState, name: str = "expert"):

    """ Route between question and answer """
    
    # Get messages
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns',2)

    # Check the number of expert answers 
    num_responses = len([m for m in messages if isinstance(m, AIMessage) and m.name == name])

    # End if expert has answered more than the max turns
    if num_responses >= max_num_turns:
        return 'save_interview'

    return "ask_question"