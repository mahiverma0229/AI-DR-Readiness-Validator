"""DR Score Calculator"""

class DRScoreCalculator:
    def __init__(self):
        self.weights = {
            "aurora": 0.20,
            "redis": 0.15,
            "kafka": 0.15,
            "mongo": 0.15,
            "redshift": 0.10,
            "route53": 0.10,
            "k8s": 0.15
        }
    
    def calculate_overall_score(self, component_scores: dict) -> float:
        weighted_sum = sum(
            component_scores.get(comp, 0) * weight
            for comp, weight in self.weights.items()
        )
        return round(weighted_sum, 2)
