# workflow/graph_builder.py
from langgraph.graph import StateGraph, END
from main_langgraph import pm_node
from main_langgraph import architect_node
from main_langgraph import developer_node
from main_langgraph import qa_node
from main_langgraph import create_initial_state

def build_workflow():
    graph = StateGraph()
    graph.add_node("pm", pm_node )
    graph.add_node("architect", architect_node)
    graph.add_node("developer", developer_node)
    graph.add_node("qa", qa_node)

    graph.add_edge("pm", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_edge("qa", END)
    graph.set_entry_point("pm")

    return graph.compile()
