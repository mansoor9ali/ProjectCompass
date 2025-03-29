"""
Inquiry data models for the ProjectCompass system.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class InquiryCategory(str, Enum):
    """Categories of vendor inquiries."""
    PREQUALIFICATION = "prequalification"
    FINANCE = "finance"
    CONTRACT = "contract"
    BIDDING = "bidding"
    ISSUE = "issue"
    INFORMATION = "information"
    OTHER = "other"


class InquiryType(str, Enum):
    """Types of inquiry within each category."""
    # Prequalification types
    APPLICATION_STATUS = "application_status"
    DOCUMENT_SUBMISSION = "document_submission"
    ELIGIBILITY_CRITERIA = "eligibility_criteria"
    
    # Finance types
    PAYMENT_STATUS = "payment_status"
    INVOICE_ISSUE = "invoice_issue"
    TAX_DOCUMENTATION = "tax_documentation"
    
    # Contract types
    CONTRACT_TERMS = "contract_terms"
    RENEWAL = "renewal"
    AMENDMENT = "amendment"
    
    # Bidding types
    BID_SUBMISSION = "bid_submission"
    BID_CLARIFICATION = "bid_clarification"
    BID_RESULTS = "bid_results"
    
    # Issue types
    TECHNICAL_ISSUE = "technical_issue"
    PORTAL_ACCESS = "portal_access"
    DELIVERY_ISSUE = "delivery_issue"
    
    # Information types
    PROCESS_INFORMATION = "process_information"
    DOCUMENTATION_REQUEST = "documentation_request"
    CONTACT_REQUEST = "contact_request"
    
    # Fallback
    GENERAL = "general"


class InquiryPriority(str, Enum):
    """Priority levels for inquiries."""
    CRITICAL = "critical"  # Needs immediate attention
    HIGH = "high"  # Needs attention within hours
    MEDIUM = "medium"  # Needs attention within a day
    LOW = "low"  # Can be addressed within several days
    INFORMATIONAL = "informational"  # No specific action required


class InquiryStatus(str, Enum):
    """Status of an inquiry in the system."""
    NEW = "new"  # Just received
    CATEGORIZED = "categorized"  # Analyzed and categorized
    PRIORITIZED = "prioritized"  # Priority assigned
    ASSIGNED = "assigned"  # Assigned to a department/person
    IN_PROGRESS = "in_progress"  # Being worked on
    PENDING_INFO = "pending_info"  # Waiting for more information
    RESOLVED = "resolved"  # Inquiry has been resolved
    CLOSED = "closed"  # Inquiry cycle complete
    ESCALATED = "escalated"  # Requires higher level attention


class EmailMetadata(BaseModel):
    """Metadata extracted from the email."""
    from_email: str
    from_name: Optional[str] = None
    to_email: str
    cc: List[str] = []
    subject: str
    date_received: datetime
    has_attachments: bool = False
    attachment_count: int = 0
    attachment_names: List[str] = []
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None


class Inquiry(BaseModel):
    """Main model for vendor inquiries."""
    id: str
    vendor_id: Optional[str] = None  # May be unknown initially
    vendor_name: Optional[str] = None
    email_metadata: EmailMetadata
    raw_content: str
    processed_content: Optional[str] = None
    category: InquiryCategory = InquiryCategory.OTHER
    inquiry_type: Optional[InquiryType] = None
    priority: Optional[InquiryPriority] = None
    status: InquiryStatus = InquiryStatus.NEW
    confidence_score: float = 0.0  # AI confidence in categorization
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_by: Optional[datetime] = None
    tags: List[str] = []
    notes: List[Dict[str, Any]] = []
    related_inquiries: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert the inquiry model to a dictionary."""
        return self.dict(by_alias=True)
