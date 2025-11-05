import oci
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

def parse_llm_json(raw_text: str):
    cleaned = re.sub(r"``````", "", raw_text, flags=re.IGNORECASE).strip()
    try:
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError:
        return {"text_response": raw_text}

class DeveloperAgent:
    def __init__(self):
        self.compartment_id = os.getenv("COMPARTMENT_ID")
        self.model_id = os.getenv("MODEL_ID")
        config_profile = os.getenv("CONFIG_PROFILE", "DEFAULT")
        endpoint = os.getenv(
            "OCI_REGION_ENDPOINT",
            "https://inference.generativeai.ap-hyderabad-1.oci.oraclecloud.com"
        )
        config = oci.config.from_file(
            os.getenv("OCI_CONFIG_PATH", "~/.oci/config"), config_profile
        )
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240)
        )

    def _query_llm(self, user_prompt: str) -> str:
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_request = oci.generative_ai_inference.models.CohereChatRequest()

        chat_request.message = user_prompt
        chat_request.max_tokens = 1500  # increased token budget
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
    

    def check_input_sufficiency(self, phase_description, task_description, system_design, tech_stack, performance_metrics, architect_answers):
        prompt = f"""
You are a highly skilled, expert AI system analyst. Your task is to evaluate the sufficiency of the provided inputs for generating a robust, well-working system.

Given these inputs:
Phase:
\"\"\"{phase_description}\"\"\"

Task:
\"\"\"{task_description}\"\"\"

System Design:
\"\"\"{system_design}\"\"\"

Tech Stack:
\"\"\"{tech_stack}\"\"\"

Desired Performance Metrics:
\"\"\"{performance_metrics}\"\"\"

Other required information:
\"\"\"{architect_answers}\"\"\"

Based on the above, analyze whether these inputs are sufficient to generate a robust, production-ready system. Only mark "architecht_required" as true if major architectural, security, scalability, compliance, or functional details are missing or ambiguous.

If all critical elements required to design and implement a secure, scalable, compliant, production-quality solution are described above, then set "architecht_required": false.

Accept answers that follow common industry best practices unless there are clear, unresolved gaps.
Do not ask for additional details or clarification unless *absolutely necessary* for a competent developer to proceed.

Respond ONLY with a JSON object with keys:
{
  "architecht_required": true or false,
  "questions_to_architecht": [] if false, else list of clarifying questions or additional requirements
}

Do not repeat questions that have already been answered or covered.

No extra text or explanation.
"""
        raw_response = self._query_llm(prompt)
        return parse_llm_json(raw_response)

    def generate_code(self, phase_description, task_description, system_design, tech_stack, performance_metrics, architect_answers):
        prompt = f"""
You are a highly skilled software developer AI agent. Your task is to generate high-quality, production-ready code and all necessary artifacts based on the given inputs.

Given these inputs:
Phase:
\"\"\"{phase_description}\"\"\"

Task:
\"\"\"{task_description}\"\"\"

System Design:
\"\"\"{system_design}\"\"\"

Tech Stack:
\"\"\"{tech_stack}\"\"\"

Desired Performance Metrics:
\"\"\"{performance_metrics}\"\"\"

Other required information:
\"\"\"{architect_answers}\"\"\"

Generate a JSON response ONLY:

{{
  "code": "<Complete and runnable source code>",
  "requirements.txt": "<dependencies list>",
  "input_output": {{
      "input": "<Input description for testing>",
      "expected_output": "<Expected outputs>"
  }}
}}

Requirements:

- The "code" field must contain all code needed to implement the task and should be ready for deployment or testing.
- The "requirements.txt" should list only relevant Python libraries with specific versions if known or commonly used.
- The "input_output" section must clearly define the format, types, and example values where applicable.
- Provide no extra explanation or text outside of the JSON object.
- Your JSON must be syntactically correct and parsable.

Generate the entire JSON response concisely and precisely. Aim for clarity, correctness, and completeness.
No extra text or explanation outside the JSON.
"""
        raw_response = self._query_llm(prompt)
        return parse_llm_json(raw_response)