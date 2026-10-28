from typing import List, Any
from app.schemas.change_detection import ChangeItem
from app.schemas.dependency_analysis import ImpactResponse
from app.schemas.risk_analysis import RiskFactor, RiskResponse
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.core.database import SessionLocal
from app.models.risk_rule import RiskRule

DEFAULT_RULES_DATA = [
    {
        "rule_name": "Replica Reduction",
        "change_type": "REPLICA_REDUCTION",
        "score": 20,
        "path_keyword": None,
        "reason_template": "Replicas reduced from {old} to {new}"
    },
    {
        "rule_name": "Memory Reduction",
        "change_type": "MEMORY_REDUCTION",
        "score": 20,
        "path_keyword": None,
        "reason_template": "Memory limits/requests reduced from {old} to {new}"
    },
    {
        "rule_name": "Missing Probe",
        "change_type": "REMOVED",
        "path_keyword": "probe",
        "score": 15,
        "reason_template": "Health probe removed at path: {path}"
    },
    {
        "rule_name": "Missing Liveness",
        "change_type": "REMOVED",
        "path_keyword": "liveness",
        "score": 15,
        "reason_template": "Health probe removed at path: {path}"
    },
    {
        "rule_name": "Missing Readiness",
        "change_type": "REMOVED",
        "path_keyword": "readiness",
        "score": 15,
        "reason_template": "Health probe removed at path: {path}"
    },
    {
        "rule_name": "Security Context Modified",
        "change_type": "MODIFIED",
        "path_keyword": "securitycontext",
        "score": 10,
        "reason_template": "Modified security context at path: {path}"
    },
    {
        "rule_name": "Privileged Escapation",
        "change_type": "MODIFIED",
        "path_keyword": "privileged",
        "score": 10,
        "reason_template": "Modified security context at path: {path}"
    }
]

class RiskEngine:
    def __init__(self, blast_calculator: BlastRadiusCalculator):
        self.blast_calculator = blast_calculator

    def _get_rules(self) -> List[Any]:
        rules = []
        try:
            from app.core.database import Base, engine as db_engine
            Base.metadata.create_all(bind=db_engine)
            db = SessionLocal()
            rules = db.query(RiskRule).all()
            if not rules:
                for r_data in DEFAULT_RULES_DATA:
                    db.add(RiskRule(**r_data))
                db.commit()
                rules = db.query(RiskRule).all()
            db.close()
        except Exception:
            pass

        if not rules:
            class InMemRule:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
            rules = [InMemRule(**r_data) for r_data in DEFAULT_RULES_DATA]
        return rules

    def evaluate(self, changed_resource: str, changes: List[ChangeItem], impact: ImpactResponse) -> RiskResponse:
        factors: List[RiskFactor] = []
        total_score = 0
        
        blast_radius = self.blast_calculator.calculate(impact)
        
        # Load rules from DB with fallback
        rules = self._get_rules()
        
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
