"""
ProjectCompass Demo Script

This script demonstrates the core functionality of the ProjectCompass system
by processing a sample vendor email inquiry.
"""
import logging
import json
from datetime import datetime
import os
import sys
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project directory to path to allow imports
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import ProjectCompass components
from models.inquiry import Inquiry, EmailMetadata, InquiryStatus, InquiryCategory
from agent_system.agent_manager import AgentManager
from services.email_processor import EmailProcessor
from services.prioritization_service import PrioritizationService
from services.routing_service import RoutingService
from data.repository import Repository

def create_sample_email(email_type="prequalification"):
    """Create a sample email for demonstration."""
    
    emails = {
        "prequalification": {
            "from": "john.smith@acmesuppliers.com",
            "to": "vendor.registration@projectcompass.com",
            "cc": "jane.doe@acmesuppliers.com",
            "subject": "Prequalification Application Status Inquiry",
            "text": """
Dear Vendor Registration Team,

We submitted our prequalification application (ID: APP-2025-078) two weeks ago and haven't heard back yet.
Could you please check the status of our application and let us know if you need any additional documents?

Our company, Acme Suppliers, is very interested in joining your vendor program as we specialize in logistics
equipment and have a strong track record with similar companies.

Thank you for your assistance.

Best regards,
John Smith
Procurement Manager
Acme Suppliers
Phone: 555-123-4567
            """
        },
        "finance": {
            "from": "accounts@techsupplies.com",
            "to": "accounts.payable@projectcompass.com",
            "cc": "",
            "subject": "URGENT: Missing Payment for Invoice #INV-2025-432",
            "text": """
Dear Accounts Payable Department,

This is regarding our invoice #INV-2025-432 for $24,500 that was due on March 15, 2025.

We have not received the payment yet, and it is now over 10 days past the due date. According to our
agreement, payments should be processed within 30 days of invoice submission.

Could you please check the status of this payment and provide an update on when we can expect to receive it?
This is becoming urgent as it's affecting our cash flow.

Thank you for your prompt attention to this matter.

Regards,
Sarah Johnson
Finance Director
Tech Supplies Inc.
            """
        },
        "contract": {
            "from": "legal@globallogistics.com",
            "to": "contracts@projectcompass.com",
            "cc": "ceo@globallogistics.com",
            "subject": "Contract Renewal Terms - Agreement #CT-2023-789",
            "text": """
Hello Contracts Team,

Our current service agreement (#CT-2023-789) is set to expire on April 30, 2025. We would like to
discuss the renewal terms as soon as possible.

Specifically, we're interested in:
1. Extending the contract period to 3 years instead of the current 1-year term
2. Revisiting the pricing structure to reflect our increased volume
3. Adding two new service categories to the scope

Could we schedule a call next week to discuss these points? We're available most afternoons.

Thank you,
Michael Chen
Legal Counsel
Global Logistics Ltd.
            """
        },
        "technical_issue": {
            "from": "operations@qualityparts.co",
            "to": "support@projectcompass.com",
            "cc": "",
            "subject": "CRITICAL: Unable to Access Vendor Portal",
            "text": """
URGENT SUPPORT NEEDED

We've been unable to access the vendor portal since yesterday morning. When trying to log in, we 
receive the error message: "Authentication failed: System error (code 503)".

This is critical as we have several pending bids that need to be submitted by tomorrow. Our account
username is supplier_qp_22.

Please help us resolve this issue as soon as possible.

Thank you,
Robert Taylor
Operations Director
Quality Parts Co.
Phone: 555-987-6543
            """
        }
    }
    
    return emails.get(email_type, emails["prequalification"])

def process_sample_email(email_type="prequalification"):
    """Process a sample email through the ProjectCompass system."""
    logger.info(f"Starting ProjectCompass demonstration with {email_type} email...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data/storage", exist_ok=True)
    
    # Initialize services
    logger.info("Initializing services...")
    email_processor = EmailProcessor()
    prioritization_service = PrioritizationService()
    routing_service = RoutingService()
    
    # Initialize agent manager
    logger.info("Initializing agent manager...")
    agent_manager = AgentManager(
        prioritization_service=prioritization_service,
        routing_service=routing_service
    )
    
    # Initialize repository
    repository = Repository()
    
    # Get sample email
    email_data = create_sample_email(email_type)
    logger.info(f"Using sample email with subject: {email_data['subject']}")
    
    # Display sample email
    print("\n" + "="*80)
    print("SAMPLE EMAIL:")
    print(f"From: {email_data['from']}")
    print(f"To: {email_data['to']}")
    if email_data['cc']:
        print(f"CC: {email_data['cc']}")
    print(f"Subject: {email_data['subject']}")
    print("-"*80)
    print(email_data['text'].strip())
    print("="*80 + "\n")
    
    # Process email
    logger.info("Processing email...")
    try:
        # Process through email processor
        inquiry = email_processor.process_email(email_data)
        print(f"Created inquiry with ID: {inquiry.id}")
        
        # Process through agent system
        print("\nProcessing through agent system...")
        result = agent_manager.handle_inquiry(inquiry)
        
        # Save to repository
        repository.save_inquiry(inquiry)
        print(f"Saved inquiry to repository")
        
        # Display results
        print("\n" + "="*80)
        print("PROCESSING RESULTS:")
        print(f"Inquiry ID: {inquiry.id}")
        print(f"Vendor: {inquiry.vendor_name or 'Unknown'}")
        print(f"Category: {inquiry.category}")
        print(f"Type: {inquiry.inquiry_type}")
        print(f"Priority: {inquiry.priority}")
        print(f"Status: {inquiry.status}")
        print(f"Assigned to: {inquiry.assigned_to}")
        if inquiry.due_by:
            print(f"Due by: {inquiry.due_by.strftime('%Y-%m-%d %H:%M')}")
        print("="*80 + "\n")
        
        # Display routing details
        print("ROUTING DETAILS:")
        result_pretty = json.dumps(result, indent=2)
        print(result_pretty)
        print("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in demonstration: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ProjectCompass Demo Script')
    parser.add_argument('--email-type', type=str, default='prequalification',
                        choices=['prequalification', 'finance', 'contract', 'technical_issue'],
                        help='Type of sample email to process')
    
    args = parser.parse_args()
    
    # Run the demo
    process_sample_email(args.email_type)
