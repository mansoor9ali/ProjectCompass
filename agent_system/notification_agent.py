"""
Notification Agent for sending alerts about vendor inquiries.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from models.inquiry import Inquiry, InquiryPriority

# Initialize logging
logger = logging.getLogger(__name__)

class NotificationAgent:
    """
    Specialized agent for sending notifications about vendor inquiries.
    Handles email notifications, system alerts, and escalation notices.
    """
    
    def __init__(self):
        """Initialize the Notification Agent."""
        logger.info("Initializing Notification Agent")
        
        # Template messages for different notification types
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize notification templates."""
        self.templates = {
            "assignment": {
                "subject": "New Vendor Inquiry Assigned: {inquiry_id}",
                "body": """
Dear {assignee_name},

A new vendor inquiry has been assigned to you:

Inquiry ID: {inquiry_id}
Vendor: {vendor_name}
Category: {category}
Type: {inquiry_type}
Priority: {priority}
Due By: {due_by}

Inquiry Details:
{inquiry_content}

Please respond to this inquiry by the due date.

Best regards,
ProjectCompass System
                """
            },
            "escalation": {
                "subject": "URGENT: Escalated Vendor Inquiry {inquiry_id}",
                "body": """
Dear {manager_name},

A vendor inquiry has been escalated due to its critical nature:

Inquiry ID: {inquiry_id}
Vendor: {vendor_name}
Category: {category}
Type: {inquiry_type}
Priority: {priority}
Due By: {due_by}
Assignee: {assignee_name}

Inquiry Details:
{inquiry_content}

This inquiry requires immediate attention.

Best regards,
ProjectCompass System
                """
            },
            "reminder": {
                "subject": "Reminder: Pending Vendor Inquiry {inquiry_id}",
                "body": """
Dear {assignee_name},

This is a reminder about a pending vendor inquiry assigned to you:

Inquiry ID: {inquiry_id}
Vendor: {vendor_name}
Category: {category}
Type: {inquiry_type}
Priority: {priority}
Due By: {due_by}

The inquiry is due soon. Please ensure timely resolution.

Best regards,
ProjectCompass System
                """
            }
        }
    
    def send_inquiry_notifications(self, inquiry: Inquiry, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send appropriate notifications for an inquiry.
        
        Args:
            inquiry: The inquiry to send notifications for
            routing_result: The routing details
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending notifications for inquiry {inquiry.id}")
        results = {
            "sent": False,
            "notifications": []
        }
        
        try:
            # Send assignment notification
            assignment_result = self._send_assignment_notification(inquiry, routing_result)
            results["notifications"].append(assignment_result)
            
            # Send escalation notification if critical priority
            if inquiry.priority == InquiryPriority.CRITICAL:
                escalation_result = self._send_escalation_notification(inquiry, routing_result)
                results["notifications"].append(escalation_result)
            
            # Mark as successful if any notifications were sent
            if results["notifications"]:
                results["sent"] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
            results["error"] = str(e)
            return results
    
    def _send_assignment_notification(self, inquiry: Inquiry, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Send assignment notification to the assigned personnel."""
        # In a real system, this would send an actual email via SMTP or messaging service
        
        assignee = inquiry.assigned_to
        department = routing_result.get("department", "Unknown Department")
        assignee_name = assignee.split("@")[0].replace(".", " ").title()
        
        # Format due by date
        due_by_formatted = inquiry.due_by.strftime("%Y-%m-%d %H:%M") if inquiry.due_by else "Not specified"
        
        # Prepare template variables
        template_vars = {
            "assignee_name": assignee_name,
            "inquiry_id": inquiry.id,
            "vendor_name": inquiry.vendor_name or "Unknown Vendor",
            "category": inquiry.category,
            "inquiry_type": inquiry.inquiry_type,
            "priority": inquiry.priority,
            "due_by": due_by_formatted,
            "inquiry_content": inquiry.processed_content or inquiry.raw_content[:200] + "..."
        }
        
        # Get template
        subject_template = self.templates["assignment"]["subject"]
        body_template = self.templates["assignment"]["body"]
        
        # Format subject and body
        subject = subject_template.format(**template_vars)
        body = body_template.format(**template_vars)
        
        # Log notification content for demonstration (in production would send email)
        logger.info(f"Assignment notification would be sent to {assignee}")
        logger.debug(f"Notification subject: {subject}")
        logger.debug(f"Notification first line: {body.split('\\n')[0]}")
        
        return {
            "type": "assignment",
            "recipient": assignee,
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "status": "simulated_success"
        }
    
    def _send_escalation_notification(self, inquiry: Inquiry, routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Send escalation notification for critical inquiries."""
        department = routing_result.get("department", "Unknown Department")
        assignee = inquiry.assigned_to
        assignee_name = assignee.split("@")[0].replace(".", " ").title()
        
        # In a real system, would determine the manager's email from the department
        # For demonstration, we'll fabricate a manager email
        manager_email = f"manager.{department.lower().replace(' ', '')}@example.com"
        manager_name = f"{department} Manager"
        
        # Format due by date
        due_by_formatted = inquiry.due_by.strftime("%Y-%m-%d %H:%M") if inquiry.due_by else "Not specified"
        
        # Prepare template variables
        template_vars = {
            "manager_name": manager_name,
            "assignee_name": assignee_name,
            "inquiry_id": inquiry.id,
            "vendor_name": inquiry.vendor_name or "Unknown Vendor",
            "category": inquiry.category,
            "inquiry_type": inquiry.inquiry_type,
            "priority": inquiry.priority,
            "due_by": due_by_formatted,
            "inquiry_content": inquiry.processed_content or inquiry.raw_content[:200] + "..."
        }
        
        # Get template
        subject_template = self.templates["escalation"]["subject"]
        body_template = self.templates["escalation"]["body"]
        
        # Format subject and body
        subject = subject_template.format(**template_vars)
        body = body_template.format(**template_vars)
        
        # Log notification content for demonstration (in production would send email)
        logger.info(f"Escalation notification would be sent to {manager_email}")
        logger.debug(f"Notification subject: {subject}")
        logger.debug(f"Notification first line: {body.split('\\n')[0]}")
        
        return {
            "type": "escalation",
            "recipient": manager_email,
            "department": department,
            "timestamp": datetime.now().isoformat(),
            "status": "simulated_success"
        }
    
    def send_reminder_notification(self, inquiry: Inquiry) -> Dict[str, Any]:
        """Send a reminder notification for a pending inquiry."""
        # This method would be called by a scheduled task in a real system
        
        if not inquiry.assigned_to:
            logger.warning(f"Cannot send reminder for inquiry {inquiry.id} - no assignee")
            return {
                "type": "reminder",
                "status": "failed",
                "reason": "no_assignee"
            }
        
        assignee = inquiry.assigned_to
        assignee_name = assignee.split("@")[0].replace(".", " ").title()
        
        # Format due by date
        due_by_formatted = inquiry.due_by.strftime("%Y-%m-%d %H:%M") if inquiry.due_by else "Not specified"
        
        # Prepare template variables
        template_vars = {
            "assignee_name": assignee_name,
            "inquiry_id": inquiry.id,
            "vendor_name": inquiry.vendor_name or "Unknown Vendor",
            "category": inquiry.category,
            "inquiry_type": inquiry.inquiry_type,
            "priority": inquiry.priority,
            "due_by": due_by_formatted
        }
        
        # Get template
        subject_template = self.templates["reminder"]["subject"]
        body_template = self.templates["reminder"]["body"]
        
        # Format subject and body
        subject = subject_template.format(**template_vars)
        body = body_template.format(**template_vars)
        
        # Log notification content for demonstration (in production would send email)
        logger.info(f"Reminder notification would be sent to {assignee}")
        logger.debug(f"Notification subject: {subject}")
        logger.debug(f"Notification first line: {body.split('\\n')[0]}")
        
        return {
            "type": "reminder",
            "recipient": assignee,
            "timestamp": datetime.now().isoformat(),
            "status": "simulated_success"
        }
