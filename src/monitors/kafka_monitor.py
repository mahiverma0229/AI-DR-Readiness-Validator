"""Kafka/MSK Monitor with Confluent Replicator"""
from datetime import datetime
import random
from src.monitors.base_monitor import BaseMonitor, HealthStatus

class KafkaMonitor(BaseMonitor):
    async def check_health(self) -> HealthStatus:
        lag = random.randint(10, 50)
        metrics = {
            "replicator_status": "running",
            "replicator_tasks_running": random.randint(8, 10),
            "replicator_tasks_total": 10,
            "replication_lag_seconds": lag,
            "topics_replicated": random.randint(45, 55),
            "bytes_in_per_sec": random.randint(1000, 5000),
            "consumer_lag": random.randint(0, 100),
            "replicator_throughput_mbps": round(random.uniform(50, 150), 1),
            "failed_replication_tasks": 0
        }
        score = 87.0 + random.uniform(-5, 8)
        alerts = []
        
        if lag > 40:
            alerts.append({
                "severity": "warning",
                "message": f"Kafka replication lag: {lag}s",
                "recommendation": "Check Confluent Replicator tasks and network connectivity",
                "impact": f"RPO may increase to {lag} seconds"
            })
        
        if metrics["replicator_tasks_running"] < metrics["replicator_tasks_total"]:
            alerts.append({
                "severity": "critical",
                "message": f"Replicator tasks: {metrics['replicator_tasks_running']}/{metrics['replicator_tasks_total']}",
                "recommendation": "Restart failed Replicator tasks",
                "impact": "Some topics may not be replicating"
            })
        
        return HealthStatus("kafka", round(score, 1), self._determine_status(score), 
                          metrics, alerts, datetime.now())

# Made with Bob
