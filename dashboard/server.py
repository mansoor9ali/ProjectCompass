"""
Dashboard server for the ProjectCompass system.
Provides web-based visualization and control of the inquiry management system.
"""
import logging
import os
import threading
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Initialize logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ProjectCompass Dashboard", description="Vendor Inquiry Management System")

# Setup templates and static files directories
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Add static files directory if it exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# In-memory data store for demo (in production this would connect to a database)
system_status = {
    "status": "operational",
    "active_inquiries": 0,
    "total_inquiries": 0,
    "notifications_sent": 0
}

# Simulated agent manager for the dashboard
agent_manager = None

# Create Pydantic models for request/response validation
class InquiryRequest(BaseModel):
    """Model for submitting a new inquiry."""
    from_email: str
    from_name: Optional[str] = None
    subject: str
    content: str
    category: Optional[str] = None
    priority: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """Model for system status response."""
    status: str
    active_inquiries: int
    total_inquiries: int
    notifications_sent: int
    performance_metrics: Optional[Dict[str, Any]] = None


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get the current system status."""
    global system_status
    
    # If we have an agent manager, get real metrics
    metrics = None
    if agent_manager:
        try:
            metrics = agent_manager.get_system_metrics()
            
            # Update system status from metrics
            system_status["active_inquiries"] = metrics["queue"]["current_queue_size"]
            system_status["total_inquiries"] = metrics["system"]["inquiries_processed"]
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
    
    return {
        **system_status,
        "performance_metrics": metrics
    }


@app.get("/api/inquiries/recent", response_class=JSONResponse)
async def get_recent_inquiries(limit: int = 10):
    """Get recent inquiries."""
    # This would fetch from a database in a real implementation
    # For demo purposes, return simulated data
    
    if agent_manager:
        try:
            # In a real implementation, would call agent_manager.get_recent_inquiries()
            pass
        except Exception as e:
            logger.error(f"Error getting recent inquiries: {str(e)}")
    
    # Return simulated data for now
    return {
        "inquiries": [
            {
                "id": "INQ-12345ABC",
                "vendor_name": "Acme Corp",
                "subject": "Prequalification Application Status",
                "category": "prequalification",
                "priority": "medium",
                "status": "assigned",
                "assigned_to": "registration.specialist@example.com",
                "created_at": "2025-03-29T08:30:00Z"
            },
            {
                "id": "INQ-67890DEF",
                "vendor_name": "TechSupplies Inc",
                "subject": "Invoice Payment Issue",
                "category": "finance",
                "priority": "high",
                "status": "in_progress",
                "assigned_to": "finance.senior@example.com",
                "created_at": "2025-03-29T10:15:00Z"
            }
        ],
        "total": 2
    }


@app.post("/api/inquiries/submit", response_class=JSONResponse)
async def submit_inquiry(inquiry: InquiryRequest):
    """Submit a new inquiry for processing."""
    global system_status
    
    try:
        # Log the submission
        logger.info(f"Manual inquiry submission: {inquiry.subject}")
        
        # In a real implementation, would process through the agent system
        # For demo purposes, just increment the counter
        system_status["total_inquiries"] += 1
        system_status["active_inquiries"] += 1
        
        return {
            "status": "success",
            "message": "Inquiry submitted successfully",
            "inquiry_id": f"INQ-MANUAL{system_status['total_inquiries']}"
        }
    except Exception as e:
        logger.error(f"Error submitting inquiry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/stats", response_class=JSONResponse)
async def get_department_stats():
    """Get statistics for departments."""
    # This would fetch from the routing service in a real implementation
    # For demo purposes, return simulated data
    
    return {
        "departments": [
            {"name": "Vendor Registration", "load": 5, "avg_response_time": 2.3},
            {"name": "Finance", "load": 8, "avg_response_time": 4.1},
            {"name": "Legal", "load": 3, "avg_response_time": 6.5},
            {"name": "Procurement", "load": 7, "avg_response_time": 3.2},
            {"name": "Technical Support", "load": 10, "avg_response_time": 1.5},
            {"name": "Vendor Relations", "load": 4, "avg_response_time": 2.8}
        ]
    }


@app.get("/api/categories/distribution", response_class=JSONResponse)
async def get_category_distribution():
    """Get distribution of inquiries by category."""
    # This would fetch from the monitoring agent in a real implementation
    # For demo purposes, return simulated data
    
    return {
        "categories": [
            {"name": "prequalification", "count": 15},
            {"name": "finance", "count": 23},
            {"name": "contract", "count": 8},
            {"name": "bidding", "count": 12},
            {"name": "issue", "count": 18},
            {"name": "information", "count": 10},
            {"name": "other", "count": 5}
        ]
    }


def run_dashboard_server(host="127.0.0.1", port=8000, agent_mgr=None):
    """
    Start the dashboard server.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        agent_mgr: Optional agent manager instance
    """

    print("Starting dashboard server")
    global agent_manager
    agent_manager = agent_mgr
    
    logger.info(f"Starting dashboard server at http://{host}:{port}")
    
    # Start Uvicorn server
    uvicorn.run(app, host=host, port=port)


def start_dashboard_in_thread(host="127.0.0.1", port=8000, agent_mgr=None):
    """
    Start the dashboard server in a separate thread.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        agent_mgr: Optional agent manager instance
    """
    global agent_manager
    agent_manager = agent_mgr
    
    # Create and start the thread
    dashboard_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host=host, port=port),
        daemon=True
    )
    
    dashboard_thread.start()
    logger.info(f"Dashboard server started in background thread at http://{host}:{port}")
    
    return dashboard_thread


# This allows the module to be run directly
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Start the server
    run_dashboard_server()
