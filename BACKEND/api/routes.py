from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from workflow.graph_builder import build_workflow
from main_langgraph import create_initial_state

router = APIRouter()



# @router.post("/project/idea")
# async def process_project_idea(request: dict):
#     """
#     Runs the LangGraph workflow when a project idea is received.
#     """
#     try:
#         idea = request.get("idea", "").strip()
#         if not idea:
#             raise HTTPException(status_code=400, detail="Missing 'idea' in request body.")

#         # ✅ Run through LangGraph workflow
#         workflow = build_workflow()
#         initial_state = create_initial_state(idea)
#         final_state = workflow.invoke(initial_state)

#         return {
#             "success": True,
#             "final_output": final_state.get("qa_output", "No output generated."),
#             "full_state": final_state
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")
