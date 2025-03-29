"""
RESTful API for the ProjectCompass system.
Provides endpoints for external systems to interact with the inquiry management system.
"""
import logging
import os
import uvicorn
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import uuid

from models.inquiry import Inquiry, InquiryCategory, InquiryType, InquiryPriority, InquiryStatus, EmailMetadata
from agent_system.agent_manager import AgentManager
from services.email_processor import EmailProcessor
from services.prioritization_service import PrioritizationService
from services.routing_service import RoutingService
from data.repository import get_repository

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ProjectCompass API",
    description="Vendor Inquiry Management System API",
    version="1.0.0"
)

# Initialize repository
repository = get_repository()

# Initialize services
email_processor = EmailProcessor()
prioritization_service = PrioritizationService()
routing_service = RoutingService()

# Initialize agent manager
agent_manager = AgentManager(
    prioritization_service=prioritization_service,
    routing_service=routing_service
)

# Define request and response models
class EmailInquiryRequest(BaseModel):
    """Model for submitting an email inquiry."""
    from_email: str
    from_name: Optional[str] = None
    to_email: str
    cc: List[str] = []
    subject: str
    content: str
    date: Optional[str] = None
    has_attachments: bool = False
    attachment_count: int = 0
    attachment_names: List[str] = []
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None


class InquiryResponse(BaseModel):
    """Model for inquiry response."""
    id: str
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    subject: str
    category: str
    inquiry_type: Optional[str] = None
    priority: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    created_at: str
    updated_at: str
    due_by: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """Model for system status response."""
    status: str
    active_inquiries: int
    total_inquiries: int
    inquiries_by_category: Dict[str, int]
    inquiries_by_priority: Dict[str, int]
    inquiries_by_status: Dict[str, int]
    uptime_seconds: float


class ErrorResponse(BaseModel):
    """Model for error response."""
    error: str
    detail: Optional[str] = None


# API endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "ProjectCompass API",
        "version": "1.0.0",
        "description": "Vendor Inquiry Management System API"
    }


@app.post("/api/inquiries/email", response_model=Dict[str, Any], tags=["Inquiries"])
async def process_email_inquiry(email_data: EmailInquiryRequest):
    """
    Process an email inquiry.
    
    This endpoint accepts email data and processes it through the inquiry management system.
    """
    try:
        logger.info(f"Received email inquiry: {email_data.subject}")
        
        # Convert to format expected by email processor
        email_dict = {
            "from": f"{email_data.from_name} <{email_data.from_email}>" if email_data.from_name else email_data.from_email,
            "to": email_data.to_email,
            "cc": ",".join(email_data.cc),
            "subject": email_data.subject,
            "text": email_data.content,
            "date": email_data.date or datetime.now().isoformat(),
            "attachments": [{"filename": name} for name in email_data.attachment_names],
            "thread_id": email_data.thread_id,
            "in_reply_to": email_data.in_reply_to
        }
        
        # Process email
        inquiry = email_processor.process_email(email_dict)
        
        # Handle inquiry through agent system
        result = agent_manager.handle_inquiry(inquiry)
        
        # Save to repository
        repository.save_inquiry(inquiry)
        
        return {
            "status": "success",
            "inquiry_id": inquiry.id,
            "processing_result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing email inquiry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inquiries", response_model=Dict[str, Any], tags=["Inquiries"])
async def get_inquiries(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get inquiries with optional filtering.
    
    This endpoint returns a list of inquiries, which can be filtered by status, category, and priority.
    """
    try:
        # Prepare filters
        filters = {}
        if status:
            filters["status"] = status
        if category:
            filters["category"] = category
        
        # Get inquiries from repository
        inquiries = repository.get_inquiries(**filters, limit=limit, offset=offset)
        
        # Apply additional filtering (for priority, which is not supported by the repository directly)
        if priority and inquiries:
            inquiries = [inq for inq in inquiries if inq.get("priority") == priority]
        
        # Get total count
        total_count = repository.get_inquiry_count(status)
        
        return {
            "inquiries": inquiries,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting inquiries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inquiries/{inquiry_id}", response_model=Dict[str, Any], tags=["Inquiries"])
async def get_inquiry(inquiry_id: str):
    """
    Get a specific inquiry by ID.
    
    This endpoint returns the details of a specific inquiry.
    """
    try:
        inquiry = repository.get_inquiry(inquiry_id)
        
        if not inquiry:
            raise HTTPException(status_code=404, detail=f"Inquiry {inquiry_id} not found")
        
        return inquiry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inquiry {inquiry_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/inquiries/{inquiry_id}/status", response_model=Dict[str, Any], tags=["Inquiries"])
async def update_inquiry_status(inquiry_id: str, status: str):
    """
    Update the status of an inquiry.
    
    This endpoint updates the status of a specific inquiry.
    """
    try:
        # Validate status
        if status not in [s.value for s in InquiryStatus]:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        # Update status
        success = repository.update_inquiry_status(inquiry_id, status)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Inquiry {inquiry_id} not found")
        
        return {
            "inquiry_id": inquiry_id,
            "status": status,
            "updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inquiry status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/status", response_model=SystemStatusResponse, tags=["System"])
async def get_system_status():
    """
    Get the current system status.
    
    This endpoint returns the current status and metrics of the system.
    """
    try:
        # Get metrics from agent manager
        metrics = agent_manager.get_system_metrics()
        
        # Get inquiry counts
        active_inquiries = repository.get_inquiry_count(InquiryStatus.NEW.value) + \
                          repository.get_inquiry_count(InquiryStatus.CATEGORIZED.value) + \
                          repository.get_inquiry_count(InquiryStatus.PRIORITIZED.value) + \
                          repository.get_inquiry_count(InquiryStatus.ASSIGNED.value) + \
                          repository.get_inquiry_count(InquiryStatus.IN_PROGRESS.value)
        
        total_inquiries = repository.get_inquiry_count()
        
        # Get inquiry distribution by category
        inquiries_by_category = {}
        for category in InquiryCategory:
            inquiries_by_category[category.value] = repository.get_inquiry_count(category=category.value)
        
        # Get inquiry distribution by status
        inquiries_by_status = {}
        for status in InquiryStatus:
            inquiries_by_status[status.value] = repository.get_inquiry_count(status=status.value)
        
        # Get inquiry distribution by priority (not directly supported by repository)
        inquiries_by_priority = metrics["system"]["inquiries_by_priority"]
        
        return {
            "status": "operational",
            "active_inquiries": active_inquiries,
            "total_inquiries": total_inquiries,
            "inquiries_by_category": inquiries_by_category,
            "inquiries_by_priority": inquiries_by_priority,
            "inquiries_by_status": inquiries_by_status,
            "uptime_seconds": metrics["uptime_seconds"]
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Run API server if module is executed directly
if __name__ == "__main__":
    # Create data directories if they don't exist
    os.makedirs("data/storage", exist_ok=True)
    
    # Start API server
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8080"))
    
    logger.info(f"Starting ProjectCompass API server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
