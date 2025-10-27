# api/routes.py
from fastapi import APIRouter, HTTPException
from Agents.pm_agent import ProductManagerAgent
from Agents.architect_agent import ArchitectAgent  

router = APIRouter()

# Initialize both agents
pm_agent = ProductManagerAgent()
architect_agent = ArchitectAgent()

@router.post("/project/idea")
async def process_project_idea(request: dict):
    print("✅ API hit: /project/idea")
    """
    Receives a project idea from the frontend and returns:
    1. Structured phase plan from Product Manager Agent
    2. Phase 1 details
    3. Weekly tasks from Architect Agent
    """
    try:
        idea = request.get("idea", "").strip()
        if not idea:
            raise HTTPException(status_code=400, detail="Missing 'idea' in request body.")

        # Step 1: Process project idea using PM Agent
        structured_output = pm_agent.process_project_idea(idea)

        # Step 2: Send first phase to architect for demonstration
        phase1 = pm_agent.send_phase_to_architect(structured_output)

        # Step 3: Process all phases using Architect Agent
        phases = structured_output.get("phases", [])
        architect_output = []
        if phases:
            architect_output = architect_agent.process_all_phases(phases)
            print("\n✅ Architect Agent Output:\n", architect_output)
        else:
            print("⚠️ No phases found in PM output.")

        # Step 4: Return combined result
        return {
            "success": True,
            "project_plan": structured_output,
            "phase1_details": phase1,
            "architect_plan": architect_output
        }

    except Exception as e:
        print("❌ Error in /project/idea:", e)
        raise HTTPException(status_code=500, detail=str(e))
