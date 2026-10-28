from app.schemas.deployment_strategy import RecommendationRequest, RecommendationResponse

class DeploymentStrategyAdvisor:
    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        level = request.risk_level.upper()
        
        if level == "LOW":
            return RecommendationResponse(
                strategy="ROLLING",
                initial_percentage=100,
                requires_approval=False,
                reason="Low risk change, safe for a standard rolling update."
            )
        elif level == "MEDIUM":
            return RecommendationResponse(
                strategy="CANARY",
                initial_percentage=25,
                requires_approval=False,
                reason="Medium risk change, recommending a 25% canary deployment to monitor impact."
            )
        elif level == "HIGH":
            return RecommendationResponse(
                strategy="CANARY",
                initial_percentage=10,
                requires_approval=False,
                reason="High-risk change with significant dependency impact. Recommending a cautious 10% canary deployment."
            )
        elif level == "CRITICAL":
            return RecommendationResponse(
                strategy="CANARY",
                initial_percentage=5,
                requires_approval=True,
                reason="Critical risk change affecting core infrastructure. Requires explicit approval and a minimal 5% canary deployment."
            )
        else:
            return RecommendationResponse(
                strategy="ROLLING",
                initial_percentage=100,
                requires_approval=False,
                reason="Default fallback strategy."
            )
