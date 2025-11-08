# agents/pm_agent.py
import oci
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def parse_llm_json(raw_text: str):
    """
    Cleans LLM response and converts it into a Python dict.
    Handles Markdown-style ```json blocks and fixes common typos in keys.
    """
    # Remove ```json and ``` if present
    cleaned = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()

    try:
        data = json.loads(cleaned)

        # Fix common key typo: "phase_nane" -> "phase_name"
        if "phases" in data:
            for phase in data["phases"]:
                if "phase_nane" in phase:
                    phase["phase_name"] = phase.pop("phase_nane")

        return data
    except json.JSONDecodeError:
        return {"text_response": raw_text}


class ProductManagerAgent:
    def __init__(self):
        # Load values from environment variables
        self.compartment_id = os.getenv("COMPARTMENT_ID")
        self.model_id = os.getenv("MODEL_ID")
        config_profile = os.getenv("CONFIG_PROFILE", "DEFAULT")
        endpoint = os.getenv(
            "OCI_REGION_ENDPOINT",
            "https://inference.generativeai.ap-hyderabad-1.oci.oraclecloud.com"
        )

        # OCI client setup
        config = oci.config.from_file(
            r"C:\Users\Jahnavi Prakash\Downloads\config", config_profile
        )
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240)
        )

    def _query_llm(self, user_prompt: str) -> str:
        """Send prompt to OCI LLM and return raw response text."""
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_request = oci.generative_ai_inference.models.CohereChatRequest()

        chat_request.message = user_prompt
        chat_request.max_tokens = 600
        chat_request.temperature = 0.7
        chat_request.top_p = 0.75
        chat_request.top_k = 0
        chat_request.frequency_penalty = 0

        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=self.model_id
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = self.compartment_id

        response = self.client.chat(chat_detail)
        return response.data.chat_response.text

    def process_project_idea(self, project_idea: str) -> dict:
        """
        Takes a user project idea, asks OCI LLM to generate development phases,
        and returns structured JSON.
        """
        prompt = f"""
        You are a Product Manager.
        # Given the following project idea, give only one phase.

        For each phase, include:
        - phase_name
        - description

        Return the output strictly in JSON format with this structure:
        {{
          "project_title": "<title>",
          "phases": [
            {{"phase_name": "", "description": ""}},
            ...
          ]
        }}

        Project idea:
        {project_idea}
        """

        raw_output = self._query_llm(prompt)
        structured_output = parse_llm_json(raw_output)

        return structured_output

    def send_phase_to_architect(self, structured_output: dict) -> dict:
        """
        Extract Phase 1 details and simulate sending to Architect Agent.
        """
        if "phases" not in structured_output or not structured_output["phases"]:
            return {"error": "No phases generated."}

        phase1 = structured_output["phases"][0]
        print("\n--- Sending Phase 1 to Architect Agent ---")
        print(json.dumps(phase1, indent=2))
        return phase1
