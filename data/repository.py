"""
Data Repository for the ProjectCompass system.
Handles data storage and retrieval operations.
"""
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from models.inquiry import Inquiry, InquiryStatus
from models.vendor import Vendor

# Initialize logging
logger = logging.getLogger(__name__)

class Repository:
    """
    Data repository for storing and retrieving vendor and inquiry data.
    In a production environment, this would use a proper database.
    This implementation uses JSON files for simplicity.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the repository.
        
        Args:
            data_dir: Directory to store data files. Defaults to 'data/storage'.
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'storage')
        
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize storage paths
        self.vendors_file = os.path.join(self.data_dir, 'vendors.json')
        self.inquiries_file = os.path.join(self.data_dir, 'inquiries.json')
        
        # Create storage files if they don't exist
        self._initialize_storage()
        
        logger.info(f"Repository initialized with data directory: {self.data_dir}")
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist."""
        # Initialize vendors file
        if not os.path.exists(self.vendors_file):
            with open(self.vendors_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created vendors storage file: {self.vendors_file}")
        
        # Initialize inquiries file
        if not os.path.exists(self.inquiries_file):
            with open(self.inquiries_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created inquiries storage file: {self.inquiries_file}")
    
    def save_inquiry(self, inquiry: Inquiry) -> bool:
        """
        Save an inquiry to storage.
        
        Args:
            inquiry: The inquiry to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing inquiries
            inquiries = self._load_data(self.inquiries_file)
            
            # Convert inquiry to dictionary
            inquiry_dict = inquiry.to_dict()
            
            # Convert datetime objects to ISO format strings
            inquiry_dict['created_at'] = inquiry_dict['created_at'].isoformat()
            inquiry_dict['updated_at'] = inquiry_dict['updated_at'].isoformat()
            if inquiry_dict.get('due_by'):
                inquiry_dict['due_by'] = inquiry_dict['due_by'].isoformat()
            
            # Check if inquiry already exists
            existing_idx = next((i for i, inq in enumerate(inquiries) 
                               if inq.get('id') == inquiry_dict['id']), None)
            
            # Update or append
            if existing_idx is not None:
                inquiries[existing_idx] = inquiry_dict
                logger.info(f"Updated inquiry: {inquiry.id}")
            else:
                inquiries.append(inquiry_dict)
                logger.info(f"Added new inquiry: {inquiry.id}")
            
            # Save back to file
            self._save_data(self.inquiries_file, inquiries)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving inquiry: {str(e)}")
            return False
    
    def get_inquiry(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an inquiry by ID.
        
        Args:
            inquiry_id: The ID of the inquiry to retrieve
            
        Returns:
            Inquiry dictionary or None if not found
        """
        try:
            inquiries = self._load_data(self.inquiries_file)
            
            # Find inquiry by ID
            inquiry = next((inq for inq in inquiries if inq.get('id') == inquiry_id), None)
            
            return inquiry
            
        except Exception as e:
            logger.error(f"Error getting inquiry: {str(e)}")
            return None
    
    def get_inquiries(self, 
                      status: Optional[Union[str, List[str]]] = None, 
                      category: Optional[Union[str, List[str]]] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get inquiries with optional filtering.
        
        Args:
            status: Filter by status or list of statuses
            category: Filter by category or list of categories
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of inquiry dictionaries
        """
        try:
            inquiries = self._load_data(self.inquiries_file)
            
            # Apply filters
            if status:
                status_list = [status] if isinstance(status, str) else status
                inquiries = [inq for inq in inquiries if inq.get('status') in status_list]
            
            if category:
                category_list = [category] if isinstance(category, str) else category
                inquiries = [inq for inq in inquiries if inq.get('category') in category_list]
            
            # Sort by created_at date (newest first)
            inquiries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Apply pagination
            paginated = inquiries[offset:offset + limit]
            
            return paginated
            
        except Exception as e:
            logger.error(f"Error getting inquiries: {str(e)}")
            return []
    
    def save_vendor(self, vendor: Vendor) -> bool:
        """
        Save a vendor to storage.
        
        Args:
            vendor: The vendor to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing vendors
            vendors = self._load_data(self.vendors_file)
            
            # Convert vendor to dictionary
            vendor_dict = vendor.to_dict()
            
            # Convert datetime objects to ISO format strings
            vendor_dict['registration_date'] = vendor_dict['registration_date'].isoformat()
            if vendor_dict.get('performance', {}).get('last_updated'):
                vendor_dict['performance']['last_updated'] = vendor_dict['performance']['last_updated'].isoformat()
            
            # Check if vendor already exists
            existing_idx = next((i for i, v in enumerate(vendors) 
                               if v.get('id') == vendor_dict['id']), None)
            
            # Update or append
            if existing_idx is not None:
                vendors[existing_idx] = vendor_dict
                logger.info(f"Updated vendor: {vendor.id}")
            else:
                vendors.append(vendor_dict)
                logger.info(f"Added new vendor: {vendor.id}")
            
            # Save back to file
            self._save_data(self.vendors_file, vendors)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving vendor: {str(e)}")
            return False
    
    def get_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a vendor by ID.
        
        Args:
            vendor_id: The ID of the vendor to retrieve
            
        Returns:
            Vendor dictionary or None if not found
        """
        try:
            vendors = self._load_data(self.vendors_file)
            
            # Find vendor by ID
            vendor = next((v for v in vendors if v.get('id') == vendor_id), None)
            
            return vendor
            
        except Exception as e:
            logger.error(f"Error getting vendor: {str(e)}")
            return None
    
    def get_vendors(self, 
                   status: Optional[str] = None,
                   category: Optional[str] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get vendors with optional filtering.
        
        Args:
            status: Filter by status
            category: Filter by category
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of vendor dictionaries
        """
        try:
            vendors = self._load_data(self.vendors_file)
            
            # Apply filters
            if status:
                vendors = [v for v in vendors if v.get('status') == status]
            
            if category:
                vendors = [v for v in vendors if v.get('category') == category]
            
            # Sort by name
            vendors.sort(key=lambda x: x.get('name', ''))
            
            # Apply pagination
            paginated = vendors[offset:offset + limit]
            
            return paginated
            
        except Exception as e:
            logger.error(f"Error getting vendors: {str(e)}")
            return []
    
    def update_inquiry_status(self, inquiry_id: str, status: str) -> bool:
        """
        Update the status of an inquiry.
        
        Args:
            inquiry_id: The ID of the inquiry to update
            status: The new status
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get inquiry
            inquiry = self.get_inquiry(inquiry_id)
            if not inquiry:
                logger.warning(f"Inquiry not found: {inquiry_id}")
                return False
            
            # Update status
            inquiry['status'] = status
            inquiry['updated_at'] = datetime.now().isoformat()
            
            # Save back to storage
            inquiries = self._load_data(self.inquiries_file)
            
            # Find and update
            for i, inq in enumerate(inquiries):
                if inq.get('id') == inquiry_id:
                    inquiries[i] = inquiry
                    break
            
            # Save
            self._save_data(self.inquiries_file, inquiries)
            
            logger.info(f"Updated inquiry status: {inquiry_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating inquiry status: {str(e)}")
            return False
    
    def get_inquiry_count(self, status: Optional[str] = None) -> int:
        """
        Get the count of inquiries, optionally filtered by status.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            Count of inquiries
        """
        try:
            inquiries = self._load_data(self.inquiries_file)
            
            if status:
                inquiries = [inq for inq in inquiries if inq.get('status') == status]
            
            return len(inquiries)
            
        except Exception as e:
            logger.error(f"Error getting inquiry count: {str(e)}")
            return 0
    
    def get_vendor_count(self, status: Optional[str] = None) -> int:
        """
        Get the count of vendors, optionally filtered by status.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            Count of vendors
        """
        try:
            vendors = self._load_data(self.vendors_file)
            
            if status:
                vendors = [v for v in vendors if v.get('status') == status]
            
            return len(vendors)
            
        except Exception as e:
            logger.error(f"Error getting vendor count: {str(e)}")
            return 0
    
    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}, creating empty file")
            with open(file_path, 'w') as f:
                json.dump([], f)
            return []
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in file: {file_path}, resetting to empty list")
            with open(file_path, 'w') as f:
                json.dump([], f)
            return []
    
    def _save_data(self, file_path: str, data: List[Dict[str, Any]]):
        """Save data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


# Singleton repository instance
_repository = None

def get_repository() -> Repository:
    """Get the singleton repository instance."""
    global _repository
    if _repository is None:
        _repository = Repository()
    return _repository
