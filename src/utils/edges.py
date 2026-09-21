from dotenv import load_dotenv
from .states import GenerateAnalystState
from typing import Literal
from langgraph.graph import END

load_dotenv()

# conditional_edges 
def should_continue(state: GenerateAnalystState)-> Literal["create_analysts", END]:
    """ Return the next node to execute """

    # Check if human feedback
    human_analyst_feedback=state.get('human_analyst_feedback', None) 

    if human_analyst_feedback:
        if human_analyst_feedback:
            return "create_analysts"
    
    # Otherwise end
    return END