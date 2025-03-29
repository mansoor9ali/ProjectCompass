"""
ProjectCompass - Intelligent Logistics and Vendor Inquiry Management System
Main task definitions for Robocorp automation
"""
from robocorp.tasks import task
import logging
import os
import sys
from services.email_processor import EmailProcessor
from services.prioritization_service import PrioritizationService
from services.routing_service import RoutingService
from agent_system.agent_manager import AgentManager
from dashboard.server import run_dashboard_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@task
def email_inquiry_processor():
    """Process incoming vendor email inquiries using the agent-based system."""
    logger.info("Starting email inquiry processor task")
    
    # Initialize services
    email_processor = EmailProcessor()
    prioritization_service = PrioritizationService()
    routing_service = RoutingService()
    
    # Initialize agent manager
    agent_manager = AgentManager(
        prioritization_service=prioritization_service,
        routing_service=routing_service
    )
    
    # Since we might not have workitems in testing, let's handle that case
    try:
        from robocorp import workitems
        # Process work items (emails)
        for item in workitems.inputs:
            try:
                # Extract email data from work item
                email_data = item.payload
                
                # Process email through the agent system
                logger.info(f"Processing email: {email_data.get('subject', 'No subject')}")
                processed_inquiry = email_processor.process_email(email_data)
                
                # Handle the inquiry with the agent manager
                result = agent_manager.handle_inquiry(processed_inquiry)
                
                # Report success
                item.done(payload={"status": "success", "result": result})
                
            except Exception as e:
                logger.error(f"Error processing email: {str(e)}")
                item.fail(exception=e)
    except ImportError:
        logger.info("No workitems module available, running in test mode")
        # Here we could add test code for running without workitems
        pass

@task
def run_dashboard():
    """Run the web dashboard for monitoring and controlling the system."""
    # Get configuration from environment variables or use defaults
    host = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.environ.get("DASHBOARD_PORT", "8000"))
    
    # Print startup messages
    print(f"Starting dashboard server at http://{host}:{port}")
    print(f"Press Ctrl+C to stop the server")
    
    # Initialize the dashboard with agent manager for monitoring
    try:
        prioritization_service = PrioritizationService()
        routing_service = RoutingService()
        agent_manager = AgentManager(
            prioritization_service=prioritization_service,
            routing_service=routing_service
        )
        
        # Run the dashboard server (this will block until the server is stopped)
        run_dashboard_server(host=host, port=port, agent_mgr=agent_manager)
    except KeyboardInterrupt:
        logger.info("Dashboard server stopped by user")
    except Exception as e:
        logger.error(f"Error running dashboard server: {str(e)}")
        print(f"Error: {str(e)}")
