import oci
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

def parse_llm_json_array(raw_text: str):
    # Remove markdown code fence if present (e.g. ``````)
    cleaned = re.sub(r"``````", "", raw_text, flags=re.IGNORECASE).strip()
    try:
        data = json.loads(cleaned)
        # Ensure it is an array of test case objects
        if isinstance(data, list):
            return data
        else:
            return {"text_response": raw_text}
    except json.JSONDecodeError:
        return {"text_response": raw_text}

class QAAgent:
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
        chat_request.max_tokens = 1800  # allow for a large set of tests
        chat_request.temperature = 0.3  # less creative, more precise
        chat_request.top_p = 0.8
        chat_request.top_k = 0
        chat_request.frequency_penalty = 0

        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=self.model_id
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = self.compartment_id

        response = self.client.chat(chat_detail)
        return response.data.chat_response.text

    def generate_test_cases(self, phase_description, task_description, system_design, tech_stack, performance_metrics, architect_answers, code, requirements_txt, input_output):
        prompt = f"""
You are a highly skilled software quality assurance (QA) engineer AI agent.

Given the following information about a system development task:

Phase:
"{phase_description}"

Task:
"{task_description}"

System Design:
"{system_design}"

Tech Stack:
"{tech_stack}"

Desired Performance Metrics:
"{performance_metrics}"

Other Architect Information:
"{architect_answers}"

Generated Code:
\"\"\"{code}\"\"\"

Dependencies (requirements.txt):
\"\"\"{requirements_txt}\"\"\"

Input and Expected Output Specification:
\"\"\"{input_output}\"\"\"

Your task is to generate a complete set of structured test cases to validate this system.

For each test case, produce a JSON object with these fields:

{{
  "test_case_id": "<unique identifier>",
  "description": "<brief description>",
  "preconditions": "<setup or initial state if any>",
  "steps": [
    "<step 1 description>",
    "<step 2 description>",
    "... etc."
  ],
  "expected_result": "<expected outcome or system response>"
}}

Ensure you cover functional scenarios, security testing, session and error handling, boundary/edge cases, and any performance considerations inferred from the inputs.

Return ONLY a JSON array of test case objects without any additional commentary or text.
"""
        raw_response = self._query_llm(prompt)
        return parse_llm_json_array(raw_response)

'''
# Example usage

if __name__ == "__main__":
    qa_agent = QAAgent()
    # Example variable content; replace with actual system values or model outputs
    phase_description = "User authentication and session management for a B2C ecommerce platform."
    task_description = "Implement secure user login, session handling, and authentication."
    system_design = "Microservices architecture, Auth Service, API Gateway, distributed Redis session store."
    tech_stack = "Python 3.11, FastAPI, PostgreSQL, Redis, Docker, NGINX."
    performance_metrics = "1000 logins/min, <200ms login latency, 99.9% uptime, 12h session expiration."
    architect_answers = "All compliance, security, scalability requirements from system architect as discussed previously."
    code = "# ... actual code string here ..."
    requirements_txt = "fastapi\nbcrypt\nredis\npsycopg2-binary\n"
    input_output = '{"input": "username, password", "expected_output": "success/fail message, JWT"}'

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

    print(json.dumps(test_cases, indent=2))
'''