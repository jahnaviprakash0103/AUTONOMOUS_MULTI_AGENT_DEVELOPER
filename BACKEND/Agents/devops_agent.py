# agents/devops_agent.py
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

class DevOpsAgent:
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
        chat_request.temperature = 0.5
        chat_request.top_p = 0.75
        chat_request.top_k = 0
        
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=self.model_id
        )
        chat_detail.chat_request = chat_request
        chat_detail.compartment_id = self.compartment_id
        
        response = self.client.chat(chat_detail)
        return response.data.chat_response.text
    
    def create_deployment_plan(self, project_info: dict, retries: int = 1) -> dict:
        """
        Create a comprehensive deployment plan based on project phases.
        """
        project_title = project_info.get("project_title", "Unnamed Project")
        phases = project_info.get("phases", [])
        
        phases_summary = "\n".join([
            f"- {p.get('phase_name', 'Unknown')}: {p.get('description', '')}"
            for p in phases
        ])
        
        prompt = f"""
        You are a DevOps Engineer planning deployment infrastructure.
        
        Project: {project_title}
        Development Phases:
        {phases_summary}
        
        Create a comprehensive DevOps plan including:
        1. Infrastructure requirements (servers, databases, storage)
        2. CI/CD pipeline setup
        3. Environment strategy (dev, staging, production)
        4. Monitoring and logging setup
        5. Security considerations
        6. Deployment strategy (blue-green, canary, rolling)
        
        Respond strictly in JSON with this structure:
        {{
          "project_title": "{project_title}",
          "infrastructure": {{
            "compute": ["server requirements"],
            "database": ["database requirements"],
            "storage": ["storage requirements"],
            "networking": ["network requirements"]
          }},
          "ci_cd_pipeline": {{
            "tools": ["CI/CD tools to use"],
            "stages": ["build", "test", "deploy"],
            "automation": ["automated tasks"]
          }},
          "environments": [
            {{
              "name": "development",
              "purpose": "description",
              "resources": ["resource list"]
            }},
            {{
              "name": "staging",
              "purpose": "description",
              "resources": ["resource list"]
            }},
            {{
              "name": "production",
              "purpose": "description",
              "resources": ["resource list"]
            }}
          ],
          "monitoring": {{
            "tools": ["monitoring tools"],
            "metrics": ["key metrics to track"],
            "alerts": ["alert configurations"]
          }},
          "security": {{
            "practices": ["security practices"],
            "tools": ["security tools"],
            "compliance": ["compliance requirements"]
          }},
          "deployment_strategy": {{
            "type": "blue-green|canary|rolling",
            "rollback_plan": "description",
            "steps": ["deployment steps"]
          }}
        }}
        """
        
        raw_output = self._query_llm(prompt)
        print(f"\n[DevOpsAgent] Raw output for deployment plan:\n{raw_output}\n")
        
        structured_output = parse_llm_json(raw_output)
        
        # Retry once if parsing fails
        if "infrastructure" not in structured_output and retries > 0:
            print(f"[DevOpsAgent] JSON parse failed. Retrying...")
            time.sleep(2)
            return self.create_deployment_plan(project_info, retries=0)
        
        # Fallback if still not valid
        if "infrastructure" not in structured_output:
            structured_output = {
                "project_title": project_title,
                "infrastructure": {},
                "ci_cd_pipeline": {},
                "environments": [],
                "monitoring": {},
                "security": {},
                "deployment_strategy": {},
                "raw_response": raw_output
            }
        
        return structured_output
    
    def create_phase_deployment(self, phase_tasks: dict, retries: int = 1) -> dict:
        """
        Create phase-specific deployment checklist based on weekly tasks.
        """
        phase_name = phase_tasks.get("phase_name", "Unnamed Phase")
        tasks_by_week = phase_tasks.get("tasks_by_week", [])
        
        tasks_summary = "\n".join([
            f"Week {week.get('week', '?')}: {', '.join(week.get('tasks', []))}"
            for week in tasks_by_week
        ])
        
        prompt = f"""
        You are a DevOps Engineer creating deployment checklists.
        
        Phase: {phase_name}
        Development Tasks:
        {tasks_summary}
        
        Create a deployment checklist for this phase including:
        1. Pre-deployment tasks
        2. Deployment steps
        3. Post-deployment validation
        4. Rollback procedures
        
        Respond strictly in JSON with this structure:
        {{
          "phase_name": "{phase_name}",
          "pre_deployment": [
            {{
              "task": "task description",
              "responsible": "role",
              "estimated_time": "duration"
            }}
          ],
          "deployment_steps": [
            {{
              "step": "step description",
              "command": "command if applicable",
              "verification": "how to verify"
            }}
          ],
          "post_deployment": [
            {{
              "check": "what to check",
              "expected_result": "expected outcome",
              "action_if_failed": "what to do if failed"
            }}
          ],
          "rollback_procedure": [
            "step 1",
            "step 2"
          ]
        }}
        """
        
        raw_output = self._query_llm(prompt)
        print(f"\n[DevOpsAgent] Raw output for phase '{phase_name}' deployment:\n{raw_output}\n")
        
        structured_output = parse_llm_json(raw_output)
        
        # Retry once if parsing fails
        if "pre_deployment" not in structured_output and retries > 0:
            print(f"[DevOpsAgent] JSON parse failed for '{phase_name}'. Retrying...")
            time.sleep(2)
            return self.create_phase_deployment(phase_tasks, retries=0)
        
        # Fallback if still not valid
        if "pre_deployment" not in structured_output:
            structured_output = {
                "phase_name": phase_name,
                "pre_deployment": [],
                "deployment_steps": [],
                "post_deployment": [],
                "rollback_procedure": [],
                "raw_response": raw_output
            }
        
        return structured_output
    
    def process_all_phases(self, architect_output: list) -> list:
        """
        Generate deployment checklists for each phase from architect output.
        """
        results = []
        for phase_tasks in architect_output:
            result = self.create_phase_deployment(phase_tasks)
            results.append(result)
        return results