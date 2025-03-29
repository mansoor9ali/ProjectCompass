"""
Routing Service for the ProjectCompass system.
Handles the business logic for routing inquiries to the appropriate department or personnel.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Initialize logging
logger = logging.getLogger(__name__)

class RoutingService:
    """
    Service for determining the optimal routing of vendor inquiries.
    Tracks department loads, personnel specializations, and routing history.
    """
    
    def __init__(self):
        """Initialize the Routing Service."""
        logger.info("Initializing Routing Service")
        
        # In a real system, this would connect to a database
        # This is a simplified in-memory implementation
        self.department_loads = {}
        self.personnel_loads = {}
        self.vendor_assignments = {}
        self.department_specializations = {}
        self.personnel_specializations = {}
        
        self._initialize_default_specializations()
    
    def _initialize_default_specializations(self):
        """Initialize default department and personnel specializations."""
        # Department specializations
        self.department_specializations = {
            "Vendor Registration": ["prequalification", "registration", "onboarding"],
            "Finance": ["payment", "invoice", "financial", "tax"],
            "Accounts Payable": ["payment", "invoice", "billing"],
            "Legal": ["contract", "agreement", "terms", "legal"],
            "Contract Management": ["contract", "renewal", "amendment"],
            "Procurement": ["bid", "tender", "proposal", "rfp", "pricing"],
            "Technical Support": ["technical", "system", "access", "login", "portal"],
            "Logistics": ["delivery", "shipping", "tracking", "schedule"],
            "Vendor Relations": ["information", "inquiry", "clarification", "general"]
        }
        
        # Personnel specializations (sample - in a real system would be more comprehensive)
        self.personnel_specializations = {
            "registration.head@example.com": ["management", "escalation", "policy"],
            "registration.senior@example.com": ["complex", "exception", "approval"],
            "registration.specialist@example.com": ["standard", "verification", "processing"],
            "finance.head@example.com": ["management", "budget", "escalation"],
            "ap.senior@example.com": ["payment", "international", "complex"],
            "legal.specialist@example.com": ["contract", "terms", "verification"],
            "procurement.specialist@example.com": ["bid", "evaluation", "selection"],
            "support.specialist@example.com": ["technical", "system", "access"],
            "relations.specialist@example.com": ["inquiry", "communication", "coordination"]
        }
    
    def get_vendor_assignee(self, vendor_id: str) -> Optional[str]:
        """
        Get the previously assigned person for a vendor.
        
        Args:
            vendor_id: The ID of the vendor
            
        Returns:
            Email address of the assigned person or None if not found
        """
        return self.vendor_assignments.get(vendor_id)
    
    def update_vendor_assignment(self, vendor_id: str, assignee: str):
        """
        Update the assignee for a vendor.
        
        Args:
            vendor_id: The ID of the vendor
            assignee: Email of the assigned person
        """
        self.vendor_assignments[vendor_id] = assignee
        logger.info(f"Updated vendor {vendor_id} assignment to {assignee}")
    
    def get_department_load(self, department: str) -> int:
        """
        Get the current inquiry load for a department.
        
        Args:
            department: Department name
            
        Returns:
            Current inquiry load count
        """
        return self.department_loads.get(department, 0)
    
    def get_personnel_load(self, email: str) -> int:
        """
        Get the current inquiry load for a person.
        
        Args:
            email: Person's email address
            
        Returns:
            Current inquiry load count
        """
        return self.personnel_loads.get(email, 0)
    
    def update_loads(self, department: str, assignee: str, increment: int = 1):
        """
        Update the load counts for a department and person.
        
        Args:
            department: Department name
            assignee: Person's email address
            increment: Amount to increment the load (default 1)
        """
        # Update department load
        current_dept_load = self.department_loads.get(department, 0)
        self.department_loads[department] = current_dept_load + increment
        
        # Update personnel load
        current_pers_load = self.personnel_loads.get(assignee, 0)
        self.personnel_loads[assignee] = current_pers_load + increment
    
    def find_optimal_assignee(self, department: str, keywords: List[str], priority_level: str = "medium") -> Tuple[str, float]:
        """
        Find the optimal assignee for an inquiry based on specialization and current load.
        
        Args:
            department: Target department
            keywords: Keywords from the inquiry for matching to specializations
            priority_level: Priority level of the inquiry
            
        Returns:
            Tuple of (assignee_email, match_score)
        """
        best_assignee = None
        best_score = -1
        
        # Get all personnel in the department
        dept_personnel = {
            email: specs for email, specs in self.personnel_specializations.items()
            if email.split("@")[0].split(".")[0] == department.lower().replace(" ", "")
        }
        
        if not dept_personnel:
            # Fall back to default email address format
            default_email = f"{department.lower().replace(' ', '')}.specialist@example.com"
            return default_email, 0.5
        
        for email, specializations in dept_personnel.items():
            # Calculate specialization match score
            match_count = sum(1 for keyword in keywords if any(spec in keyword or keyword in spec for spec in specializations))
            spec_score = match_count / len(keywords) if keywords else 0.5
            
            # Consider current load
            load = self.get_personnel_load(email)
            load_factor = max(0, 1 - (load / 20))  # Normalize: 0 load = 1.0, 20+ load = 0.0
            
            # Consider priority for high-priority inquiries, assign to more senior staff
            seniority_boost = 0
            if priority_level == "critical" and "head" in email:
                seniority_boost = 0.3
            elif priority_level == "high" and "senior" in email:
                seniority_boost = 0.2
            elif priority_level == "medium" and "specialist" in email:
                seniority_boost = 0.1
            elif priority_level == "low" and "assistant" in email:
                seniority_boost = 0.1
            
            # Calculate final score
            score = (spec_score * 0.5) + (load_factor * 0.3) + seniority_boost
            
            if score > best_score:
                best_score = score
                best_assignee = email
        
        if not best_assignee:
            # Fall back to default email address format
            best_assignee = f"{department.lower().replace(' ', '')}.specialist@example.com"
            best_score = 0.5
        
        return best_assignee, best_score
    
    def get_department_for_keywords(self, keywords: List[str]) -> Tuple[str, float]:
        """
        Find the most appropriate department based on inquiry keywords.
        
        Args:
            keywords: Keywords from the inquiry
            
        Returns:
            Tuple of (department_name, match_score)
        """
        best_department = "Vendor Relations"  # Default
        best_score = 0
        
        for department, specializations in self.department_specializations.items():
            # Count how many keywords match this department's specializations
            match_count = sum(1 for keyword in keywords if any(spec in keyword or keyword in spec for spec in specializations))
            
            # Calculate score as percentage of matched keywords
            score = match_count / len(keywords) if keywords else 0
            
            # Consider department load as a small factor
            load = self.get_department_load(department)
            load_factor = max(0, 1 - (load / 50))  # Normalize: 0 load = 1.0, 50+ load = 0.0
            
            # Combine scores (mainly specialization with small load influence)
            final_score = (score * 0.9) + (load_factor * 0.1)
            
            if final_score > best_score:
                best_score = final_score
                best_department = department
        
        return best_department, best_score
    
    def record_routing_decision(self, inquiry_id: str, vendor_id: Optional[str], department: str, assignee: str):
        """
        Record a routing decision for tracking and analysis.
        
        Args:
            inquiry_id: The ID of the inquiry
            vendor_id: The ID of the vendor (if available)
            department: The assigned department
            assignee: The assigned person's email
        """
        # In a real system, this would store to a database
        # For this simplified implementation, we just update the loads and vendor assignment
        
        # Update load counters
        self.update_loads(department, assignee)
        
        # Record vendor assignment if vendor_id is available
        if vendor_id:
            self.update_vendor_assignment(vendor_id, assignee)
        
        logger.info(f"Inquiry {inquiry_id} routed to {department} / {assignee}")
    
    def get_department_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on department loads and assignments.
        
        Returns:
            Dictionary with department statistics
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_inquiries": sum(self.department_loads.values()),
            "department_loads": {k: v for k, v in sorted(self.department_loads.items(), key=lambda item: item[1], reverse=True)},
            "busiest_department": max(self.department_loads.items(), key=lambda x: x[1])[0] if self.department_loads else None,
            "personnel_loads": {k: v for k, v in sorted(self.personnel_loads.items(), key=lambda item: item[1], reverse=True)[:10]}
        }
        
        return stats
