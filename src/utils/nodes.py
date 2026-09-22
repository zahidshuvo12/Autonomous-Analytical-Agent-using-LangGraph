from dotenv import load_dotenv
from .states import GenerateAnalystState, InterviewState
from .models import llm
from .objects import Analyst, Perspectives, SearchQuery
from .prompts import analyst_instructions, question_instructions, search_instructions, answer_instructions
from langchain.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import interrupt
from langchain_tavily import TavilyResearch

load_dotenv()

# nodes
def create_analysts(state: GenerateAnalystState):
    """create analyst"""
    topic=state['topic']
    max_analysts=state['max_analysts']
    human_analyst_feedback=state.get('human_analyst_feedback', '')
        
    # Enforce structured output
    structured_llm = llm.with_structured_output(Perspectives)
    
    # System message
    system_message = analyst_instructions.format(topic=topic,
                                            human_analyst_feedback=human_analyst_feedback, 
                                            max_analysts=max_analysts)
    
    # Generate question
    analysts = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])
    
    # Write the list of analysis to state
    # return {"analysts": analysts.analysts}
    # Build a readable summary for the Interact chat view
    summary = "\n\n".join(
        f"**{a.name}**\n"
        f"- Role: {a.role}\n"
        f"- Affiliation: {a.affiliation}\n"
        f"- Description: {a.description}"
        for a in analysts.analysts
    )
    summary_message = AIMessage(
        content=f"Created {len(analysts.analysts)} analyst(s):\n\n{summary}"
    )
    
    # Write the list of analysts + a chat message to state
    return {
        "analyst": analysts.analysts,
        "messages": [summary_message],
    }
    
def human_feedback(state: GenerateAnalystState):
    
    analysts = [ analyst.model_dump() if hasattr(analyst, "model_dump") 
                else analyst for analyst in state.get("analysts", []) ] 
    
    # Build a readable version for the interrupt UI 
    analyst_summary = "\n\n".join( f"{i}. **{analyst.get('name', 'Unknown')}**\n" 
                                  f" - Role: {analyst.get('role', 'N/A')}\n" 
                                  for i, analyst in enumerate(analysts, start=1) )
    feedback = interrupt({
        "question": "Are these analysts okay?",
        "analysts": analyst_summary,
        "instructions": "Return feedback to regenerate analysts, or return empty/perfect/continue to approve."
    })

    if feedback is None:
        return {"human_analyst_feedback": None}

    if isinstance(feedback, str):
        feedback = feedback.strip()

        if feedback == "":
            return {"human_analyst_feedback": None}

        if feedback.lower() in {"perfect", "continue", "approved", "yes"}:
            return {"human_analyst_feedback": None}

        return {"human_analyst_feedback": feedback}

    return {"human_analyst_feedback": None}

def generate_question(state: InterviewState):
    """ Node to generate a question """

    # Get state
    analyst = state["analyst"]
    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)
    messages = state["messages"]

    # Generate question 
    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)]+messages)
        
    # Write messages to state
    return {"messages": [question]}

def search_web(state: InterviewState):
    """ Retrieve docs from web search """

    # Search instruction
    structured_llm = llm.with_structured_output(SearchQuery)
    search_instruction_system_message = SystemMessage(content= search_instructions)
    tavily_search = TavilyResearch (max_results = 3)
    search_query = structured_llm.invoke([search_instruction_system_message]+state['messages'])
    
    #Search
    data = tavily_search.invoke({"query": search_query.search_query})
    search_docs = data.get("results", data)
    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

def search_web2(state: InterviewState):
    """ Retrieve docs from web search """

    # Search instruction
    structured_llm = llm.with_structured_output(SearchQuery)
    search_instruction_system_message = SystemMessage(content= search_instructions)
    tavily_search = TavilyResearch (max_results = 3)
    search_query = structured_llm.invoke([search_instruction_system_message]+state['messages'])
    
    #Search
    data = tavily_search.invoke({"query": search_query.search_query})
    search_docs = data.get("results", data)
    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}
    
def generate_answer(state: InterviewState):
    
    """ Node to answer a question """

    # Get state
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    if isinstance(analyst, dict):
            analyst = Analyst.model_validate(analyst)

    # Answer question
    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)]+messages)
            
    # Name the message as coming from the expert
    answer.name = "expert"
    
    # Append it to state
    return {"messages": [answer]}  