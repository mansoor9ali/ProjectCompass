"""
Monitoring Agent for tracking system health and performance metrics.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import threading
import time

from models.inquiry import Inquiry, InquiryCategory, InquiryPriority, InquiryStatus

# Initialize logging
logger = logging.getLogger(__name__)

class MonitoringAgent:
    """
    Specialized agent for tracking system health and performance metrics.
    Records activity, errors, and performance metrics for the ProjectCompass system.
    """
    
    def __init__(self):
        """Initialize the Monitoring Agent."""
        logger.info("Initializing Monitoring Agent")
        
        # Initialize metrics storage
        self.reset_metrics()
        
        # Initialize error log
        self.error_log = []
        
        # Initialize activity log
        self.activity_log = []
        
        # Start background monitoring thread (in a real system)
        # self._start_monitoring_thread()
    
    def reset_metrics(self):
        """Reset all metrics to initial values."""
        # System metrics
        self.system_metrics = {
            "start_time": datetime.now(),
            "inquiries_processed": 0,
            "inquiries_by_category": {cat.value: 0 for cat in InquiryCategory},
            "inquiries_by_priority": {pri.value: 0 for pri in InquiryPriority},
            "avg_processing_time": 0,
            "total_processing_time": 0,
            "error_count": 0
        }
        
        # Performance metrics
        self.performance_metrics = {
            "response_times": [],  # List of response times in seconds
            "categorization_accuracy": 1.0,  # Placeholder, would be updated based on feedback
            "routing_efficiency": 1.0,  # Placeholder
            "agent_load": {}  # Map of agent_id to current load
        }
        
        # Queue metrics
        self.queue_metrics = {
            "current_queue_size": 0,
            "avg_wait_time": 0,
            "inquiries_by_status": {status.value: 0 for status in InquiryStatus}
        }
    
    def update_metrics(self, inquiry: Inquiry):
        """
        Update metrics based on a processed inquiry.
        
        Args:
            inquiry: The processed inquiry
        """
        # Update system metrics
        self.system_metrics["inquiries_processed"] += 1
        
        # Update category counts
        if inquiry.category:
            cat_value = inquiry.category.value if hasattr(inquiry.category, 'value') else str(inquiry.category)
            if cat_value in self.system_metrics["inquiries_by_category"]:
                self.system_metrics["inquiries_by_category"][cat_value] += 1
        
        # Update priority counts
        if inquiry.priority:
            pri_value = inquiry.priority.value if hasattr(inquiry.priority, 'value') else str(inquiry.priority)
            if pri_value in self.system_metrics["inquiries_by_priority"]:
                self.system_metrics["inquiries_by_priority"][pri_value] += 1
        
        # Update status counts
        if inquiry.status:
            status_value = inquiry.status.value if hasattr(inquiry.status, 'value') else str(inquiry.status)
            if status_value in self.queue_metrics["inquiries_by_status"]:
                self.queue_metrics["inquiries_by_status"][status_value] += 1
        
        # Calculate processing time
        processing_time = (datetime.now() - inquiry.created_at).total_seconds()
        
        # Update average processing time
        total_processed = self.system_metrics["inquiries_processed"]
        current_total = self.system_metrics["total_processing_time"]
        new_total = current_total + processing_time
        
        self.system_metrics["total_processing_time"] = new_total
        self.system_metrics["avg_processing_time"] = new_total / total_processed if total_processed > 0 else 0
        
        # Update performance metrics
        self.performance_metrics["response_times"].append(processing_time)
        
        # Update agent load (simplified for demonstration)
        if inquiry.assigned_to and inquiry.assigned_to in self.performance_metrics["agent_load"]:
            self.performance_metrics["agent_load"][inquiry.assigned_to] += 1
        else:
            self.performance_metrics["agent_load"][inquiry.assigned_to] = 1
        
        # Log this activity
        self.log_activity("inquiry_processed", {
            "inquiry_id": inquiry.id,
            "category": cat_value if inquiry.category else "unknown",
            "priority": pri_value if inquiry.priority else "unknown",
            "processing_time": processing_time
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """
        Log an error that occurred during processing.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context for the error
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        self.error_log.append(error_entry)
        self.system_metrics["error_count"] += 1
        
        # Log to standard logger as well
        logger.error(f"{error_type}: {error_message}")
    
    def log_activity(self, activity_type: str, details: Dict[str, Any] = None):
        """
        Log a system activity.
        
        Args:
            activity_type: Type of activity
            details: Activity details
        """
        activity_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "details": details or {}
        }
        
        self.activity_log.append(activity_entry)
        
        # Limit log size by removing oldest entries if needed
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-1000:]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return {
            "time": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.system_metrics["start_time"]).total_seconds(),
            "system": self.system_metrics,
            "performance": {
                "avg_response_time": sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"]) if self.performance_metrics["response_times"] else 0,
                "categorization_accuracy": self.performance_metrics["categorization_accuracy"],
                "routing_efficiency": self.performance_metrics["routing_efficiency"],
                "agent_load": {k: v for k, v in sorted(self.performance_metrics["agent_load"].items(), key=lambda item: item[1], reverse=True)}
            },
            "queue": self.queue_metrics,
            "recent_errors": self.error_log[-5:] if self.error_log else []
        }
    
    def get_error_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent error log entries."""
        return self.error_log[-limit:] if self.error_log else []
    
    def get_activity_log(self, limit: int = 100, activity_type: str = None) -> List[Dict[str, Any]]:
        """Get recent activity log entries, optionally filtered by type."""
        if activity_type:
            filtered_log = [entry for entry in self.activity_log if entry["activity_type"] == activity_type]
            return filtered_log[-limit:] if filtered_log else []
        else:
            return self.activity_log[-limit:] if self.activity_log else []
    
    def _start_monitoring_thread(self):
        """Start a background thread for continuous monitoring."""
        def monitoring_loop():
            while True:
                try:
                    # Collect system level metrics
                    # In a real system, would collect CPU, memory, disk usage, etc.
                    self.log_activity("system_check", {
                        "queue_size": self.queue_metrics["current_queue_size"],
                        "error_count": self.system_metrics["error_count"]
                    })
                    
                    # Wait for next collection interval
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Error in monitoring thread: {str(e)}")
                    # Don't crash the monitoring thread
                    time.sleep(300)  # Wait longer after an error
        
        # Start as daemon thread so it doesn't block program exit
        thread = threading.Thread(target=monitoring_loop, daemon=True)
        thread.start()
        logger.info("Started monitoring background thread")
