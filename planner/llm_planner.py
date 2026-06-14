from langchain_community.llms import Ollama
import json


class LLMPlanner:
    def __init__(self):
        try:
            self.llm = Ollama(model="phi3")
        except:
            self.llm = None

    def generate_plan(self, command, detections, context=None):

        # 🚫 If LLM not available → skip
        if self.llm is None:
            return None

        try:
            prompt = f"""
Convert this command into JSON:

COMMAND: {command}

Return ONLY:
{{
  "action": "pick|drop|move|bring",
  "object": "string or null"
}}
"""

            response = self.llm.invoke(prompt)

            start = response.find("{")
            end = response.rfind("}") + 1

            return json.loads(response[start:end])

        except:
            return None