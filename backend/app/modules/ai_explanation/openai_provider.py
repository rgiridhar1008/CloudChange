import httpx
from app.modules.ai_explanation.provider import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # For this demonstration, we are constructing a generic LLM call.
        # This could easily be pointed at OpenAI's chat completions endpoint.
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def generate_explanation(self, payload: dict) -> str:
        if not self.api_key:
            raise ValueError("No API key provided for OpenAIProvider.")

        prompt = (
            "Explain the following Kubernetes configuration change in simple terms. "
            "Explain why the change is risky, what components may be affected, "
            "why the recommended deployment strategy was chosen, and what to monitor. "
            f"Context: {payload}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150
        }

        async with httpx.AsyncClient() as client:
            # We enforce a short timeout so it fails fast and falls back if key is invalid
            response = await client.post(self.endpoint, headers=headers, json=data, timeout=5.0)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
