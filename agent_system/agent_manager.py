"""
Agent Manager for coordinating specialized agents in the ProjectCompass system.
"""
import logging
from typing import Dict, Any, Optional

from models.inquiry import Inquiry, InquiryStatus
from .analysis_agent import AnalysisAgent
from .prioritization_agent import PrioritizationAgent
from .routing_agent import RoutingAgent
from .notification_agent import NotificationAgent
from .monitoring_agent import MonitoringAgent

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Coordinates specialized agents to process vendor email inquiries.
    Acts as the central controller for the agent-based system.
    """
    
    def __init__(self, prioritization_service=None, routing_service=None):
        """Initialize the agent manager with necessary services."""
        logger.info("Initializing Agent Manager")
        
        # Initialize specialized agents
        self.analysis_agent = AnalysisAgent()
        self.prioritization_agent = PrioritizationAgent(prioritization_service)
        self.routing_agent = RoutingAgent(routing_service)
        self.notification_agent = NotificationAgent()
        self.monitoring_agent = MonitoringAgent()
        
        # System state
        self.active_inquiries: Dict[str, Inquiry] = {}
        
    def handle_inquiry(self, inquiry: Inquiry) -> Dict[str, Any]:
        """
        Process an inquiry through the complete agent workflow.
        
        Args:
            inquiry: The vendor inquiry to process
            
        Returns:
            Dictionary with processing results and status
        """
        try:
            # Track inquiry
            self.active_inquiries[inquiry.id] = inquiry
            self.monitoring_agent.log_activity("inquiry_received", {"inquiry_id": inquiry.id})
            
            # 1. Analyze and categorize the inquiry
            inquiry = self.analysis_agent.analyze_inquiry(inquiry)
            logger.info(f"Inquiry {inquiry.id} analyzed as {inquiry.category} - {inquiry.inquiry_type}")
            
            # 2. Prioritize the inquiry
            inquiry = self.prioritization_agent.prioritize_inquiry(inquiry)
            logger.info(f"Inquiry {inquiry.id} prioritized as {inquiry.priority}")
            
            # 3. Route the inquiry to the appropriate department/person
            inquiry, routing_result = self.routing_agent.route_inquiry(inquiry)
            logger.info(f"Inquiry {inquiry.id} routed to {inquiry.assigned_to}")
            
            # 4. Send notifications
            notification_result = self.notification_agent.send_inquiry_notifications(inquiry, routing_result)
            
            # Update monitoring metrics
            self.monitoring_agent.update_metrics(inquiry)
            
            # Update inquiry status
            inquiry.status = InquiryStatus.ASSIGNED
            self.active_inquiries[inquiry.id] = inquiry
            
            return {
                "inquiry_id": inquiry.id,
                "status": "success",
                "category": inquiry.category,
                "priority": inquiry.priority,
                "assigned_to": inquiry.assigned_to,
                "notifications_sent": notification_result.get("sent", False)
            }
            
        except Exception as e:
            logger.error(f"Error processing inquiry {inquiry.id}: {str(e)}")
            self.monitoring_agent.log_error("inquiry_processing", str(e), {"inquiry_id": inquiry.id})
            return {
                "inquiry_id": inquiry.id,
                "status": "error",
                "error_message": str(e)
            }
    
    def get_inquiry_status(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an inquiry."""
        inquiry = self.active_inquiries.get(inquiry_id)
        if not inquiry:
            return None
        
        return {
            "inquiry_id": inquiry.id,
            "status": inquiry.status,
            "category": inquiry.category,
            "priority": inquiry.priority,
            "assigned_to": inquiry.assigned_to,
            "created_at": inquiry.created_at,
            "updated_at": inquiry.updated_at,
            "due_by": inquiry.due_by
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return self.monitoring_agent.get_current_metrics()
