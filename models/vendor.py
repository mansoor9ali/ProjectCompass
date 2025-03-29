"""
Vendor data model for the ProjectCompass system.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class VendorContact(BaseModel):
    """Contact information for a vendor representative."""
    name: str
    email: str
    phone: Optional[str] = None
    role: Optional[str] = None


class VendorPerformance(BaseModel):
    """Historical performance metrics for a vendor."""
    response_time_avg: Optional[float] = None  # Average response time in hours
    issue_resolution_rate: Optional[float] = None  # Percentage of issues resolved
    contract_adherence: Optional[float] = None  # Score from 0-100
    last_updated: datetime = Field(default_factory=datetime.now)


class Vendor(BaseModel):
    """Main vendor data model."""
    id: str
    name: str
    category: str  # e.g., supplier, service provider, contractor
    contacts: List[VendorContact]
    status: str = "active"  # active, inactive, pending, blacklisted
    registration_date: datetime
    prequalification_status: Optional[str] = None  # pending, approved, rejected
    contract_status: Optional[str] = None  # none, negotiating, active, expired
    financial_status: Optional[str] = None  # good, review, hold
    performance: Optional[VendorPerformance] = None
    tags: List[str] = []
    metadata: Dict = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert the vendor model to a dictionary."""
        return self.dict(by_alias=True)
