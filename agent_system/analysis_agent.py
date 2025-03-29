"""
Analysis Agent for analyzing and categorizing vendor inquiries.
"""
import logging
import re
import nltk
from typing import Dict, List, Tuple, Optional
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from models.inquiry import Inquiry, InquiryCategory, InquiryType, InquiryStatus

# Initialize logging
logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Specialized agent for analyzing email content and categorizing inquiries.
    Uses NLP techniques to determine the category and type of inquiry.
    """
    
    def __init__(self):
        """Initialize the Analysis Agent with NLP tools."""
        logger.info("Initializing Analysis Agent")
        
        # Initialize NLP components
        try:
            # Download necessary NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            logger.warning(f"Could not initialize all NLP components: {str(e)}")
            # Fallback to simpler approach if NLP tools aren't available
            self.nlp = None
        
        # Define keyword dictionaries for categories and types
        self._initialize_keyword_dictionaries()
    
    def _initialize_keyword_dictionaries(self):
        """Initialize keyword dictionaries for categorization."""
        # Category keywords
        self.category_keywords = {
            InquiryCategory.PREQUALIFICATION: [
                "prequalification", "pre-qualification", "qualify", "qualification", 
                "prerequisites", "pre-requisites", "registration", "onboarding"
            ],
            InquiryCategory.FINANCE: [
                "payment", "invoice", "billing", "financial", "tax", "finance",
                "accounting", "receipt", "reimbursement", "credit", "debit"
            ],
            InquiryCategory.CONTRACT: [
                "contract", "agreement", "terms", "conditions", "clause",
                "termination", "renewal", "amendment", "legal", "contractual"
            ],
            InquiryCategory.BIDDING: [
                "bid", "tender", "proposal", "rfp", "rfi", "rfq", "offer",
                "quotation", "submission", "procurement", "pricing"
            ],
            InquiryCategory.ISSUE: [
                "issue", "problem", "error", "mistake", "bug", "defect",
                "malfunction", "trouble", "difficulty", "complaint", "concern"
            ],
            InquiryCategory.INFORMATION: [
                "information", "details", "guide", "instructions", "clarification",
                "explain", "process", "procedure", "steps", "how to", "help"
            ],
        }
        
        # Type keywords (subset for demonstration)
        self.type_keywords = {
            InquiryType.APPLICATION_STATUS: [
                "status", "application", "progress", "submitted", "review", "accepted", "rejected"
            ],
            InquiryType.DOCUMENT_SUBMISSION: [
                "document", "upload", "submit", "attach", "certificate", "form", "paperwork"
            ],
            InquiryType.PAYMENT_STATUS: [
                "payment", "paid", "pending", "overdue", "scheduled", "processed"
            ],
            InquiryType.CONTRACT_TERMS: [
                "terms", "conditions", "clause", "agreement", "provision", "stipulation"
            ],
            InquiryType.BID_SUBMISSION: [
                "submit", "submission", "deadline", "requirements", "upload", "proposal"
            ],
            InquiryType.TECHNICAL_ISSUE: [
                "technical", "system", "error", "platform", "website", "portal", "login"
            ],
            InquiryType.PROCESS_INFORMATION: [
                "process", "procedure", "steps", "information", "guide", "instruction", "timeline"
            ],
            # Add more type keywords as needed
        }
    
    def analyze_inquiry(self, inquiry: Inquiry) -> Inquiry:
        """
        Analyze an inquiry to determine its category and type.
        
        Args:
            inquiry: The inquiry to analyze
            
        Returns:
            Updated inquiry with category and type
        """
        logger.info(f"Analyzing inquiry {inquiry.id}")
        
        # Extract text from email
        subject = inquiry.email_metadata.subject
        content = inquiry.raw_content
        
        # Combine subject and content for analysis
        text = f"{subject} {content}"
        
        # Perform categorization
        category, category_confidence = self._categorize_inquiry(text)
        inquiry_type, type_confidence = self._determine_inquiry_type(text, category)
        
        # Update the inquiry
        inquiry.category = category
        inquiry.inquiry_type = inquiry_type
        inquiry.confidence_score = (category_confidence + type_confidence) / 2
        inquiry.status = InquiryStatus.CATEGORIZED
        inquiry.processed_content = self._extract_key_information(text)
        
        # Extract vendor information if possible
        vendor_info = self._extract_vendor_info(text, inquiry.email_metadata.from_email)
        if vendor_info.get("name"):
            inquiry.vendor_name = vendor_info.get("name")
        
        return inquiry
    
    def _categorize_inquiry(self, text: str) -> Tuple[InquiryCategory, float]:
        """
        Determine the category of an inquiry based on text content.
        
        Args:
            text: The text to analyze
            
        Returns:
            Tuple of (category, confidence_score)
        """
        # Preprocess text
        text = text.lower()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Select category with highest score
        if not scores or max(scores.values()) == 0:
            return InquiryCategory.OTHER, 0.5
        
        best_category = max(scores.items(), key=lambda x: x[1])[0]
        total_score = sum(scores.values())
        confidence = scores[best_category] / total_score if total_score > 0 else 0.5
        
        return best_category, min(confidence + 0.3, 1.0)  # Add base confidence
    
    def _determine_inquiry_type(self, text: str, category: InquiryCategory) -> Tuple[Optional[InquiryType], float]:
        """
        Determine the specific type of inquiry within its category.
        
        Args:
            text: The text to analyze
            category: The determined category
            
        Returns:
            Tuple of (inquiry_type, confidence_score)
        """
        text = text.lower()
        
        # Count keyword matches for each type
        scores = {}
        for inquiry_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[inquiry_type] = score
        
        # Select type with highest score
        if not scores or max(scores.values()) == 0:
            return InquiryType.GENERAL, 0.5
        
        best_type = max(scores.items(), key=lambda x: x[1])[0]
        total_score = sum(scores.values())
        confidence = scores[best_type] / total_score if total_score > 0 else 0.5
        
        return best_type, confidence
    
    def _extract_key_information(self, text: str) -> str:
        """Extract key information from the email text."""
        # Simplified implementation - in production this would use more sophisticated NLP
        lines = text.split('\n')
        important_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines with important indicators
            indicators = ["urgent", "important", "question", "request", "deadline",
                         "need", "please", "help", "issue", "problem", "when",
                         "where", "who", "how", "why", "what"]
            
            if any(indicator in line.lower() for indicator in indicators):
                important_lines.append(line)
        
        # If we didn't find important lines, return first few non-empty lines
        if not important_lines:
            important_lines = [line for line in lines if line.strip()][:5]
        
        return "\n".join(important_lines)
    
    def _extract_vendor_info(self, text: str, email: str) -> Dict[str, str]:
        """
        Extract vendor information from the email.
        
        Args:
            text: The email text
            email: The sender's email address
            
        Returns:
            Dictionary with vendor information
        """
        # This is a simplified implementation
        result = {"email": email}
        
        # Try to extract name from email signature patterns
        signature_patterns = [
            r"Regards,[\s\n]+([A-Za-z\s]+)",
            r"Sincerely,[\s\n]+([A-Za-z\s]+)",
            r"Best regards,[\s\n]+([A-Za-z\s]+)",
            r"Thanks,[\s\n]+([A-Za-z\s]+)",
            r"Thank you,[\s\n]+([A-Za-z\s]+)",
            r"\n([A-Za-z\s]+)\n[A-Za-z\s]*[Dd]epartment",
            r"\n([A-Za-z\s]+)\n[A-Za-z\s]*[Cc]ompany",
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if name and len(name) < 50:  # Sanity check
                    result["name"] = name
                    break
        
        # Try to extract company name
        company_patterns = [
            r"[Cc]ompany:[\s\n]+([A-Za-z0-9\s&.,]+)",
            r"[Ff]rom[\s\n]+([A-Za-z0-9\s&.,]+)[Cc]ompany",
            r"on behalf of[\s\n]+([A-Za-z0-9\s&.,]+)"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                if company and len(company) < 100:  # Sanity check
                    result["company"] = company
                    break
        
        return result
