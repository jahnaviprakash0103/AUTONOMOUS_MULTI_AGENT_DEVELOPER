# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from api.routes import router as api_router
import os

# Import LangGraph components
from langgraph.graph import StateGraph, END
from main_langgraph import pm_node
from main_langgraph import architect_node
from main_langgraph import developer_node
from main_langgraph import qa_node
from main_langgraph import create_initial_state

app = FastAPI(title="Autonomous Developer - Product Manager Agent")

# Allow frontend (React) to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can restrict this to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Backend API is running 🚀"}


# -------------------------------
# 🔹 Endpoint: Generate pipeline graph
# -------------------------------
@app.get("/api/pipeline/graph")
def generate_pipeline_graph():
    """
    Generates a visual PNG of the agent workflow pipeline and returns the file path.
    """
    try:
        # Step 1: Define workflow structure
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

        # Step 2: Generate and save pipeline visualization
        output_file = "pipeline.png"
        try:
            graph.get_graph().draw_mermaid_png(output_file)
        except AttributeError:
            # fallback for older langgraph versions
            graph.draw_mermaid_png(output_file)

        return FileResponse(output_file, media_type="image/png")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# -------------------------------
# 🔹 Endpoint: Run workflow from frontend input
# -------------------------------
import traceback

from typing import TypedDict

class ProjectState(TypedDict):
    idea: str
    pm_output: str | None
    architect_output: str | None
    developer_output: str | None
    qa_output: str | None


@app.post("/api/project/idea")
async def run_project_idea(data: dict):
    print("api hit")
    """
    Receives a project idea from frontend and executes the full workflow.
    """
    try:
        project_idea = data.get("idea", "")
        if not project_idea:
            return JSONResponse(status_code=400, content={"error": "Project idea is required."})

        print("\n📩 API hit: /project/idea")
        print("🧠 Project Idea Received:", project_idea)

        # Step 1: Build the workflow graph
        print("⚙️  Building LangGraph workflow...")
        graph = StateGraph(ProjectState)  # ✅ Pass schema here

        graph.add_node("pm", pm_node)
        graph.add_node("architect", architect_node)
        graph.add_node("developer", developer_node)
        graph.add_node("qa", qa_node)

        graph.add_edge("pm", "architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "qa")
        graph.add_edge("qa", END)
        graph.set_entry_point("pm")

        # Step 2: Compile and run
        workflow = graph.compile()
        state = create_initial_state(project_idea)

        print("🚀 Executing LangGraph workflow...")
        final_state = workflow.invoke(state)

        print("✅ Workflow completed.")
        print("🧾 Final State:", final_state)

        # Step 3: Return result to frontend
        return {"result": final_state.get("qa_output", "No output generated.")}

    except Exception as e:
        print("❌ Error in /api/project/idea endpoint:")
        traceback.print_exc()
        import sys
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(f"\n⚠️ Exception Type: {exc_type}")
        print(f"⚠️ Exception Message: {exc_value}")
        print("⚠️ Traceback:")
        traceback.print_tb(exc_tb)
        return JSONResponse(status_code=500, content={"error": str(e)})
      




# -------------------------------
# 🔹 Entry Point
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
