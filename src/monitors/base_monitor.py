"""
Base Monitor Class for all component monitors
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
import random


@dataclass
class HealthStatus:
    """Health status data class"""
    component: str
    score: float  # 0-100
    status: str  # healthy, warning, critical
    metrics: Dict[str, Any]
    alerts: List[Dict[str, str]]
    timestamp: datetime


class BaseMonitor(ABC):
    """Base class for all component monitors"""
    
    def __init__(self, settings, demo_mode: bool = False):
        self.settings = settings
        self.demo_mode = demo_mode
        self.component_name = self.__class__.__name__.replace("Monitor", "").lower()
    
    @abstractmethod
    async def check_health(self) -> HealthStatus:
        """Check health of the component"""
        pass
    
    def _calculate_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate health score based on metrics"""
        # Default implementation - override in subclasses
        return 95.0
    
    def _determine_status(self, score: float) -> str:
        """Determine status based on score"""
        if score >= 90:
            return "healthy"
        elif score >= 75:
            return "warning"
        else:
            return "critical"
    
    def _generate_alerts(self, metrics: Dict[str, Any], score: float) -> List[Dict[str, str]]:
        """Generate alerts based on metrics"""
        alerts = []
        
        if score < 90:
            alerts.append({
                "severity": "warning" if score >= 75 else "critical",
                "message": f"{self.component_name} health score below threshold: {score}%",
                "recommendation": f"Review {self.component_name} metrics and logs"
            })
        
        return alerts
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate realistic demo data for testing"""
        # Override in subclasses for component-specific demo data
        return {}

# Made with Bob
