"""
Amazon Aurora PostgreSQL Monitor
Monitors global database replication, backup freshness, and connection health
"""

from datetime import datetime
import random
from typing import Dict, Any

from src.monitors.base_monitor import BaseMonitor, HealthStatus


class AuroraMonitor(BaseMonitor):
    """Monitor for Amazon Aurora PostgreSQL"""
    
    async def check_health(self) -> HealthStatus:
        """Check Aurora PostgreSQL health"""
        
        if self.demo_mode:
            metrics = self._generate_demo_data()
        else:
            metrics = await self._collect_real_metrics()
        
        score = self._calculate_score(metrics)
        status = self._determine_status(score)
        alerts = self._generate_alerts(metrics, score)
        
        return HealthStatus(
            component="aurora",
            score=score,
            status=status,
            metrics=metrics,
            alerts=alerts,
            timestamp=datetime.now()
        )
    
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate realistic demo data"""
        # Simulate realistic Aurora metrics
        base_lag = 1.8  # Base replication lag in seconds
        lag_variation = random.uniform(-0.5, 1.5)
        replication_lag = max(0.1, base_lag + lag_variation)
        
        return {
            "primary_region": "us-east-1",
            "secondary_region": "us-west-2",
            "replication_lag_seconds": round(replication_lag, 2),
            "primary_connections": random.randint(45, 65),
            "secondary_connections": random.randint(5, 15),
            "backup_age_hours": round(random.uniform(0.5, 2.5), 1),
            "cpu_utilization_primary": round(random.uniform(35, 55), 1),
            "cpu_utilization_secondary": round(random.uniform(10, 25), 1),
            "storage_used_gb": random.randint(450, 550),
            "storage_total_gb": 1000,
            "global_database_status": "available",
            "primary_cluster_status": "available",
            "secondary_cluster_status": "available",
            "last_failover_test": "2024-01-15T10:30:00Z",
            "automatic_backups_enabled": True,
            "backup_retention_days": 7,
            "multi_az": True
        }
    
    async def _collect_real_metrics(self) -> Dict[str, Any]:
        """Collect real metrics from AWS (placeholder)"""
        # In production, this would use boto3 to collect real metrics
        return self._generate_demo_data()
    
    def _calculate_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate health score based on Aurora metrics"""
        score = 100.0
        
        # Replication lag penalty
        lag = metrics.get("replication_lag_seconds", 0)
        if lag > 10:
            score -= 20
        elif lag > 5:
            score -= 10
        elif lag > 3:
            score -= 5
        
        # Backup freshness penalty
        backup_age = metrics.get("backup_age_hours", 0)
        if backup_age > 24:
            score -= 15
        elif backup_age > 12:
            score -= 8
        elif backup_age > 6:
            score -= 3
        
        # CPU utilization check
        cpu_primary = metrics.get("cpu_utilization_primary", 0)
        if cpu_primary > 80:
            score -= 10
        elif cpu_primary > 70:
            score -= 5
        
        # Storage check
        storage_used = metrics.get("storage_used_gb", 0)
        storage_total = metrics.get("storage_total_gb", 1000)
        storage_percent = (storage_used / storage_total) * 100
        if storage_percent > 90:
            score -= 15
        elif storage_percent > 80:
            score -= 8
        
        # Cluster status check
        if metrics.get("global_database_status") != "available":
            score -= 30
        if metrics.get("primary_cluster_status") != "available":
            score -= 25
        if metrics.get("secondary_cluster_status") != "available":
            score -= 20
        
        return max(0, min(100, score))
    
    def _generate_alerts(self, metrics: Dict[str, Any], score: float) -> list:
        """Generate Aurora-specific alerts"""
        alerts = []
        
        lag = metrics.get("replication_lag_seconds", 0)
        if lag > 5:
            alerts.append({
                "severity": "critical" if lag > 10 else "warning",
                "message": f"Aurora replication lag is {lag}s (threshold: 5s)",
                "recommendation": "Check network connectivity and secondary cluster performance",
                "impact": f"RPO may increase to {int(lag)} seconds"
            })
        
        backup_age = metrics.get("backup_age_hours", 0)
        if backup_age > 6:
            alerts.append({
                "severity": "warning" if backup_age < 12 else "critical",
                "message": f"Last backup is {backup_age} hours old",
                "recommendation": "Verify automatic backup configuration",
                "impact": "Increased data loss risk in DR scenario"
            })
        
        cpu_primary = metrics.get("cpu_utilization_primary", 0)
        if cpu_primary > 70:
            alerts.append({
                "severity": "warning",
                "message": f"Primary cluster CPU at {cpu_primary}%",
                "recommendation": "Consider scaling up instance size or optimizing queries",
                "impact": "May affect replication performance"
            })
        
        return alerts

# Made with Bob
