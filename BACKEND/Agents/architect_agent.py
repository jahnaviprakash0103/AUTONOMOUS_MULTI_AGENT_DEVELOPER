import oci
import json
import re
import time

def parse_llm_json(raw_text: str):
    """Parse LLM JSON safely, removing markdown artifacts."""
    cleaned = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_text": raw_text}


class ArchitectAgent:
    def __init__(self):
        self.compartment_id = "ocid1.compartment.oc1..aaaaaaaadg4huvdmy2wyjt2lkg5pl4wmi2gxabxwtckbzyoz7pjggidoau2a"
        self.model_id = "ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyapnibwg42qjhwaxrlqfpreueirtwghiwvv2whsnwmnlva"
        endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

        config = oci.config.from_file(
            r"C:\Users\Jahnavi Prakash\Downloads\config", "DEFAULT"
        )

        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240)
        )

    def _query_llm(self, prompt: str) -> str:
        """Send prompt to OCI LLM and return response."""
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_request = oci.generative_ai_inference.models.CohereChatRequest()

        chat_request.message = prompt
        chat_request.max_tokens = 800
        chat_request.temperature = 0.6
        chat_request.top_p = 0.75
        chat_request.top_k = 0

        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=self.model_id
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = self.compartment_id

        response = self.client.chat(chat_detail)
        return response.data.chat_response.text

    def divide_phase_into_tasks(self, phase: dict, retries: int = 1) -> dict:
        """Divide a phase into daily tasks for a single week."""
        phase_name = phase.get("phase_name", "Unnamed Phase")
        description = phase.get("description", "")

        prompt = f"""
You are a senior software architect planning a short development sprint.

Phase Name: {phase_name}
Description: {description}

This project has 3 total phases (each = 1 week). 
For this phase, generate a simple plan for ONE week, broken into daily tasks (Day 1 to Day 5).
Each day should have clear, actionable developer tasks.

Also include:
- system_design: brief explanation of the high-level architecture
- tech_stack: list of main tools and technologies
- performance_metrics: 2–3 measurable KPIs

Respond strictly in valid JSON like this:
{{
  "phase_name": "{phase_name}",
  "system_design": "Short summary of design decisions",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "performance_metrics": ["API latency <200ms", "95% uptime"],
  "tasks_by_day": [
    {{"day": 1, "tasks": ["Task 1", "Task 2"]}},
    {{"day": 2, "tasks": ["Task 3", "Task 4"]}},
    {{"day": 3, "tasks": ["Task 5"]}},
    {{"day": 4, "tasks": ["Task 6"]}},
    {{"day": 5, "tasks": ["Testing", "Code review"]}}
  ]
}}
"""

        raw_output = self._query_llm(prompt)
        print(f"\n[ArchitectAgent] Raw output for phase '{phase_name}':\n{raw_output}\n")

        structured_output = parse_llm_json(raw_output)

        # Retry once if parsing fails
        if "tasks_by_day" not in structured_output and retries > 0:
            print(f"[ArchitectAgent] JSON parse failed for '{phase_name}'. Retrying...")
            time.sleep(2)
            return self.divide_phase_into_tasks(phase, retries=0)

        # Fallback if still invalid
        if "tasks_by_day" not in structured_output:
            structured_output = {
                "phase_name": phase_name,
                "system_design": "Not generated",
                "tech_stack": [],
                "performance_metrics": [],
                "tasks_by_day": [],
                "raw_response": raw_output
            }

        return structured_output

    def process_all_phases(self, phases: list) -> list:
        """Generate daily breakdown for each phase (1 week per phase)."""
        results = []
        for phase in phases:
            result = self.divide_phase_into_tasks(phase)
            results.append(result)
        return results
