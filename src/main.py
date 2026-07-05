"""
AI DR Readiness Validator - Main Application
Production deployment for IBM Guardium Insights SaaS
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path

from src.config.settings import Settings
from src.monitors.aurora_monitor import AuroraMonitor
from src.monitors.redis_monitor import RedisMonitor
from src.monitors.kafka_monitor import KafkaMonitor
from src.monitors.mongo_monitor import MongoMonitor
from src.monitors.redshift_monitor import RedshiftMonitor
from src.monitors.route53_monitor import Route53Monitor
from src.monitors.k8s_monitor import K8sMonitor
from src.ai.scoring import DRScoreCalculator
from src.ai.rto_rpo_predictor import RTORPOPredictor
from src.database.timescale import TimescaleDB
from src.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Global state
monitors = {}
db = None
score_calculator = None
rto_rpo_predictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global monitors, db, score_calculator, rto_rpo_predictor
    
    logger.info("Starting AI DR Readiness Validator...")
    
    # Initialize settings
    settings = Settings()
    
    # Initialize database
    db = TimescaleDB(settings)
    await db.connect()
    
    # Initialize monitors with demo data
    monitors = {
        "aurora": AuroraMonitor(settings, demo_mode=True),
        "redis": RedisMonitor(settings, demo_mode=True),
        "kafka": KafkaMonitor(settings, demo_mode=True),
        "mongo": MongoMonitor(settings, demo_mode=True),
        "redshift": RedshiftMonitor(settings, demo_mode=True),
        "route53": Route53Monitor(settings, demo_mode=True),
        "k8s": K8sMonitor(settings, demo_mode=True),
    }
    
    # Initialize AI components
    score_calculator = DRScoreCalculator()
    rto_rpo_predictor = RTORPOPredictor()
    
    logger.info("All components initialized successfully")
    
    # Start background monitoring task
    monitoring_task = asyncio.create_task(background_monitoring())
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI DR Readiness Validator...")
    monitoring_task.cancel()
    await db.disconnect()


# Create FastAPI app
app = FastAPI(
    title="AI DR Readiness Validator",
    description="Production DR monitoring system for IBM Guardium Insights SaaS",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def background_monitoring():
    """Background task to continuously monitor all components"""
    while True:
        try:
            logger.info("Running monitoring cycle...")
            
            # Collect metrics from all monitors
            for name, monitor in monitors.items():
                try:
                    health_status = await monitor.check_health()
                    await db.store_health_status(name, health_status)
                    logger.debug(f"{name} health: {health_status.score}%")
                except Exception as e:
                    logger.error(f"Error monitoring {name}: {e}")
            
            # Wait before next cycle (30 seconds)
            await asyncio.sleep(30)
            
        except asyncio.CancelledError:
            logger.info("Monitoring task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            await asyncio.sleep(30)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Serve dashboard"""
    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    with open(template_path, "r") as f:
        return f.read()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard endpoint"""
    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    with open(template_path, "r") as f:
        return f.read()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "monitors": len(monitors),
        "database": "connected" if db else "disconnected"
    }


@app.get("/api/v1/dr-score")
async def get_dr_score():
    """Get overall DR readiness score"""
    try:
        # Collect current health from all monitors
        component_scores = {}
        component_details = {}
        
        for name, monitor in monitors.items():
            health_status = await monitor.check_health()
            component_scores[name] = health_status.score
            component_details[name] = {
                "score": health_status.score,
                "status": health_status.status,
                "metrics": health_status.metrics,
                "timestamp": health_status.timestamp.isoformat()
            }
        
        # Calculate overall DR score
        overall_score = score_calculator.calculate_overall_score(component_scores)
        
        # Get RTO/RPO predictions
        rto_rpo = await rto_rpo_predictor.predict(component_scores)
        
        return {
            "overall_score": overall_score,
            "rto_minutes": rto_rpo["rto"],
            "rpo_minutes": rto_rpo["rpo"],
            "confidence": rto_rpo["confidence"],
            "components": component_details,
            "status": "healthy" if overall_score >= 90 else "warning" if overall_score >= 75 else "critical"
        }
        
    except Exception as e:
        logger.error(f"Error calculating DR score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/components/{component_name}")
async def get_component_health(component_name: str):
    """Get detailed health for a specific component"""
    if component_name not in monitors:
        raise HTTPException(status_code=404, detail=f"Component {component_name} not found")
    
    try:
        monitor = monitors[component_name]
        health_status = await monitor.check_health()
        
        return {
            "component": component_name,
            "score": health_status.score,
            "status": health_status.status,
            "metrics": health_status.metrics,
            "timestamp": health_status.timestamp.isoformat(),
            "alerts": health_status.alerts
        }
        
    except Exception as e:
        logger.error(f"Error getting component health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/history/{component_name}")
async def get_component_history(component_name: str, hours: int = 24):
    """Get historical data for a component"""
    if component_name not in monitors:
        raise HTTPException(status_code=404, detail=f"Component {component_name} not found")
    
    try:
        history = await db.get_history(component_name, hours)
        return {
            "component": component_name,
            "hours": hours,
            "data_points": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/alerts")
async def get_active_alerts():
    """Get all active alerts"""
    try:
        all_alerts = []
        
        for name, monitor in monitors.items():
            health_status = await monitor.check_health()
            if health_status.alerts:
                for alert in health_status.alerts:
                    all_alerts.append({
                        "component": name,
                        "severity": alert["severity"],
                        "message": alert["message"],
                        "recommendation": alert.get("recommendation", ""),
                        "timestamp": health_status.timestamp.isoformat()
                    })
        
        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        all_alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return {
            "total_alerts": len(all_alerts),
            "critical": len([a for a in all_alerts if a["severity"] == "critical"]),
            "warning": len([a for a in all_alerts if a["severity"] == "warning"]),
            "alerts": all_alerts
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/predictions")
async def get_predictions():
    """Get predictive insights for next 24 hours"""
    try:
        # Get current component scores
        component_scores = {}
        for name, monitor in monitors.items():
            health_status = await monitor.check_health()
            component_scores[name] = health_status.score
        
        # Get predictions
        predictions = await rto_rpo_predictor.get_predictions(component_scores)
        
        return {
            "predictions": predictions,
            "generated_at": predictions[0]["timestamp"] if predictions else None
        }
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/environments")
async def get_environments():
    """Get list of monitored environments"""
    return {
        "environments": [
            {
                "name": "dev",
                "clusters": ["sgi-dev01", "sgi-dev02", "sgi-dev03"],
                "regions": ["us-east-1", "us-west-2"],
                "status": "healthy"
            },
            {
                "name": "test",
                "clusters": ["sgi-preprod01"],
                "regions": ["us-east-1", "us-west-2"],
                "status": "healthy"
            },
            {
                "name": "prod",
                "clusters": ["sgi-prod01"],
                "regions": ["us-east-1", "us-west-2"],
                "status": "healthy"
            }
        ]
    }


@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get summary of all metrics"""
    try:
        summary = {
            "total_components": len(monitors),
            "healthy_components": 0,
            "warning_components": 0,
            "critical_components": 0,
            "average_score": 0.0,
            "data_points_today": 0
        }
        
        total_score = 0
        for name, monitor in monitors.items():
            health_status = await monitor.check_health()
            total_score += health_status.score
            
            if health_status.score >= 90:
                summary["healthy_components"] += 1
            elif health_status.score >= 75:
                summary["warning_components"] += 1
            else:
                summary["critical_components"] += 1
        
        summary["average_score"] = round(total_score / len(monitors), 2)
        summary["data_points_today"] = await db.get_data_points_count(hours=24)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Made with Bob
