"""
API server for the ProjectCompass system.
Provides RESTful endpoints for the inquiry management system.
"""
import logging
import os
import threading
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Import the repository to access database data
from data.repository import get_repository

# Initialize logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ProjectCompass API", 
    description="Vendor Inquiry Management System",
    version="1.0.0"
)

# In-memory data store for demo (in production this would connect to a database)
system_status = {
    "status": "operational",
    "active_inquiries": 0,
    "total_inquiries": 0,
    "notifications_sent": 0
}

# Simulated agent manager for the API
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


@app.get("/")
async def root():
    """API root endpoint with basic information."""
    return {
        "name": "ProjectCompass API",
        "version": "1.0.0",
        "description": "Vendor Inquiry Management System API",
        "endpoints": [
            "/api/system/status",
            "/api/inquiries/recent",
            "/api/inquiries/submit",
            "/api/departments/stats",
            "/api/categories/distribution"
        ]
    }


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


@app.get("/api/inquiries/recent")
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


@app.post("/api/inquiries/submit")
async def submit_inquiry(inquiry: InquiryRequest):
    """Submit a new inquiry for processing."""
    global system_status
    
    try:
        # Log the submission
        logger.info(f"Manual inquiry submission: {inquiry.subject}")
        
        # This would process the inquiry in a real implementation
        # For now, just increment the count
        system_status["active_inquiries"] += 1
        system_status["total_inquiries"] += 1
        
        return {
            "status": "success",
            "inquiry_id": f"INQ-{os.urandom(4).hex().upper()}",
            "message": "Inquiry received and being processed"
        }
    except Exception as e:
        logger.error(f"Error submitting inquiry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/stats")
async def get_department_stats():
    """Get statistics for departments."""
    try:
        # Get the repository instance
        repository = get_repository()
        
        # Get departments from the database
        departments = repository.get_departments()
        
        # Transform the data to match the expected format for the frontend
        transformed_departments = []
        for dept in departments:
            transformed_departments.append({
                "name": dept["name"],
                "inquiry_count": dept["inquiry_count"],
                "avg_response_time": dept["avg_response_time"],
                "load": dept["load"]
            })
        
        logger.info(f"Retrieved {len(transformed_departments)} departments")
        return {
            "departments": transformed_departments
        }
    except Exception as e:
        logger.error(f"Error retrieving department stats: {str(e)}")
        # Fallback to static data in case of error
        return {
            "departments": [
                {"name": "Registration", "inquiry_count": 42, "avg_response_time": 8.5, "load": 65},
                {"name": "Finance", "inquiry_count": 27, "avg_response_time": 12.3, "load": 45},
                {"name": "Contracts", "inquiry_count": 19, "avg_response_time": 24.7, "load": 35},
                {"name": "Technical Support", "inquiry_count": 35, "avg_response_time": 4.2, "load": 55}
            ]
        }


@app.get("/api/categories/distribution")
async def get_category_distribution():
    """Get distribution of inquiries by category."""
    try:
        # Get the repository instance
        repository = get_repository()
        
        # Get categories from the database
        categories = repository.get_categories()
        
        # Transform the data to match the expected format for the frontend
        transformed_categories = []
        for cat in categories:
            transformed_categories.append({
                "name": cat["name"],
                "count": cat["count"],
                "percentage": cat["percentage"]
            })
        
        logger.info(f"Retrieved {len(transformed_categories)} categories")
        return {
            "categories": transformed_categories
        }
    except Exception as e:
        logger.error(f"Error retrieving category distribution: {str(e)}")
        # Fallback to static data in case of error
        return {
            "categories": [
                {"name": "prequalification", "count": 30, "percentage": 25},
                {"name": "finance", "count": 24, "percentage": 20},
                {"name": "contract", "count": 18, "percentage": 15},
                {"name": "bidding", "count": 12, "percentage": 10},
                {"name": "technical", "count": 24, "percentage": 20},
                {"name": "information", "count": 12, "percentage": 10}
            ]
        }


@app.post("/api/stats/categories/{category_id}")
async def update_category(category_id: str, data: Dict[str, Any]):
    """Update a category's information."""
    try:
        repository = get_repository()
        success = repository.update_category(category_id, data)
        
        if success:
            # Recalculate percentages after updating a category
            repository.recalculate_category_percentages()
            return {"status": "success", "message": f"Category {category_id} updated successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stats/departments/{department_id}")
async def update_department(department_id: str, data: Dict[str, Any]):
    """Update a department's information."""
    try:
        repository = get_repository()
        success = repository.update_department(department_id, data)
        
        if success:
            return {"status": "success", "message": f"Department {department_id} updated successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    except Exception as e:
        logger.error(f"Error updating department: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def run_dashboard_server(host="127.0.0.1", port=8000, agent_mgr=None):
    """
    Start the API server.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        agent_mgr: Optional agent manager instance
    """
    print(f"Starting ProjectCompass API server")
    global agent_manager
    agent_manager = agent_mgr
    
    logger.info(f"Starting API server at http://{host}:{port}")
    
    # Start Uvicorn server
    uvicorn.run(app, host=host, port=port)


def start_dashboard_in_thread(host="127.0.0.1", port=8000, agent_mgr=None):
    """
    Start the API server in a separate thread.
    
    Args:
        host: Host to listen on
        port: Port to listen on
        agent_mgr: Optional agent manager instance
    """
    global agent_manager
    agent_manager = agent_mgr
    
    # Create and start the thread
    server_thread = threading.Thread(
        target=run_dashboard_server,
        args=(host, port, agent_mgr),
        daemon=True
    )
    server_thread.start()
    
    logger.info(f"API server thread started at http://{host}:{port}")
    return server_thread


# This allows the module to be run directly
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get configuration from environment variables or use defaults
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", "8000"))
    
    print(f"Starting ProjectCompass API server at http://{host}:{port}")
    print(f"Press Ctrl+C to stop the server")
    
    # Run the server
    run_dashboard_server(host=host, port=port)
