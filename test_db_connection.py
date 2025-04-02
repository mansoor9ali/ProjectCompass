"""
Test script to verify PostgreSQL connection and repository functions.
"""
import logging
import uuid
from datetime import datetime, timedelta
from data.repository import get_repository
from models.inquiry import Inquiry, InquiryStatus, InquiryPriority, InquiryCategory, EmailMetadata
from models.vendor import Vendor, VendorContact, VendorPerformance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test connecting to the PostgreSQL database."""
    try:
        # Get the repository instance
        repository = get_repository()
        
        # Test connection by getting counts
        inquiry_count = repository.get_inquiry_count()
        vendor_count = repository.get_vendor_count()
        
        logger.info(f"Successfully connected to database.")
        logger.info(f"Current inquiry count: {inquiry_count}")
        logger.info(f"Current vendor count: {vendor_count}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return False

def test_raw_sql():
    """Test direct SQL operations to verify database structure."""
    try:
        repository = get_repository()
        connection = repository._get_connection()
        
        # Test inserting a simple row directly with SQL
        cursor = connection.cursor()
        
        # Insert a test vendor with minimal fields
        vendor_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO vendors (id, name, category, status, registration_date) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            vendor_id,
            "Test SQL Vendor",
            "IT",
            "active",
            datetime.now()
        ))
        
        # Verify it was inserted
        cursor.execute("SELECT COUNT(*) FROM vendors")
        count = cursor.fetchone()[0]
        logger.info(f"Vendor count after direct SQL insert: {count}")
        
        # Insert a test inquiry with minimal fields
        inquiry_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO inquiries (
                id, status, category, created_at, updated_at, 
                raw_content, email_metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            inquiry_id,
            "new",
            "information",
            datetime.now(),
            datetime.now(),
            "Test content",
            '{}'  # Empty JSON object for email_metadata
        ))
        
        # Verify it was inserted
        cursor.execute("SELECT COUNT(*) FROM inquiries")
        count = cursor.fetchone()[0]
        logger.info(f"Inquiry count after direct SQL insert: {count}")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Error in direct SQL test: {str(e)}")
        return False

if __name__ == "__main__":
    # Test database connection
    if test_database_connection():
        # Test direct SQL operations
        test_raw_sql()
    else:
        logger.error("Database connection test failed. Please check PostgreSQL connection settings.")
