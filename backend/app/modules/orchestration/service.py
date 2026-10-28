from app.modules.change_detection.detector import ChangeDetector
from app.modules.dependency_analysis.analyzer import DependencyAnalyzer
from app.modules.dependency_analysis.impact import ImpactAnalyzer
from app.modules.risk_analysis.engine import RiskEngine
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.modules.deployment_strategy.advisor import DeploymentStrategyAdvisor
from app.modules.ai_explanation.service import AIExplanationService
from app.schemas.deployment_strategy import RecommendationRequest
from app.schemas.change_detection import ChangeRequest
from app.schemas.dependency_analysis import ImpactRequest
from app.schemas.risk_analysis import RiskRequest

class OrchestratorService:
    def __init__(self):
        self.change_detector = ChangeDetector()
        
        # Dependency Analysis
        self.dependency_analyzer = DependencyAnalyzer()
        graph = self.dependency_analyzer.get_graph()
        self.impact_analyzer = ImpactAnalyzer(graph)
        
        # Risk Analysis
        self.blast_calculator = BlastRadiusCalculator()
        self.risk_engine = RiskEngine(self.blast_calculator)
        
        self.deployment_advisor = DeploymentStrategyAdvisor()
        self.ai_explanation = AIExplanationService()

    async def analyze_change_pipeline(self, manifest_content: str, resource_name: str, old_manifest_content: str = "") -> dict:
        """
        Orchestrates the entire CloudChange analysis pipeline.
        """
        # 1. Detect Changes
        changes = self.change_detector.compare(old_manifest_content, manifest_content)
        
        # 2. Dependency & Impact Analysis
        impact = self.impact_analyzer.analyze(resource_name)
        
        # 3. Risk Engine
        risk_result = self.risk_engine.evaluate(resource_name, changes, impact)
        
        # 4. Deployment Advisor
        recommendation_req = RecommendationRequest(
            risk_score=risk_result.risk_score,
            risk_level=risk_result.risk_level,
            blast_radius=risk_result.blast_radius.model_dump() if hasattr(risk_result.blast_radius, 'model_dump') else risk_result.blast_radius.dict(),
            affected_services=risk_result.affected_services,
            criticality=risk_result.blast_radius.criticality
        )
        recommendation = self.deployment_advisor.recommend(recommendation_req)
        
        # 5. AI Explanation
        ai_payload = {
            "risk_score": risk_result.risk_score,
            "risk_level": risk_result.risk_level,
            "blast_radius": risk_result.blast_radius.model_dump() if hasattr(risk_result.blast_radius, 'model_dump') else risk_result.blast_radius.dict(),
            "affected_services": risk_result.affected_services,
            "strategy": recommendation.strategy,
            "reason": recommendation.reason
        }
        
        explanation = await self.ai_explanation.get_explanation(ai_payload)
        recommendation.explanation = explanation
        
        # 6. Combine all outputs
        return {
            "changes": changes,
            "impact": impact,
            "risk": risk_result,
            "recommendation": recommendation,
        }
