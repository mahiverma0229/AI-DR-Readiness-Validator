"""Redshift Monitor"""
from datetime import datetime
import random
from src.monitors.base_monitor import BaseMonitor, HealthStatus

class RedshiftMonitor(BaseMonitor):
    async def check_health(self) -> HealthStatus:
        backup_age = round(random.uniform(0.5, 2.0), 1)
        metrics = {
            "snapshot_copy_age_hours": backup_age,
            "cluster_status": "available",
            "cpu_utilization": round(random.uniform(30, 50), 1),
            "storage_used_percent": round(random.uniform(55, 75), 1),
            "connections": random.randint(15, 35)
        }
        score = 92.0 + random.uniform(-3, 5)
        return HealthStatus("redshift", round(score, 1), self._determine_status(score), 
                          metrics, [], datetime.now())
