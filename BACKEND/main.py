from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langgraph.graph import StateGraph, END
from main_langgraph import pm_node, architect_node, developer_node, qa_node, create_initial_state
from typing import TypedDict
import os, traceback, shutil, json

# --- FastAPI setup ---
app = FastAPI(title="Autonomous Developer - Product Manager Agent")

# Allow frontend (React) to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output folders
os.makedirs("generated_outputs", exist_ok=True)
os.makedirs("qa_outputs", exist_ok=True)

# Mount folders for static file download
app.mount("/outputs", StaticFiles(directory="generated_outputs"), name="outputs")
app.mount("/qa_outputs", StaticFiles(directory="qa_outputs"), name="qa_outputs")

# -------------------------------
# 🔹 Download All Files as ZIP
# -------------------------------
@app.get("/download/all")
def download_all_files():
    """
    Zips all developer & QA task files (keeping folder structure) and returns the ZIP.
    """
    zip_name = "all_task_outputs.zip"
    temp_dir = "temp_all_outputs"

    # Remove old ZIP if exists
    if os.path.exists(zip_name):
        os.remove(zip_name)
    # Remove temp folder if exists
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # Copy developer outputs
    if os.path.exists("generated_outputs"):
        shutil.copytree("generated_outputs", os.path.join(temp_dir, "developer"), dirs_exist_ok=True)
    # Copy QA outputs
    if os.path.exists("qa_outputs"):
        shutil.copytree("qa_outputs", os.path.join(temp_dir, "qa"), dirs_exist_ok=True)

    # Create ZIP
    shutil.make_archive("all_task_outputs", 'zip', temp_dir)
    # Clean temp folder
    shutil.rmtree(temp_dir)

    return FileResponse(
        path=zip_name,
        filename=zip_name,
        media_type="application/zip"
    )

# -------------------------------
# 🔹 Root Endpoint
# -------------------------------
@app.get("/")
def root():
    return {"message": "Backend API is running 🚀"}

# -------------------------------
# 🔹 Pipeline Graph Visualization
# -------------------------------
@app.get("/api/pipeline/graph")
def generate_pipeline_graph():
    try:
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

        output_file = "pipeline.png"
        try:
            graph.get_graph().draw_mermaid_png(output_file)
        except AttributeError:
            graph.draw_mermaid_png(output_file)

        return FileResponse(output_file, media_type="image/png")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------
# 🔹 Project Workflow Execution
# -------------------------------
class ProjectState(TypedDict):
    idea: str
    pm_output: str | None
    architect_output: str | None
    developer_output: str | None
    qa_output: str | None

# Helper function to recursively list files
def list_files_recursive(base_dir, base_url):
    all_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, base_dir).replace("\\", "/")
            all_files.append({
                "name": rel_path,
                "url": f"{base_url}/{rel_path}"
            })
    return all_files

@app.post("/api/project/idea")
async def run_project_idea(request: Request):
    try:
        data = await request.json()
        project_idea = data.get("idea", "")
        if not project_idea:
            return JSONResponse(status_code=400, content={"error": "Project idea is required."})

        print("\n📩 API hit: /api/project/idea")
        print("🧠 Project Idea Received:", project_idea)

        # Build workflow graph
        graph = StateGraph(ProjectState)
        graph.add_node("pm", pm_node)
        graph.add_node("architect", architect_node)
        graph.add_node("developer", developer_node)
        graph.add_node("qa", qa_node)
        graph.add_edge("pm", "architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "qa")
        graph.add_edge("qa", END)
        graph.set_entry_point("pm")

        # Execute workflow
        workflow = graph.compile()
        state = create_initial_state(project_idea)
        print("🚀 Executing workflow...")
        final_state = workflow.invoke(state)
        print("✅ Workflow completed.")

        # -----------------------
        # Prepare files for frontend
        # -----------------------
        dev_files = list_files_recursive("generated_outputs", "http://127.0.0.1:8000/outputs")
        qa_files = list_files_recursive("qa_outputs", "http://127.0.0.1:8000/qa_outputs")
        generated_files = dev_files + qa_files

        # Group outputs by phase for structured display
        developer_output = final_state.get("developer_output", [])
        qa_output = final_state.get("qa_output", [])

        grouped_outputs = {}
        for dev in developer_output:
            phase = dev.get("phase", "Unknown Phase")
            grouped_outputs.setdefault(phase, {"developer": [], "qa": []})
            grouped_outputs[phase]["developer"].append(dev)
        for qa in qa_output:
            phase = qa.get("phase", "Unknown Phase")
            grouped_outputs.setdefault(phase, {"developer": [], "qa": []})
            grouped_outputs[phase]["qa"].append(qa)

        return {
            "message": "Workflow completed successfully",
            "phases": grouped_outputs,
            "files": generated_files,
            "text_response": f"```json\n{json.dumps(grouped_outputs, indent=2)}\n```"
        }

    except Exception as e:
        print("❌ Error during workflow execution:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------
# 🔹 Entry Point
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
