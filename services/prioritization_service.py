"""
Prioritization Service for the ProjectCompass system.
Handles vendor prioritization logic and scoring algorithms.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Initialize logging
logger = logging.getLogger(__name__)

class PrioritizationService:
    """
    Service for determining vendor and inquiry priorities.
    Provides scoring algorithms and prioritization rules.
    """
    
    def __init__(self):
        """Initialize the Prioritization Service."""
        logger.info("Initializing Prioritization Service")
        
        # In a real system, this would connect to a database
        # This is a simplified in-memory implementation
        self.vendor_data = {}
        self.vendor_scores = {}
        self.priority_factors = {
            "inquiry_frequency": 0.2,  # Higher frequency = higher priority
            "relationship_status": 0.3,  # Key vendors get higher priority
            "contract_value": 0.3,  # Higher value = higher priority
            "response_history": 0.2   # Slower past responses = higher priority
        }
    
    def get_vendor_data(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get vendor data for prioritization decisions.
        
        Args:
            vendor_id: The ID of the vendor
            
        Returns:
            Dictionary with vendor data or None if not found
        """
        return self.vendor_data.get(vendor_id)
    
    def calculate_vendor_score(self, vendor_id: str) -> float:
        """
        Calculate a priority score for a vendor.
        Higher score = higher priority.
        
        Args:
            vendor_id: The ID of the vendor
            
        Returns:
            Priority score from 0.0 to 1.0
        """
        # Get vendor data
        vendor_data = self.get_vendor_data(vendor_id)
        if not vendor_data:
            # Default score for unknown vendors
            return 0.5
        
        # Calculate score based on priority factors
        score = 0.0
        
        # Factor 1: Inquiry frequency
        inquiry_count = vendor_data.get("inquiry_count", 0)
        freq_score = min(inquiry_count / 10, 1.0)  # Cap at 10 inquiries
        score += freq_score * self.priority_factors["inquiry_frequency"]
        
        # Factor 2: Relationship status
        relationship = vendor_data.get("relationship_status", "standard")
        rel_scores = {
            "key": 1.0,
            "preferred": 0.8,
            "standard": 0.5,
            "new": 0.7,  # New vendors get higher priority than standard
            "probation": 0.6
        }
        rel_score = rel_scores.get(relationship, 0.5)
        score += rel_score * self.priority_factors["relationship_status"]
        
        # Factor 3: Contract value
        contract_value = vendor_data.get("contract_value", 0)
        # Normalize to 0-1 range (assuming $1M is the max)
        value_score = min(contract_value / 1000000, 1.0)
        score += value_score * self.priority_factors["contract_value"]
        
        # Factor 4: Response history
        avg_response_time = vendor_data.get("avg_response_time", 24)  # Hours
        # Convert to score (slower response = higher priority)
        # 0 hours = 0.0, 48+ hours = 1.0
        response_score = min(avg_response_time / 48, 1.0)
        score += response_score * self.priority_factors["response_history"]
        
        # Cache the score
        self.vendor_scores[vendor_id] = score
        
        return score
    
    def update_vendor_stats(self, vendor_id: str, inquiry_data: Dict[str, Any]):
        """
        Update vendor statistics based on a new inquiry.
        
        Args:
            vendor_id: The ID of the vendor
            inquiry_data: Data about the inquiry
        """
        if vendor_id not in self.vendor_data:
            # Create new vendor record
            self.vendor_data[vendor_id] = {
                "inquiry_count": 0,
                "last_inquiry_date": None,
                "relationship_status": "new",
                "contract_value": 0,
                "avg_response_time": 24,  # Default 24 hours
                "inquiries": []
            }
        
        # Update vendor data
        vendor = self.vendor_data[vendor_id]
        vendor["inquiry_count"] += 1
        vendor["last_inquiry_date"] = datetime.now()
        
        # Add inquiry to history
        vendor["inquiries"].append({
            "date": datetime.now(),
            "type": inquiry_data.get("type"),
            "priority": inquiry_data.get("priority"),
            "category": inquiry_data.get("category")
        })
        
        # Limit history size
        if len(vendor["inquiries"]) > 100:
            vendor["inquiries"] = vendor["inquiries"][-100:]
    
    def get_key_vendors(self) -> List[str]:
        """
        Get a list of key vendor IDs.
        
        Returns:
            List of key vendor IDs
        """
        return [
            vendor_id for vendor_id, data in self.vendor_data.items()
            if data.get("relationship_status") == "key"
        ]
    
    def set_vendor_relationship(self, vendor_id: str, relationship: str):
        """
        Set the relationship status for a vendor.
        
        Args:
            vendor_id: The ID of the vendor
            relationship: Relationship status (key, preferred, standard, new, probation)
        """
        if vendor_id not in self.vendor_data:
            # Create new vendor record
            self.vendor_data[vendor_id] = {
                "inquiry_count": 0,
                "last_inquiry_date": None,
                "relationship_status": relationship,
                "contract_value": 0,
                "avg_response_time": 24,
                "inquiries": []
            }
        else:
            # Update existing record
            self.vendor_data[vendor_id]["relationship_status"] = relationship
    
    def set_contract_value(self, vendor_id: str, value: float):
        """
        Set the contract value for a vendor.
        
        Args:
            vendor_id: The ID of the vendor
            value: Contract value in dollars
        """
        if vendor_id not in self.vendor_data:
            # Create new vendor record
            self.vendor_data[vendor_id] = {
                "inquiry_count": 0,
                "last_inquiry_date": None,
                "relationship_status": "new",
                "contract_value": value,
                "avg_response_time": 24,
                "inquiries": []
            }
        else:
            # Update existing record
            self.vendor_data[vendor_id]["contract_value"] = value
    
    def record_response_time(self, vendor_id: str, hours: float):
        """
        Record a response time for a vendor inquiry.
        
        Args:
            vendor_id: The ID of the vendor
            hours: Response time in hours
        """
        if vendor_id not in self.vendor_data:
            # Create new vendor record with this response time
            self.vendor_data[vendor_id] = {
                "inquiry_count": 1,
                "last_inquiry_date": datetime.now() - timedelta(hours=hours),
                "relationship_status": "new",
                "contract_value": 0,
                "avg_response_time": hours,
                "inquiries": []
            }
        else:
            # Update existing record
            vendor = self.vendor_data[vendor_id]
            
            # Calculate new average
            current_avg = vendor["avg_response_time"]
            count = vendor["inquiry_count"]
            
            # Weighted average (more weight to recent responses)
            new_avg = (current_avg * count + hours * 2) / (count + 2)
            vendor["avg_response_time"] = new_avg
