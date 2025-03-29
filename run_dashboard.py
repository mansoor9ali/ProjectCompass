"""
ProjectCompass Dashboard Runner

This script provides a simple way to start the dashboard server.
"""
import logging
import os
from services.prioritization_service import PrioritizationService
from services.routing_service import RoutingService
from agent_system.agent_manager import AgentManager
from dashboard.server import run_dashboard_server

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Get configuration from environment variables or use defaults
    host = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.environ.get("DASHBOARD_PORT", "8000"))
    
    # Print startup message
    print(f"Starting ProjectCompass Dashboard at http://{host}:{port}")
    print(f"Press Ctrl+C to stop the server")
    
    # Initialize services for the dashboard
    try:
        # Initialize the core services
        prioritization_service = PrioritizationService()
        routing_service = RoutingService()
        
        # Initialize agent manager for monitoring
        agent_manager = AgentManager(
            prioritization_service=prioritization_service,
            routing_service=routing_service
        )
        
        # Run the dashboard server (this will block until the server is stopped)
        run_dashboard_server(host=host, port=port, agent_mgr=agent_manager)
    except KeyboardInterrupt:
        print("\nDashboard server stopped by user")
    except Exception as e:
        print(f"\nError running dashboard server: {str(e)}")
