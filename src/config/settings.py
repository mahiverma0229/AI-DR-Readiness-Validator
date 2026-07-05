"""
Configuration settings for AI DR Readiness Validator
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI DR Readiness Validator"
    environment: str = "production"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_secondary_region: str = "us-west-2"
    aws_account_id: str = "123456789012"
    
    # Database
    timescale_host: str = "localhost"
    timescale_port: int = 5432
    timescale_database: str = "dr_metrics"
    timescale_user: str = "postgres"
    timescale_password: str = "postgres"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Monitoring
    check_interval_seconds: int = 30
    data_retention_days: int = 90
    
    # Component Configuration
    # Aurora
    aurora_cluster_primary: str = "gi-prod01-aurora-cluster"
    aurora_cluster_secondary: str = "gi-prod01-aurora-cluster-secondary"
    
    # Redis ElastiCache
    redis_cluster_primary: str = "gi-prod01-redis"
    redis_cluster_secondary: str = "gi-prod01-redis-secondary"
    
    # MSK/Kafka
    msk_cluster_primary: str = "gi-prod01-msk"
    msk_cluster_secondary: str = "gi-prod01-msk-secondary"
    
    # MongoDB Atlas
    mongo_cluster_id: str = "cluster0"
    mongo_project_id: str = "66276176f74fcd55bb95269c"
    mongo_api_key: Optional[str] = None
    mongo_api_secret: Optional[str] = None
    
    # Redshift
    redshift_cluster: str = "gi-prod01-redshift"
    
    # Route53
    route53_hosted_zone_id: str = "Z1234567890ABC"
    
    # Kubernetes/OpenShift
    k8s_cluster: str = "sgi-prod01"
    k8s_namespace: str = "giaas"
    
    # Integrations
    slack_webhook_url: Optional[str] = None
    pagerduty_api_key: Optional[str] = None
    
    # AI/ML
    anomaly_detection_enabled: bool = True
    prediction_enabled: bool = True
    model_refresh_hours: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Made with Bob
