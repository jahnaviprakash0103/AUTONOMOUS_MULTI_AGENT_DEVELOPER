# backend/langgraph_workflow.py

from langgraph.graph import StateGraph, END
from Agents.pm_agent import ProductManagerAgent
from Agents.architect_agent import ArchitectAgent
from Agents.dev_agent import DeveloperAgent
from Agents.qa_agent import QAAgent
import os
import json

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
    # return {**state, "architect_output": [architect_output] if isinstance(architect_output, dict) else architect_output}
    return {**state, "architect_output": architect_output}


def developer_node(state):
    import json, os

    print("\n👩‍💻 Running Developer Agent...")
    developer = DeveloperAgent()
    all_dev_outputs = []

    # Iterate through each phase and its architected data
    for phase in state["pm_output"]["phases"]:
        for arch_data in state["architect_output"]:
            if arch_data["phase_name"] == phase["phase_name"]:
                # Extract details dynamically from architect output
                system_design = arch_data.get("system_design", "N/A")
                tech_stack = json.dumps(arch_data.get("tech_stack", {}), indent=2)
                performance_metrics = json.dumps(arch_data.get("performance_metrics", {}), indent=2)
                architect_answers = json.dumps(arch_data, indent=2)

                # ✅ Updated: iterate through daily tasks instead of weekly
                for day_data in arch_data.get("tasks_by_day", []):
                    day = day_data.get("day", "Day X")
                    for task in day_data.get("tasks", []):
                        dev_result = developer.generate_code(
                            phase_description=phase["description"],
                            task_description=task,
                            system_design=system_design,
                            tech_stack=tech_stack,
                            performance_metrics=performance_metrics,
                            architect_answers=architect_answers,
                        )

                        all_dev_outputs.append({
                            "phase": phase["phase_name"],
                            "day": day,
                            "task": task,
                            "result": dev_result
                        })

    print("✅ Developer Agent completed.")

    # 🖨️ Preview output in terminal
    print("\n📦 Developer Output Preview (truncated):")
    for i, dev_output in enumerate(all_dev_outputs, start=1):
        print(f"\n--- Phase: {dev_output['phase']} | {dev_output['day']} | Task {i} ---")
        print(json.dumps(dev_output["result"], indent=2)[:800])

    # 💾 Save outputs to a folder (cleaner: one file per phase)
    output_dir = "generated_outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Group outputs by phase to reduce file clutter
    grouped_by_phase = {}
    for output in all_dev_outputs:
        grouped_by_phase.setdefault(output["phase"], []).append(output)

    for phase_name, outputs in grouped_by_phase.items():
        phase_file = os.path.join(output_dir, f"{phase_name.replace(' ', '_')}_dev_outputs.json")
        with open(phase_file, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2)

    print(f"\n💾 All generated developer outputs saved in folder: {output_dir}")

    return {**state, "developer_output": all_dev_outputs}




def qa_node(state):
    qa = QAAgent()
    all_test_cases = []

    print("\n🧪 Running QA Agent...")

    # Iterate through developer outputs
    for dev_output in state["developer_output"]:
        # Match the corresponding architect data for this phase
        phase_name = dev_output.get("phase", "")
        arch_data = next(
            (a for a in state["architect_output"] if a["phase_name"] == phase_name),
            {}
        )

        # Extract contextual info from Architect + Developer outputs
        phase_description = phase_name
        task_description = dev_output.get("task", "N/A")
        system_design = arch_data.get("system_design", "N/A")
        tech_stack = json.dumps(arch_data.get("tech_stack", {}), indent=2)
        performance_metrics = json.dumps(arch_data.get("performance_metrics", {}), indent=2)
        architect_answers = json.dumps(arch_data, indent=2)

        # Developer output result object
        result = dev_output.get("result", {})

        # --- Handle multiple possible code formats ---
        if isinstance(result.get("code"), dict):
            # Combine multiple code files into one string for LLM
            code_combined = "\n\n".join(
                [f"# File: {fname}\n{fcontent}" for fname, fcontent in result["code"].items()]
            )
        else:
            # Single code string
            code_combined = result.get("code", "")

        # --- Handle requirements (could be separate or inside code) ---
        requirements_txt = (
            result.get("requirements.txt")
            or (result.get("code", {}).get("requirements.txt") if isinstance(result.get("code"), dict) else "")
            or ""
        )

        # --- Input/Output stays the same ---
        input_output = json.dumps(result.get("input_output", {}), indent=2)


        # 🧠 Call QA Agent
        test_cases = qa.generate_test_cases(
        phase_description=phase_description,
        task_description=task_description,
        system_design=system_design,
        tech_stack=tech_stack,
        performance_metrics=performance_metrics,
        architect_answers=architect_answers,
        code=code_combined,
        requirements_txt=requirements_txt,
        input_output=input_output,
)

        # Store results
        all_test_cases.append({
            "phase": phase_name,
            "week": dev_output.get("week"),
            "task": task_description,
            "test_cases": test_cases
        })

    print("✅ QA Agent completed.")
    print(f"🧾 Total QA test sets generated: {len(all_test_cases)}")

    # 💾 Save to folder
    output_dir = "qa_outputs"
    os.makedirs(output_dir, exist_ok=True)

    for i, qa_output in enumerate(all_test_cases, start=1):
        base_name = f"{qa_output['phase'].replace(' ', '_')}_week{qa_output.get('week')}_task{i}"
        json_file = os.path.join(output_dir, f"{base_name}_tests.json")

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(qa_output, f, indent=2)

    print(f"\n💾 All QA test cases saved in folder: {output_dir}\n")

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
