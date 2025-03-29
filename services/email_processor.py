"""
Email Processor service for handling incoming vendor email inquiries.
"""
import logging
import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from models.inquiry import Inquiry, EmailMetadata, InquiryStatus

# Initialize logging
logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    Service for processing incoming email inquiries from vendors.
    Extracts relevant data from emails and converts them to Inquiry objects.
    """
    
    def __init__(self):
        """Initialize the Email Processor service."""
        logger.info("Initializing Email Processor service")
    
    def process_email(self, email_data: Dict[str, Any]) -> Inquiry:
        """
        Process an incoming email and convert it to an Inquiry object.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Inquiry object created from the email
        """
        logger.info(f"Processing email: {email_data.get('subject', 'No subject')}")
        
        try:
            # Extract metadata from the email
            metadata = self._extract_metadata(email_data)
            
            # Extract email content
            content = self._extract_content(email_data)
            
            # Create a unique ID for the inquiry
            inquiry_id = self._generate_inquiry_id()
            
            # Try to extract vendor information
            vendor_id, vendor_name = self._extract_vendor_info(email_data)
            
            # Create the inquiry object
            inquiry = Inquiry(
                id=inquiry_id,
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                email_metadata=metadata,
                raw_content=content,
                status=InquiryStatus.NEW,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return inquiry
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            raise
    
    def _extract_metadata(self, email_data: Dict[str, Any]) -> EmailMetadata:
        """Extract metadata from the email."""
        # Extract the sender information
        from_email = email_data.get("from", "").strip()
        from_name = None
        
        # Try to extract name from email format "Name <email@example.com>"
        if "<" in from_email and ">" in from_email:
            match = re.match(r"(.*?)\s*<(.+?)>", from_email)
            if match:
                from_name = match.group(1).strip()
                from_email = match.group(2).strip()
        
        # Extract other metadata
        to_email = email_data.get("to", "").strip()
        cc = [cc.strip() for cc in email_data.get("cc", "").split(",") if cc.strip()]
        subject = email_data.get("subject", "").strip()
        
        # Parse received date
        date_str = email_data.get("date", "")
        try:
            date_received = datetime.fromisoformat(date_str) if date_str else datetime.now()
        except ValueError:
            # Handle various date formats here in a real implementation
            date_received = datetime.now()
        
        # Check for attachments
        attachments = email_data.get("attachments", [])
        has_attachments = len(attachments) > 0
        attachment_names = [att.get("filename", f"attachment_{i}") for i, att in enumerate(attachments)]
        
        # Extract threading information
        thread_id = email_data.get("thread_id")
        in_reply_to = email_data.get("in_reply_to")
        
        # Create metadata object
        metadata = EmailMetadata(
            from_email=from_email,
            from_name=from_name,
            to_email=to_email,
            cc=cc,
            subject=subject,
            date_received=date_received,
            has_attachments=has_attachments,
            attachment_count=len(attachments),
            attachment_names=attachment_names,
            thread_id=thread_id,
            in_reply_to=in_reply_to
        )
        
        return metadata
    
    def _extract_content(self, email_data: Dict[str, Any]) -> str:
        """Extract the content from the email."""
        # Try to get HTML content first
        html_content = email_data.get("html", "")
        
        # If HTML content exists, convert it to plain text
        if html_content:
            plain_content = self._html_to_text(html_content)
        else:
            # Otherwise use plain text content
            plain_content = email_data.get("text", "")
        
        # Clean up the content
        clean_content = self._clean_email_content(plain_content)
        
        return clean_content
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML content to plain text.
        In a real implementation, this would use a proper HTML parser.
        """
        # This is a simplified implementation
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _clean_email_content(self, content: str) -> str:
        """Clean up email content by removing signatures, quotes, etc."""
        # This is a simplified implementation
        
        # Try to remove email signature
        signature_markers = [
            "\n-- \n",
            "\n__________________",
            "\nRegards,",
            "\nBest regards,",
            "\nThanks,",
            "\nThank you,",
            "\nSincerely,",
            "\nCheers,"
        ]
        
        for marker in signature_markers:
            if marker in content:
                content = content.split(marker)[0]
        
        # Try to remove quoted text
        quoted_text_patterns = [
            r'\nOn .* wrote:[\s\S]*',
            r'\n-+Original Message-+[\s\S]*',
            r'\n>.*',
            r'\nFrom:.*\nSent:.*\nTo:.*\nSubject:.*\n[\s\S]*'
        ]
        
        for pattern in quoted_text_patterns:
            content = re.sub(pattern, '', content)
        
        # Clean up whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _generate_inquiry_id(self) -> str:
        """Generate a unique ID for the inquiry."""
        # Use UUID to generate a unique ID
        return f"INQ-{uuid.uuid4().hex[:8].upper()}"
    
    def _extract_vendor_info(self, email_data: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """
        Try to extract vendor ID and name from the email.
        In a real system, this would look up the sender in a vendor database.
        
        Returns:
            Tuple of (vendor_id, vendor_name)
        """
        # Simplified implementation - in a real system, would query a vendor database
        vendor_id = None
        vendor_name = None
        
        # Try to extract from email domain
        from_email = email_data.get("from", "").strip()
        if "@" in from_email:
            domain = from_email.split("@")[-1]
            if domain:
                # Remove potential "<" and ">" characters
                domain = domain.replace("<", "").replace(">", "")
                
                # Use domain as a simplified vendor name
                vendor_name = domain.split(".")[0].title()
        
        # Try to extract from name part if available
        if "<" in from_email and ">" in from_email:
            match = re.match(r"(.*?)\s*<(.+?)>", from_email)
            if match:
                from_name = match.group(1).strip()
                if from_name:
                    # Use sender name as vendor name
                    vendor_name = from_name
                    
                    # In a real system, we would look up this name in a vendor database
                    # For now, generate a fake vendor ID based on the name
                    if from_name:
                        vendor_id = f"VEN-{uuid.uuid5(uuid.NAMESPACE_DNS, from_name).hex[:8].upper()}"
        
        return vendor_id, vendor_name
