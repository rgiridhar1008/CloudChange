from typing import List
from app.schemas.change_detection import ChangeItem
from app.schemas.dependency_analysis import ImpactResponse
from app.schemas.risk_analysis import RiskFactor, RiskResponse
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.core.database import SessionLocal
from app.models.risk_rule import RiskRule

class RiskEngine:
    def __init__(self, blast_calculator: BlastRadiusCalculator):
        self.blast_calculator = blast_calculator

    def evaluate(self, changed_resource: str, changes: List[ChangeItem], impact: ImpactResponse) -> RiskResponse:
        factors: List[RiskFactor] = []
        total_score = 0
        
        blast_radius = self.blast_calculator.calculate(impact)
        
        # Load rules from DB
        db = SessionLocal()
        rules = db.query(RiskRule).all()
        db.close()
        
        matched_changes = set()
        for rule in rules:
            for idx, change in enumerate(changes):
                if idx in matched_changes:
                    continue
                if change.type == rule.change_type:
                    factor_name = "Security Issue" if ("security" in rule.rule_name.lower() or "privileged" in rule.rule_name.lower()) else rule.rule_name
                    # If path_keyword is required, check if it's in the path
                    if rule.path_keyword:
                        if rule.path_keyword.lower() in change.path.lower():
                            reason = rule.reason_template.format(path=change.path, old=change.old, new=change.new)
                            factors.append(RiskFactor(
                                factor=factor_name,
                                score=rule.score,
                                reason=reason
                            ))
                            matched_changes.add(idx)
                            break # Only apply rule once per evaluation
                    else:
                        reason = rule.reason_template.format(path=change.path, old=change.old, new=change.new)
                        factors.append(RiskFactor(
                            factor=factor_name,
                            score=rule.score,
                            reason=reason
                        ))
                        matched_changes.add(idx)
                        break # Only apply rule once per evaluation
                
        # Rule 4: High Traffic (+15)
        if blast_radius.traffic_exposure == "EXTERNAL":
            factors.append(RiskFactor(
                factor="High Traffic",
                score=15,
                reason="Changed resource affects external ingress or gateway traffic"
            ))
            
        # Rule 5: Critical Service (+20)
        if blast_radius.criticality in ["HIGH", "CRITICAL"]:
            factors.append(RiskFactor(
                factor="Critical Service",
                score=20,
                reason=f"Impacts services with {blast_radius.criticality} criticality"
            ))
                
        # Calculate total score
        for f in factors:
            total_score += f.score
            
        total_score = min(total_score, 100)
        
        # Determine risk level
        if total_score <= 30:
            risk_level = "LOW"
        elif total_score <= 60:
            risk_level = "MEDIUM"
        elif total_score <= 80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        affected_resources = impact.affected_deployments + impact.affected_pods + impact.affected_apis
            
        return RiskResponse(
            risk_score=total_score,
            risk_level=risk_level,
            risk_factors=factors,
            blast_radius=blast_radius,
            affected_services=impact.affected_services,
            affected_resources=affected_resources
        )
