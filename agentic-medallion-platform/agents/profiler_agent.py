from models.state import ProfileState

from langgraph.graph import StateGraph, START, END
from tools.schema_tool import analyze_schema

def profiler_node(state:ProfileState) -> ProfileState:
    """
    First Langgraph node
    Currently it only updates the state.
    """

    print("Profiler node started...")

    # print(f"Input file: {state['file_path']}")

    # state["report"] = {"status": "Profiler node executed successfully."}
    schema = analyze_schema(state["file_path"])

    state["schema"] = schema

    return state

def create_graph():

    #Create a workflow that uses ProfileState
    workflow = StateGraph(ProfileState)

    #Register the node
    workflow.add_node("profiler", profiler_node)

    #start -> Profiler
    workflow.add_edge(START, "profiler")
    #profiler -> end
    workflow.add_edge("profiler", END)


    #compile the workflow
    return workflow.compile()
