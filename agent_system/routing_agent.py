"""
Routing Agent for assigning inquiries to appropriate departments or personnel.
"""
import logging
from typing import Dict, Tuple, List, Any
import random  # Only for demo, remove in production

from models.inquiry import Inquiry, InquiryCategory, InquiryType, InquiryPriority

# Initialize logging
logger = logging.getLogger(__name__)

class RoutingAgent:
    """
    Specialized agent for routing inquiries to appropriate departments or personnel.
    Determines the best recipient based on inquiry content and organizational structure.
    """
    
    def __init__(self, routing_service=None):
        """Initialize the Routing Agent."""
        logger.info("Initializing Routing Agent")
        self.routing_service = routing_service
        
        # Define routing rules
        self._initialize_routing_rules()
    
    def _initialize_routing_rules(self):
        """Initialize department and personnel routing rules."""
        # Department mapping by category
        self.department_routing = {
            InquiryCategory.PREQUALIFICATION: "Vendor Registration",
            InquiryCategory.FINANCE: "Finance",
            InquiryCategory.CONTRACT: "Legal",
            InquiryCategory.BIDDING: "Procurement",
            InquiryCategory.ISSUE: "Technical Support",
            InquiryCategory.INFORMATION: "Vendor Relations",
            InquiryCategory.OTHER: "Vendor Relations"
        }
        
        # Specific routing by inquiry type
        self.type_routing = {
            # Prequalification
            InquiryType.APPLICATION_STATUS: "Vendor Registration",
            InquiryType.DOCUMENT_SUBMISSION: "Vendor Registration",
            InquiryType.ELIGIBILITY_CRITERIA: "Vendor Registration",
            
            # Finance
            InquiryType.PAYMENT_STATUS: "Accounts Payable",
            InquiryType.INVOICE_ISSUE: "Accounts Payable",
            InquiryType.TAX_DOCUMENTATION: "Finance",
            
            # Contract
            InquiryType.CONTRACT_TERMS: "Legal",
            InquiryType.RENEWAL: "Contract Management",
            InquiryType.AMENDMENT: "Contract Management",
            
            # Bidding
            InquiryType.BID_SUBMISSION: "Procurement",
            InquiryType.BID_CLARIFICATION: "Procurement",
            InquiryType.BID_RESULTS: "Procurement",
            
            # Issues
            InquiryType.TECHNICAL_ISSUE: "Technical Support",
            InquiryType.PORTAL_ACCESS: "Technical Support",
            InquiryType.DELIVERY_ISSUE: "Logistics",
            
            # Information
            InquiryType.PROCESS_INFORMATION: "Vendor Relations",
            InquiryType.DOCUMENTATION_REQUEST: "Vendor Relations",
            InquiryType.CONTACT_REQUEST: "Vendor Relations",
            
            # Default
            InquiryType.GENERAL: "Vendor Relations"
        }
        
        # Priority-based personnel routing
        # In a real system, this would connect to a service that provides current personnel availability
        self.priority_teams = {
            InquiryPriority.CRITICAL: ["urgent_response_team", "department_head"],
            InquiryPriority.HIGH: ["senior_specialist", "specialist"],
            InquiryPriority.MEDIUM: ["specialist", "associate"],
            InquiryPriority.LOW: ["associate", "assistant"],
            InquiryPriority.INFORMATIONAL: ["assistant"]
        }
        
        # Define department staff (mock data for demonstration)
        # In a real system, this would be sourced from a database or directory service
        self.department_staff = {
            "Vendor Registration": {
                "department_head": "registration.head@example.com",
                "senior_specialist": "registration.senior@example.com",
                "specialist": "registration.specialist@example.com",
                "associate": "registration.associate@example.com",
                "assistant": "registration.assistant@example.com",
                "urgent_response_team": "registration.urgent@example.com"
            },
            "Finance": {
                "department_head": "finance.head@example.com",
                "senior_specialist": "finance.senior@example.com",
                "specialist": "finance.specialist@example.com",
                "associate": "finance.associate@example.com",
                "assistant": "finance.assistant@example.com",
                "urgent_response_team": "finance.urgent@example.com"
            },
            "Accounts Payable": {
                "department_head": "ap.head@example.com",
                "senior_specialist": "ap.senior@example.com",
                "specialist": "ap.specialist@example.com",
                "associate": "ap.associate@example.com",
                "assistant": "ap.assistant@example.com",
                "urgent_response_team": "ap.urgent@example.com"
            },
            "Legal": {
                "department_head": "legal.head@example.com",
                "senior_specialist": "legal.senior@example.com",
                "specialist": "legal.specialist@example.com",
                "associate": "legal.associate@example.com",
                "assistant": "legal.assistant@example.com",
                "urgent_response_team": "legal.urgent@example.com"
            },
            "Contract Management": {
                "department_head": "contracts.head@example.com",
                "senior_specialist": "contracts.senior@example.com",
                "specialist": "contracts.specialist@example.com",
                "associate": "contracts.associate@example.com",
                "assistant": "contracts.assistant@example.com",
                "urgent_response_team": "contracts.urgent@example.com"
            },
            "Procurement": {
                "department_head": "procurement.head@example.com",
                "senior_specialist": "procurement.senior@example.com",
                "specialist": "procurement.specialist@example.com",
                "associate": "procurement.associate@example.com",
                "assistant": "procurement.assistant@example.com",
                "urgent_response_team": "procurement.urgent@example.com"
            },
            "Technical Support": {
                "department_head": "support.head@example.com",
                "senior_specialist": "support.senior@example.com",
                "specialist": "support.specialist@example.com",
                "associate": "support.associate@example.com",
                "assistant": "support.assistant@example.com",
                "urgent_response_team": "support.urgent@example.com"
            },
            "Logistics": {
                "department_head": "logistics.head@example.com",
                "senior_specialist": "logistics.senior@example.com",
                "specialist": "logistics.specialist@example.com",
                "associate": "logistics.associate@example.com",
                "assistant": "logistics.assistant@example.com",
                "urgent_response_team": "logistics.urgent@example.com"
            },
            "Vendor Relations": {
                "department_head": "relations.head@example.com",
                "senior_specialist": "relations.senior@example.com",
                "specialist": "relations.specialist@example.com",
                "associate": "relations.associate@example.com",
                "assistant": "relations.assistant@example.com",
                "urgent_response_team": "relations.urgent@example.com"
            }
        }
    
    def route_inquiry(self, inquiry: Inquiry) -> Tuple[Inquiry, Dict[str, Any]]:
        """
        Route an inquiry to the appropriate department and personnel.
        
        Args:
            inquiry: The inquiry to route
            
        Returns:
            Tuple of (updated inquiry, routing_results)
        """
        logger.info(f"Routing inquiry {inquiry.id}")
        
        # Determine target department
        department = self._determine_department(inquiry)
        
        # Determine target personnel based on priority
        assignee = self._determine_assignee(inquiry, department)
        
        # Track historical vendor assignments if available
        if self.routing_service and inquiry.vendor_id:
            previous_assignee = self._check_vendor_history(inquiry.vendor_id)
            if previous_assignee:
                assignee = previous_assignee
                logger.info(f"Routing to previous assignee: {assignee}")
        
        # Apply load balancing (mock implementation)
        # In production, this would check actual workloads and availability
        assignee = self._apply_load_balancing(department, assignee)
        
        # Update the inquiry
        inquiry.assigned_to = assignee
        
        # Return both the updated inquiry and routing details
        routing_result = {
            "department": department,
            "assignee": assignee,
            "assignment_time": inquiry.updated_at,
            "routing_reason": f"Routed based on {inquiry.category} category and {inquiry.priority} priority"
        }
        
        return inquiry, routing_result
    
    def _determine_department(self, inquiry: Inquiry) -> str:
        """Determine the appropriate department for an inquiry."""
        # First try routing by specific inquiry type
        if inquiry.inquiry_type and inquiry.inquiry_type in self.type_routing:
            return self.type_routing[inquiry.inquiry_type]
        
        # Fall back to category-based routing
        return self.department_routing.get(inquiry.category, "Vendor Relations")
    
    def _determine_assignee(self, inquiry: Inquiry, department: str) -> str:
        """Determine the appropriate personnel to assign based on priority."""
        # Get the appropriate roles for this priority
        if inquiry.priority not in self.priority_teams:
            roles = ["specialist"]  # Default role
        else:
            roles = self.priority_teams[inquiry.priority]
        
        # Get the department's staff mapping
        if department not in self.department_staff:
            # Fall back to Vendor Relations if department not found
            department = "Vendor Relations"
        
        staff_map = self.department_staff[department]
        
        # Find the first available role that exists in the department
        for role in roles:
            if role in staff_map:
                return staff_map[role]
        
        # Fall back to a default person in the department
        if "specialist" in staff_map:
            return staff_map["specialist"]
        else:
            # Last resort: return first available staff member
            return next(iter(staff_map.values()))
    
    def _check_vendor_history(self, vendor_id: str) -> str:
        """Check if the vendor has been assigned to someone previously."""
        if not self.routing_service:
            return None
            
        try:
            return self.routing_service.get_vendor_assignee(vendor_id)
        except Exception as e:
            logger.warning(f"Error checking vendor history: {str(e)}")
            return None
    
    def _apply_load_balancing(self, department: str, default_assignee: str) -> str:
        """Apply load balancing to avoid overloading specific personnel."""
        # In a real system, this would check current workloads and availability
        # For this mock implementation, 80% of the time we'll use the default assignee
        # and 20% of the time we'll select someone else from the department
        
        if random.random() < 0.8:
            return default_assignee
            
        # Get all staff in the department who aren't the default assignee
        if department not in self.department_staff:
            return default_assignee
            
        staff_map = self.department_staff[department]
        alternative_staff = [email for role, email in staff_map.items() 
                            if email != default_assignee]
        
        if not alternative_staff:
            return default_assignee
            
        # Select a random alternative
        return random.choice(alternative_staff)
