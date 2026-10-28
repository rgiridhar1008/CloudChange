from app.core.config import settings
from app.modules.ai_explanation.provider import AIProvider
from app.modules.ai_explanation.fallback_provider import FallbackProvider
from app.modules.ai_explanation.openai_provider import OpenAIProvider

class AIExplanationService:
    def __init__(self):
        self.fallback_provider = FallbackProvider()
        self.primary_provider: AIProvider | None = None
        
        if settings.LLM_API_KEY:
            self.primary_provider = OpenAIProvider(settings.LLM_API_KEY)

    async def get_explanation(self, payload: dict) -> str:
        if self.primary_provider:
            try:
                # Attempt to get AI explanation
                return await self.primary_provider.generate_explanation(payload)
            except Exception as e:
                # Log exception and fall back
                print(f"AI Provider failed: {e}. Falling back to deterministic explanation.")
                
        # Always fallback if no provider or provider fails
        return await self.fallback_provider.generate_explanation(payload)
