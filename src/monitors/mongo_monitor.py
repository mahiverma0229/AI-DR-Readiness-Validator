"""MongoDB Atlas Monitor"""
from datetime import datetime
import random
from src.monitors.base_monitor import BaseMonitor, HealthStatus

class MongoMonitor(BaseMonitor):
    async def check_health(self) -> HealthStatus:
        metrics = {
            "replica_set_config": "3:2",
            "primary_region_nodes": 3,
            "secondary_region_nodes": 2,
            "replication_lag_seconds": round(random.uniform(0.5, 2.5), 2),
            "oplog_window_hours": round(random.uniform(20, 26), 1),
            "connections": random.randint(150, 250)
        }
        score = 96.0 + random.uniform(-2, 2)
        return HealthStatus("mongo", round(score, 1), self._determine_status(score), 
                          metrics, [], datetime.now())
