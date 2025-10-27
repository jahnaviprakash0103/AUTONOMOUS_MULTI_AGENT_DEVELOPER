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
            r"C:\Users\D Harshavardhan\Desktop\config\config", "DEFAULT"
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
        """Divide a phase into week-by-week tasks, retrying if JSON parse fails."""
        phase_name = phase.get("phase_name", "Unnamed Phase")
        description = phase.get("description", "")

        prompt = f"""
        You are a Software Architect planning weekly execution tasks.

        Phase Name: {phase_name}
        Description: {description}

        Break this phase into detailed weekly tasks.
        Each week should have specific, actionable developer tasks.

        Respond strictly in JSON with this structure:
        {{
          "phase_name": "{phase_name}",
          "tasks_by_week": [
            {{
              "week": 1,
              "tasks": ["task1", "task2"]
            }},
            {{
              "week": 2,
              "tasks": ["task3", "task4"]
            }}
          ]
        }}
        """

        raw_output = self._query_llm(prompt)
        print(f"\n[ArchitectAgent] Raw output for phase '{phase_name}':\n{raw_output}\n")

        structured_output = parse_llm_json(raw_output)

        # Retry once if parsing fails
        if "tasks_by_week" not in structured_output and retries > 0:
            print(f"[ArchitectAgent] JSON parse failed for '{phase_name}'. Retrying...")
            time.sleep(2)
            return self.divide_phase_into_tasks(phase, retries=0)

        # Fallback if still not valid
        if "tasks_by_week" not in structured_output:
            structured_output = {
                "phase_name": phase_name,
                "tasks_by_week": [],
                "raw_response": raw_output
            }

        return structured_output

    def process_all_phases(self, phases: list) -> list:
        """Generate weekly breakdowns for each phase."""
        results = []
        for phase in phases:
            result = self.divide_phase_into_tasks(phase)
            results.append(result)
        return results
