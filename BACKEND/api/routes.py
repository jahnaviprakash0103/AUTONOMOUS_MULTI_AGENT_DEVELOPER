from fastapi import APIRouter, HTTPException
from Agents.architect_agent import ArchitectAgent
from Agents.pm_agent import ProductManagerAgent
from Agents.dev_agent import DeveloperAgent
from Agents.qa_agent import QAAgent

router = APIRouter()

pm_agent = ProductManagerAgent()
dev_agent = DeveloperAgent()
qa_agent = QAAgent()

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Architect agent provides breakdown details for the phase
    try:
        architect_agent = ArchitectAgent()
        phase_description, task_description, system_design, tech_stack, performance_metrics = architect_agent(phase1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Architect breakdown failed: {e}")

    # Developer Agent requirement loop
    try:
        architect_answers = ""  # Initialize with any pre-known answers or empty

        while True:
            check_result = dev_agent.check_input_sufficiency(
                phase_description, task_description, system_design, tech_stack, performance_metrics, architect_answers
            )
            arch_required = check_result.get("architecht_required", True)
            questions = check_result.get("questions_to_architecht", [])

            if not arch_required:
                # Inputs sufficient, proceed to generate code
                code_result = dev_agent.generate_code(
                    phase_description, task_description, system_design, tech_stack, performance_metrics, architect_answers
                )
                break  # Exit loop after code generation

            if questions:
                # Send questions to Architect Agent and get response
                print("Sending questions to Architect Agent:")
                for q in questions:
                    print("-", q)
                architect_response = architect_agent.answer_questions(questions)
                # Update the architect_answers with new responses
                architect_answers += "\n" + architect_response
            else:
                # No questions despite arch_required = True - prevent infinite loop
                raise RuntimeError("Architect required but no questions provided to ask.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Developer agent failed: {e}")

    # QA Agent call after code generation
    try:
        # Gather everything needed for QA agent input
        code = code_result.get("code", "")
        requirements_txt = code_result.get("requirements.txt", "")
        input_output = code_result.get("input_output", "")

        # qa_agent call
        test_cases = qa_agent.generate_test_cases(
            phase_description,
            task_description,
            system_design,
            tech_stack,
            performance_metrics,
            architect_answers,
            code,
            requirements_txt,
            input_output
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA agent failed: {e}")

    # Final response (add more as needed)
    return {
        "success": True,
        "project_plan": structured_output,
        "phase1_details": phase1,
        "code": code_result,
        "test_cases": test_cases
    }
