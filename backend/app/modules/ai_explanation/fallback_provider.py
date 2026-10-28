from app.modules.ai_explanation.provider import AIProvider

class FallbackProvider(AIProvider):
    async def generate_explanation(self, payload: dict) -> str:
        """
        Provides a deterministic fallback explanation when the AI API is unavailable.
        """
        score = payload.get("risk_score", 0)
        level = payload.get("risk_level", "UNKNOWN")
        strategy = payload.get("strategy", "UNKNOWN")
        services = payload.get("affected_services", [])
        
        explanation = f"The change carries a {level} risk score of {score}. "
        
        if services:
            explanation += f"It affects the following services: {', '.join(services)}. "
            
        explanation += f"Due to these factors, a {strategy} deployment strategy is recommended to ensure safety."
        
        return explanation
