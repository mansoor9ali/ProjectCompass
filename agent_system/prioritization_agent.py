"""
Prioritization Agent for scoring and prioritizing vendor inquiries.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from models.inquiry import Inquiry, InquiryPriority, InquiryCategory, InquiryType

# Initialize logging
logger = logging.getLogger(__name__)

class PrioritizationAgent:
    """
    Specialized agent for determining the priority of vendor inquiries.
    Assigns priority levels based on multiple factors including inquiry type,
    content analysis, and vendor relationship.
    """
    
    def __init__(self, prioritization_service=None):
        """Initialize the Prioritization Agent."""
        logger.info("Initializing Prioritization Agent")
        self.prioritization_service = prioritization_service
        
        # Priority rules by category and type
        self._initialize_priority_rules()
    
    def _initialize_priority_rules(self):
        """Initialize priority rules for different inquiry types."""
        # Default priorities by category
        self.category_priorities = {
            InquiryCategory.PREQUALIFICATION: InquiryPriority.MEDIUM,
            InquiryCategory.FINANCE: InquiryPriority.HIGH,
            InquiryCategory.CONTRACT: InquiryPriority.HIGH,
            InquiryCategory.BIDDING: InquiryPriority.HIGH,
            InquiryCategory.ISSUE: InquiryPriority.HIGH,
            InquiryCategory.INFORMATION: InquiryPriority.LOW,
            InquiryCategory.OTHER: InquiryPriority.MEDIUM,
        }
        
        # Priority overrides by specific inquiry type
        self.type_priorities = {
            # Critical priority types
            InquiryType.TECHNICAL_ISSUE: InquiryPriority.CRITICAL,
            InquiryType.PORTAL_ACCESS: InquiryPriority.HIGH,
            
            # High priority types
            InquiryType.PAYMENT_STATUS: InquiryPriority.HIGH,
            InquiryType.INVOICE_ISSUE: InquiryPriority.HIGH,
            InquiryType.CONTRACT_TERMS: InquiryPriority.HIGH,
            InquiryType.RENEWAL: InquiryPriority.HIGH,
            InquiryType.BID_SUBMISSION: InquiryPriority.HIGH,
            InquiryType.BID_CLARIFICATION: InquiryPriority.HIGH,
            
            # Medium priority types
            InquiryType.APPLICATION_STATUS: InquiryPriority.MEDIUM,
            InquiryType.DOCUMENT_SUBMISSION: InquiryPriority.MEDIUM,
            InquiryType.ELIGIBILITY_CRITERIA: InquiryPriority.MEDIUM,
            InquiryType.TAX_DOCUMENTATION: InquiryPriority.MEDIUM,
            InquiryType.AMENDMENT: InquiryPriority.MEDIUM,
            InquiryType.BID_RESULTS: InquiryPriority.MEDIUM,
            
            # Low priority types
            InquiryType.PROCESS_INFORMATION: InquiryPriority.LOW,
            InquiryType.DOCUMENTATION_REQUEST: InquiryPriority.LOW,
            InquiryType.CONTACT_REQUEST: InquiryPriority.LOW,
            
            # Default
            InquiryType.GENERAL: InquiryPriority.LOW,
        }
        
        # Urgency keywords
        self.urgency_keywords = {
            "critical": ["urgent", "immediately", "asap", "emergency", "critical", "crucial", 
                       "deadline", "today", "serious", "severe", "time-sensitive"],
            "high": ["important", "priority", "high priority", "significant", "pressing", 
                   "expedite", "quickly", "fast", "soon", "promptly"],
            "low": ["whenever", "no rush", "at your convenience", "when possible", 
                  "not urgent", "routine", "regular", "standard"]
        }
    
    def prioritize_inquiry(self, inquiry: Inquiry) -> Inquiry:
        """
        Determine the priority of an inquiry based on multiple factors.
        
        Args:
            inquiry: The inquiry to prioritize
            
        Returns:
            Updated inquiry with priority set
        """
        logger.info(f"Prioritizing inquiry {inquiry.id}")
        
        # Base priority from category and type
        base_priority = self._get_base_priority(inquiry)
        
        # Check for urgent keywords
        keyword_priority = self._check_urgency_keywords(inquiry)
        
        # External factors that may affect priority
        # 1. Check if it's a follow-up email (reduces priority if it's been delayed)
        is_followup = self._is_followup_inquiry(inquiry)
        
        # 2. Check for time factors (e.g., upcoming deadlines mentioned)
        time_factors = self._check_time_factors(inquiry)
        
        # 3. Vendor relationship factors (if we know the vendor)
        vendor_factors = self._check_vendor_factors(inquiry)
        
        # Determine final priority by weighing all factors
        final_priority = self._determine_final_priority(
            base_priority, 
            keyword_priority, 
            is_followup,
            time_factors,
            vendor_factors
        )
        
        # Set due date based on priority
        due_by = self._calculate_due_date(final_priority)
        
        # Update the inquiry
        inquiry.priority = final_priority
        inquiry.due_by = due_by
        
        return inquiry
    
    def _get_base_priority(self, inquiry: Inquiry) -> InquiryPriority:
        """Get base priority from inquiry category and type."""
        # Get priority from type if available
        if inquiry.inquiry_type and inquiry.inquiry_type in self.type_priorities:
            return self.type_priorities[inquiry.inquiry_type]
        
        # Fall back to category priority
        return self.category_priorities.get(inquiry.category, InquiryPriority.MEDIUM)
    
    def _check_urgency_keywords(self, inquiry: Inquiry) -> InquiryPriority:
        """Check for urgency keywords in the inquiry text."""
        # Combine subject and content
        text = f"{inquiry.email_metadata.subject} {inquiry.raw_content}".lower()
        
        # Check for critical urgency keywords
        if any(keyword in text for keyword in self.urgency_keywords["critical"]):
            return InquiryPriority.CRITICAL
        
        # Check for high urgency keywords
        if any(keyword in text for keyword in self.urgency_keywords["high"]):
            return InquiryPriority.HIGH
        
        # Check for low urgency keywords
        if any(keyword in text for keyword in self.urgency_keywords["low"]):
            return InquiryPriority.LOW
        
        # No urgency keywords found
        return None
    
    def _is_followup_inquiry(self, inquiry: Inquiry) -> bool:
        """Check if this is a follow-up inquiry."""
        # Check email metadata for reply indicators
        if inquiry.email_metadata.in_reply_to:
            return True
        
        # Check content for follow-up phrases
        followup_phrases = [
            "following up", "follow up", "follow-up", "following-up",
            "previous email", "earlier email", "still waiting", 
            "haven't heard", "no response", "any update"
        ]
        
        text = inquiry.raw_content.lower()
        return any(phrase in text for phrase in followup_phrases)
    
    def _check_time_factors(self, inquiry: Inquiry) -> Dict[str, Any]:
        """Check for time-related factors affecting priority."""
        text = f"{inquiry.email_metadata.subject} {inquiry.raw_content}".lower()
        result = {
            "has_deadline": False,
            "deadline_soon": False,
            "mentions_delay": False
        }
        
        # Check for deadline mentions
        deadline_phrases = ["deadline", "due date", "due by", "by tomorrow", 
                           "this week", "end of week", "by friday", "by monday"]
        result["has_deadline"] = any(phrase in text for phrase in deadline_phrases)
        
        # Check for imminent deadlines
        imminent_phrases = ["today", "tomorrow", "asap", "immediately", 
                           "right away", "urgent", "within 24 hours"]
        result["deadline_soon"] = any(phrase in text for phrase in imminent_phrases)
        
        # Check for mentions of delay
        delay_phrases = ["delayed", "waiting for", "long time", "weeks ago",
                        "still pending", "overdue", "late"]
        result["mentions_delay"] = any(phrase in text for phrase in delay_phrases)
        
        return result
    
    def _check_vendor_factors(self, inquiry: Inquiry) -> Dict[str, Any]:
        """Check vendor-related factors affecting priority."""
        result = {
            "is_key_vendor": False,
            "has_active_contract": False,
            "has_history": False
        }
        
        # Use external service if available
        if self.prioritization_service and inquiry.vendor_id:
            try:
                vendor_data = self.prioritization_service.get_vendor_data(inquiry.vendor_id)
                if vendor_data:
                    result["is_key_vendor"] = vendor_data.get("is_key", False)
                    result["has_active_contract"] = vendor_data.get("has_active_contract", False)
                    result["has_history"] = vendor_data.get("has_history", False)
            except Exception as e:
                logger.warning(f"Error getting vendor data: {str(e)}")
        
        return result
    
    def _determine_final_priority(
        self, 
        base_priority: InquiryPriority, 
        keyword_priority: InquiryPriority,
        is_followup: bool,
        time_factors: Dict[str, bool],
        vendor_factors: Dict[str, bool]
    ) -> InquiryPriority:
        """Determine final priority based on all factors."""
        # Start with the highest priority among base and keyword
        if keyword_priority == InquiryPriority.CRITICAL:
            priority = InquiryPriority.CRITICAL
        elif keyword_priority == InquiryPriority.HIGH or base_priority == InquiryPriority.HIGH:
            priority = InquiryPriority.HIGH
        elif keyword_priority == InquiryPriority.MEDIUM or base_priority == InquiryPriority.MEDIUM:
            priority = InquiryPriority.MEDIUM
        else:
            priority = InquiryPriority.LOW
        
        # Adjust for follow-ups (increase priority)
        if is_followup and priority != InquiryPriority.CRITICAL:
            if priority == InquiryPriority.LOW:
                priority = InquiryPriority.MEDIUM
            elif priority == InquiryPriority.MEDIUM:
                priority = InquiryPriority.HIGH
        
        # Adjust for time factors
        if time_factors["deadline_soon"]:
            if priority != InquiryPriority.CRITICAL:
                priority = InquiryPriority.HIGH
        elif time_factors["has_deadline"] and priority == InquiryPriority.LOW:
            priority = InquiryPriority.MEDIUM
        
        if time_factors["mentions_delay"] and priority != InquiryPriority.CRITICAL:
            if priority == InquiryPriority.LOW:
                priority = InquiryPriority.MEDIUM
            elif priority == InquiryPriority.MEDIUM:
                priority = InquiryPriority.HIGH
        
        # Adjust for vendor factors
        if vendor_factors["is_key_vendor"] and priority != InquiryPriority.CRITICAL:
            if priority == InquiryPriority.LOW:
                priority = InquiryPriority.MEDIUM
            elif priority == InquiryPriority.MEDIUM:
                priority = InquiryPriority.HIGH
        
        return priority
    
    def _calculate_due_date(self, priority: InquiryPriority) -> datetime:
        """Calculate due date based on priority."""
        now = datetime.now()
        
        if priority == InquiryPriority.CRITICAL:
            return now + timedelta(hours=2)
        elif priority == InquiryPriority.HIGH:
            return now + timedelta(hours=8)
        elif priority == InquiryPriority.MEDIUM:
            return now + timedelta(days=1)
        else:  # LOW or INFORMATIONAL
            return now + timedelta(days=3)
