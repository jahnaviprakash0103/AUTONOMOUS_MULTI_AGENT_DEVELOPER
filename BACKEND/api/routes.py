# api/routes.py
from fastapi import APIRouter, HTTPException
from Agents.pm_agent import ProductManagerAgent

router = APIRouter()

# Initialize the Product Manager Agent
pm_agent = ProductManagerAgent()

@router.post("/project/idea")
async def process_project_idea(request: dict):
    print("api hit")
    """
    Receives a project idea from the frontend and returns
    the structured phase plan and Phase 1 details.
    """
    try:
        idea = request.get("idea", "").strip()
        if not idea:
            raise HTTPException(status_code=400, detail="Missing 'idea' in request body.")

        # Process the idea using PM Agent
        structured_output = pm_agent.process_project_idea(idea)
        phase1 = pm_agent.send_phase_to_architect(structured_output)

        return {
            "success": True,
            "project_plan": structured_output,
            "phase1_details": phase1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
