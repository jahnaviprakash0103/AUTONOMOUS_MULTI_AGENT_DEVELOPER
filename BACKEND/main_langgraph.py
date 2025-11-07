# backend/langgraph_workflow.py

from langgraph.graph import StateGraph, END
from Agents.pm_agent import ProductManagerAgent
from Agents.architect_agent import ArchitectAgent
from Agents.dev_agent import DeveloperAgent
from Agents.qa_agent import QAAgent


# --- Define the state of the workflow ---
def create_initial_state(project_idea: str):
    return {
        "idea": project_idea,
        "pm_output": None,
        "architect_output": None,
        "developer_output": None,
        "qa_output": None,
    }


# --- Define nodes ---
def pm_node(state):
    pm = ProductManagerAgent()
    pm_output = pm.process_project_idea(state["idea"])
    phase1 = pm.send_phase_to_architect(pm_output)
    return {**state, "pm_output": pm_output, "phase1": phase1}


def architect_node(state):
    architect = ArchitectAgent()
    architect_output = architect.process_all_phases(state["pm_output"]["phases"])
    print("✅ Architect output generated.")
    return {**state, "architect_output": [architect_output] if isinstance(architect_output, dict) else architect_output}



def developer_node(state):
    print("\n👩‍💻 Running Developer Agent...")
    developer = DeveloperAgent()
    all_dev_outputs = []

    for phase in state["pm_output"]["phases"]:
        for taskset in state["architect_output"]:
            if taskset["phase_name"] == phase["phase_name"]:
                for week_task in taskset.get("tasks_by_week", []):
                    for task in week_task["tasks"]:
                        dev_result = developer.generate_code(
                            phase_description=phase["description"],
                            task_description=task,
                            system_design="Based on architect plan",
                            tech_stack="Python, FastAPI, PostgreSQL, Docker",
                            performance_metrics="High throughput, low latency",
                            architect_answers="As per architect plan",
                        )
                        all_dev_outputs.append(dev_result)
    print("✅ Developer Agent completed.")
    return {**state, "developer_output": all_dev_outputs}


def qa_node(state):
    qa = QAAgent()
    all_test_cases = []

    for dev_output in state["developer_output"]:
        test_cases = qa.generate_test_cases(
            phase_description="Overall Phase Description",
            task_description="Task from developer output",
            system_design="Architect system plan",
            tech_stack="Python, FastAPI, PostgreSQL",
            performance_metrics="Low latency, scalability",
            architect_answers="As per architect plan",
            code=dev_output.get("code", ""),
            requirements_txt=dev_output.get("requirements.txt", ""),
            input_output=dev_output.get("input_output", {}),
        )
        all_test_cases.append(test_cases)

    return {**state, "qa_output": all_test_cases}


# --- Build the workflow graph ---
def build_workflow():
    graph = StateGraph()

    graph.add_node("pm", pm_node)
    graph.add_node("architect", architect_node)
    graph.add_node("developer", developer_node)
    graph.add_node("qa", qa_node)

    graph.add_edge("pm", "architect")
    graph.add_edge("architect", "developer")
    graph.add_edge("developer", "qa")
    graph.add_edge("qa", END)

    graph.set_entry_point("pm")

    return graph.compile()
