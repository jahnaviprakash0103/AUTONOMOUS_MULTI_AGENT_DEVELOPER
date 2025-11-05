# api/routes.py
from fastapi import APIRouter, HTTPException
from Agents.pm_agent import ProductManagerAgent
from Agents.architect_agent import ArchitectAgent
from Agents.devops_agent import DevOpsAgent

router = APIRouter()

# Initialize all agents
pm_agent = ProductManagerAgent()
architect_agent = ArchitectAgent()
devops_agent = DevOpsAgent()

@router.post("/project/idea")
async def process_project_idea(request: dict):
    print("✅ API hit: /project/idea")
    """
    Receives a project idea from the frontend and returns:
    1. Structured phase plan from Product Manager Agent
    2. Phase 1 details
    3. Weekly tasks from Architect Agent
    4. Deployment plan from DevOps Agent
    5. Phase-specific deployment checklists
    """
    try:
        idea = request.get("idea", "").strip()
        if not idea:
            raise HTTPException(status_code=400, detail="Missing 'idea' in request body.")
        
        # Step 1: Process project idea using PM Agent
        print("\n📋 Step 1: Product Manager creating project phases...")
        structured_output = pm_agent.process_project_idea(idea)
        
        # Step 2: Send first phase to architect for demonstration
        phase1 = pm_agent.send_phase_to_architect(structured_output)
        
        # Step 3: Process all phases using Architect Agent
        print("\n🏗️ Step 2: Architect breaking down phases into weekly tasks...")
        phases = structured_output.get("phases", [])
        architect_output = []
        if phases:
            architect_output = architect_agent.process_all_phases(phases)
            print("\n✅ Architect Agent Output:\n", architect_output)
        else:
            print("⚠️ No phases found in PM output.")
        
        # Step 4: Create overall deployment plan using DevOps Agent
        print("\n🚀 Step 3: DevOps creating overall deployment plan...")
        deployment_plan = {}
        if structured_output:
            deployment_plan = devops_agent.create_deployment_plan(structured_output)
            print("\n✅ DevOps Deployment Plan Created")
        
        # Step 5: Create phase-specific deployment checklists
        print("\n📝 Step 4: DevOps creating phase-specific deployment checklists...")
        phase_deployments = []
        if architect_output:
            phase_deployments = devops_agent.process_all_phases(architect_output)
            print("\n✅ DevOps Phase Deployment Checklists Created")
        
        # Step 6: Return combined result
        return {
            "success": True,
            "project_plan": structured_output,
            "phase1_details": phase1,
            "architect_plan": architect_output,
            "devops_deployment_plan": deployment_plan,
            "devops_phase_deployments": phase_deployments
        }
    
    except Exception as e:
        print("❌ Error in /project/idea:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/deployment-plan")
async def get_deployment_plan(request: dict):
    """
    Separate endpoint to get just the deployment plan for a project.
    """
    try:
        project_info = request.get("project_info")
        if not project_info:
            raise HTTPException(status_code=400, detail="Missing 'project_info' in request body.")
        
        print("\n🚀 Creating deployment plan...")
        deployment_plan = devops_agent.create_deployment_plan(project_info)
        
        return {
            "success": True,
            "deployment_plan": deployment_plan
        }
    
    except Exception as e:
        print("❌ Error in /project/deployment-plan:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/phase-deployment")
async def get_phase_deployment(request: dict):
    """
    Get deployment checklist for a specific phase.
    """
    try:
        phase_tasks = request.get("phase_tasks")
        if not phase_tasks:
            raise HTTPException(status_code=400, detail="Missing 'phase_tasks' in request body.")
        
        print(f"\n📝 Creating deployment checklist for phase...")
        phase_deployment = devops_agent.create_phase_deployment(phase_tasks)
        
        return {
            "success": True,
            "phase_deployment": phase_deployment
        }
    
    except Exception as e:
        print("❌ Error in /project/phase-deployment:", e)
        raise HTTPException(status_code=500, detail=str(e))