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
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from models.inquiry import Inquiry, InquiryStatus
from models.vendor import Vendor

# Initialize logging
logger = logging.getLogger(__name__)

class Repository:
    """
    Data repository for storing and retrieving vendor and inquiry data.
    Uses PostgreSQL database for storage.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the repository with PostgreSQL connection.
        
        Args:
            data_dir: Directory for legacy data files (kept for backwards compatibility).
        """
        # Keep data_dir for backwards compatibility during migration
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'storage')
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # PostgreSQL connection settings from docker-compose environment
        self.db_config = {
            'host': 'postgres_db',  # Use 'postgres_db' when running inside docker network
            'port': 5432,
            'user': 'myuser',
            'password': 'mysecretpassword',
            'database': 'myvectordb'
        }
        
        # Initialize database and tables
        self._initialize_database()
        
        logger.info(f"Repository initialized with PostgreSQL database: {self.db_config['database']}")
    
    def _prepare_for_json(self, obj):
        """Prepare an object for JSON serialization, converting datetime objects to ISO strings."""
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(i) for i in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
            
    def _get_connection(self):
        """Get a PostgreSQL database connection."""
        try:
            connection = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            return connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist."""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Drop existing tables to ensure schema consistency
            # Comment out these DROP statements after successful migration in production
            cursor.execute("DROP TABLE IF EXISTS inquiries CASCADE")
            cursor.execute("DROP TABLE IF EXISTS vendors CASCADE")
            cursor.execute("DROP TABLE IF EXISTS categories CASCADE")
            cursor.execute("DROP TABLE IF EXISTS departments CASCADE")
            
            # Create inquiries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inquiries (
                    id VARCHAR(50) PRIMARY KEY,
                    vendor_id VARCHAR(50),
                    vendor_name VARCHAR(255),
                    status VARCHAR(50) NOT NULL,
                    category VARCHAR(100),
                    priority VARCHAR(50),
                    assigned_to VARCHAR(100),
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    due_by TIMESTAMP,
                    email_metadata JSONB,
                    raw_content TEXT,
                    processed_content TEXT,
                    confidence_score NUMERIC,
                    tags JSONB,
                    notes JSONB,
                    related_inquiries JSONB,
                    metadata JSONB
                )
            """)
            
            # Create vendors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendors (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    status VARCHAR(50),
                    registration_date TIMESTAMP NOT NULL,
                    prequalification_status VARCHAR(100),
                    contract_status VARCHAR(100),
                    financial_status VARCHAR(100),
                    contacts JSONB,
                    performance JSONB,
                    tags JSONB,
                    metadata JSONB
                )
            """)
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    count INTEGER DEFAULT 0,
                    percentage NUMERIC DEFAULT 0,
                    color VARCHAR(50),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create departments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    inquiry_count INTEGER DEFAULT 0,
                    avg_response_time NUMERIC DEFAULT 0,
                    load INTEGER DEFAULT 0,
                    manager VARCHAR(100),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert initial data for categories if table is empty
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO categories (id, name, description, count, percentage, color)
                    VALUES
                    ('cat-001', 'prequalification', 'Prequalification inquiries', 30, 25, '#FF6384'),
                    ('cat-002', 'finance', 'Finance-related inquiries', 24, 20, '#36A2EB'),
                    ('cat-003', 'contract', 'Contract-related inquiries', 18, 15, '#FFCE56'),
                    ('cat-004', 'bidding', 'Bidding-related inquiries', 12, 10, '#4BC0C0'),
                    ('cat-005', 'technical', 'Technical support inquiries', 24, 20, '#9966FF'),
                    ('cat-006', 'information', 'Information requests', 12, 10, '#FF9F40')
                """)
            
            # Insert initial data for departments if table is empty
            cursor.execute("SELECT COUNT(*) FROM departments")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO departments (id, name, description, inquiry_count, avg_response_time, load)
                    VALUES
                    ('dept-001', 'Registration', 'Handles vendor registration and prequalification', 42, 8.5, 65),
                    ('dept-002', 'Finance', 'Manages financial aspects of vendor relationships', 27, 12.3, 45),
                    ('dept-003', 'Contracts', 'Handles contract negotiations and management', 19, 24.7, 35),
                    ('dept-004', 'Technical Support', 'Provides technical assistance to vendors', 35, 4.2, 55)
                """)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            # If database connection fails, we could fall back to file-based storage
            logger.warning("Database initialization failed, might fall back to file storage")
    
    def save_inquiry(self, inquiry: Inquiry) -> bool:
        """
        Save an inquiry to storage.
        
        Args:
            inquiry: The inquiry to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Convert inquiry to dictionary and prepare for JSON serialization
            inquiry_dict = inquiry.to_dict()
            
            # Check if inquiry already exists
            cursor.execute("SELECT id FROM inquiries WHERE id = %s", (inquiry_dict['id'],))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing inquiry using the current model structure
                cursor.execute("""
                    UPDATE inquiries SET
                        vendor_id = %s,
                        vendor_name = %s,
                        status = %s,
                        category = %s,
                        priority = %s,
                        assigned_to = %s,
                        created_at = %s,
                        updated_at = %s,
                        due_by = %s,
                        email_metadata = %s,
                        raw_content = %s,
                        processed_content = %s,
                        confidence_score = %s,
                        tags = %s,
                        notes = %s,
                        related_inquiries = %s,
                        metadata = %s
                    WHERE id = %s
                """, (
                    inquiry_dict.get('vendor_id'),
                    inquiry_dict.get('vendor_name'),
                    inquiry_dict['status'],
                    inquiry_dict['category'],
                    inquiry_dict.get('priority'),
                    inquiry_dict.get('assigned_to'),
                    inquiry_dict['created_at'],
                    inquiry_dict['updated_at'],
                    inquiry_dict.get('due_by'),
                    Json(self._prepare_for_json(inquiry_dict['email_metadata'])),
                    inquiry_dict['raw_content'],
                    inquiry_dict.get('processed_content'),
                    inquiry_dict.get('confidence_score', 0.0),
                    Json(self._prepare_for_json(inquiry_dict.get('tags', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('notes', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('related_inquiries', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('metadata', {}))),
                    inquiry_dict['id']
                ))
                logger.info(f"Updated inquiry: {inquiry.id}")
            else:
                # Insert new inquiry
                cursor.execute("""
                    INSERT INTO inquiries (
                        id, vendor_id, vendor_name, status, category, priority,
                        assigned_to, created_at, updated_at, due_by,
                        email_metadata, raw_content, processed_content,
                        confidence_score, tags, notes, related_inquiries, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    inquiry_dict['id'],
                    inquiry_dict.get('vendor_id'),
                    inquiry_dict.get('vendor_name'),
                    inquiry_dict['status'],
                    inquiry_dict['category'],
                    inquiry_dict.get('priority'),
                    inquiry_dict.get('assigned_to'),
                    inquiry_dict['created_at'],
                    inquiry_dict['updated_at'],
                    inquiry_dict.get('due_by'),
                    Json(self._prepare_for_json(inquiry_dict['email_metadata'])),
                    inquiry_dict['raw_content'],
                    inquiry_dict.get('processed_content'),
                    inquiry_dict.get('confidence_score', 0.0),
                    Json(self._prepare_for_json(inquiry_dict.get('tags', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('notes', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('related_inquiries', []))),
                    Json(self._prepare_for_json(inquiry_dict.get('metadata', {})))
                ))
                logger.info(f"Added new inquiry: {inquiry.id}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
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
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM inquiries WHERE id = %s", (inquiry_id,))
            inquiry = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            # Convert result to dictionary if found
            if inquiry:
                # Convert to regular dict from RealDictRow
                inquiry = dict(inquiry)
                
                # Convert JSONB fields to dict
                for field in ['email_metadata', 'tags', 'notes', 'related_inquiries', 'metadata']:
                    if inquiry.get(field):
                        inquiry[field] = dict(inquiry[field])
                
                return inquiry
            
            return None
            
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
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM inquiries"
            params = []
            where_clauses = []
            
            # Apply filters
            if status:
                if isinstance(status, str):
                    where_clauses.append("status = %s")
                    params.append(status)
                else:
                    placeholders = ", ".join(["%s"] * len(status))
                    where_clauses.append(f"status IN ({placeholders})")
                    params.extend(status)
            
            if category:
                if isinstance(category, str):
                    where_clauses.append("category = %s")
                    params.append(category)
                else:
                    placeholders = ", ".join(["%s"] * len(category))
                    where_clauses.append(f"category IN ({placeholders})")
                    params.extend(category)
            
            # Add WHERE clause if filters are present
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY clause
            query += " ORDER BY created_at DESC"
            
            # Add pagination
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            inquiries = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert to dict and process JSONB fields
            result = []
            for inquiry in inquiries:
                inquiry_dict = dict(inquiry)
                
                # Convert JSONB fields to dict
                for field in ['email_metadata', 'tags', 'notes', 'related_inquiries', 'metadata']:
                    if inquiry_dict.get(field):
                        inquiry_dict[field] = dict(inquiry_dict[field])
                
                result.append(inquiry_dict)
            
            return result
            
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
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Convert vendor to dictionary and prepare for JSON serialization
            vendor_dict = vendor.to_dict()
            
            # Check if vendor already exists
            cursor.execute("SELECT id FROM vendors WHERE id = %s", (vendor_dict['id'],))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing vendor
                cursor.execute("""
                    UPDATE vendors SET
                        name = %s,
                        category = %s,
                        status = %s,
                        registration_date = %s,
                        prequalification_status = %s,
                        contract_status = %s,
                        financial_status = %s,
                        contacts = %s,
                        performance = %s,
                        tags = %s,
                        metadata = %s
                    WHERE id = %s
                """, (
                    vendor_dict['name'],
                    vendor_dict['category'],
                    vendor_dict['status'],
                    vendor_dict['registration_date'],
                    vendor_dict.get('prequalification_status'),
                    vendor_dict.get('contract_status'),
                    vendor_dict.get('financial_status'),
                    Json(self._prepare_for_json(vendor_dict.get('contacts', []))),
                    Json(self._prepare_for_json(vendor_dict.get('performance', {}))),
                    Json(self._prepare_for_json(vendor_dict.get('tags', []))),
                    Json(self._prepare_for_json(vendor_dict.get('metadata', {}))),
                    vendor_dict['id']
                ))
                logger.info(f"Updated vendor: {vendor.id}")
            else:
                # Insert new vendor
                cursor.execute("""
                    INSERT INTO vendors (
                        id, name, category, status, registration_date,
                        prequalification_status, contract_status, financial_status,
                        contacts, performance, tags, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    vendor_dict['id'],
                    vendor_dict['name'],
                    vendor_dict['category'],
                    vendor_dict['status'],
                    vendor_dict['registration_date'],
                    vendor_dict.get('prequalification_status'),
                    vendor_dict.get('contract_status'),
                    vendor_dict.get('financial_status'),
                    Json(self._prepare_for_json(vendor_dict.get('contacts', []))),
                    Json(self._prepare_for_json(vendor_dict.get('performance', {}))),
                    Json(self._prepare_for_json(vendor_dict.get('tags', []))),
                    Json(self._prepare_for_json(vendor_dict.get('metadata', {})))
                ))
                logger.info(f"Added new vendor: {vendor.id}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
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
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM vendors WHERE id = %s", (vendor_id,))
            vendor = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            # Convert result to dictionary if found
            if vendor:
                # Convert to regular dict from RealDictRow
                vendor = dict(vendor)
                
                # Convert JSONB fields to dict
                for field in ['contacts', 'performance', 'tags', 'metadata']:
                    if vendor.get(field):
                        vendor[field] = dict(vendor[field])
                
                return vendor
            
            return None
            
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
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM vendors"
            params = []
            where_clauses = []
            
            # Apply filters
            if status:
                where_clauses.append("status = %s")
                params.append(status)
            
            if category:
                where_clauses.append("category = %s")
                params.append(category)
            
            # Add WHERE clause if filters are present
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY clause
            query += " ORDER BY name ASC"
            
            # Add pagination
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            vendors = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert to dict and process JSONB fields
            result = []
            for vendor in vendors:
                vendor_dict = dict(vendor)
                
                # Convert JSONB fields to dict
                for field in ['contacts', 'performance', 'tags', 'metadata']:
                    if vendor_dict.get(field):
                        vendor_dict[field] = dict(vendor_dict[field])
                
                result.append(vendor_dict)
            
            return result
            
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
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Update status and updated_at timestamp
            cursor.execute("""
                UPDATE inquiries 
                SET status = %s, updated_at = %s 
                WHERE id = %s
            """, (status, datetime.now(), inquiry_id))
            
            # Check if any row was affected
            affected = cursor.rowcount > 0
            
            connection.commit()
            cursor.close()
            connection.close()
            
            if affected:
                logger.info(f"Updated inquiry status: {inquiry_id} -> {status}")
                return True
            else:
                logger.warning(f"Inquiry not found: {inquiry_id}")
                return False
            
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
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT COUNT(*) FROM inquiries"
            params = []
            
            if status:
                query += " WHERE status = %s"
                params.append(status)
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count
            
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
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT COUNT(*) FROM vendors"
            params = []
            
            if status:
                query += " WHERE status = %s"
                params.append(status)
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting vendor count: {str(e)}")
            return 0
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories with their statistics.
        
        Returns:
            List of category dictionaries
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, name, description, count, percentage, color
                FROM categories
                ORDER BY name ASC
            """)
            
            categories = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert RealDictRow objects to regular dictionaries
            return [dict(category) for category in categories]
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []
    
    def get_departments(self) -> List[Dict[str, Any]]:
        """
        Get all departments with their statistics.
        
        Returns:
            List of department dictionaries
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, name, description, inquiry_count, avg_response_time, load, manager
                FROM departments
                ORDER BY name ASC
            """)
            
            departments = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert RealDictRow objects to regular dictionaries
            return [dict(department) for department in departments]
            
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            return []
    
    def update_category(self, category_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a category's information.
        
        Args:
            category_id: ID of the category to update
            data: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Build the SET clause dynamically based on the data provided
            set_clauses = []
            params = []
            
            for key, value in data.items():
                if key not in ['id']:  # Don't allow updating the ID
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = %s")
            params.append(datetime.now())
            
            # Add category_id as the last parameter
            params.append(category_id)
            
            query = f"""
                UPDATE categories 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            cursor.execute(query, params)
            affected = cursor.rowcount > 0
            
            connection.commit()
            cursor.close()
            connection.close()
            
            if affected:
                logger.info(f"Updated category: {category_id}")
                return True
            else:
                logger.warning(f"Category not found: {category_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            return False
    
    def update_department(self, department_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a department's information.
        
        Args:
            department_id: ID of the department to update
            data: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Build the SET clause dynamically based on the data provided
            set_clauses = []
            params = []
            
            for key, value in data.items():
                if key not in ['id']:  # Don't allow updating the ID
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = %s")
            params.append(datetime.now())
            
            # Add department_id as the last parameter
            params.append(department_id)
            
            query = f"""
                UPDATE departments 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            cursor.execute(query, params)
            affected = cursor.rowcount > 0
            
            connection.commit()
            cursor.close()
            connection.close()
            
            if affected:
                logger.info(f"Updated department: {department_id}")
                return True
            else:
                logger.warning(f"Department not found: {department_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error updating department: {str(e)}")
            return False
    
    def recalculate_category_percentages(self) -> bool:
        """
        Recalculate category percentages based on counts.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Get total count across all categories
            cursor.execute("SELECT SUM(count) FROM categories")
            total = cursor.fetchone()[0] or 0
            
            if total > 0:
                # Update percentages for all categories
                cursor.execute("""
                    UPDATE categories
                    SET percentage = (count * 100.0 / %s)::numeric(5,2),
                        updated_at = %s
                """, (total, datetime.now()))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("Recalculated category percentages")
            return True
            
        except Exception as e:
            logger.error(f"Error recalculating category percentages: {str(e)}")
            return False
    
    def _migrate_legacy_data(self):
        """Migrate data from JSON files to PostgreSQL database."""
        try:
            # Migrate inquiries
            if os.path.exists(os.path.join(self.data_dir, 'inquiries.json')):
                with open(os.path.join(self.data_dir, 'inquiries.json'), 'r') as f:
                    inquiries = json.load(f)
                
                for inquiry_dict in inquiries:
                    # Convert string dates back to datetime objects for Inquiry constructor
                    if 'created_at' in inquiry_dict and isinstance(inquiry_dict['created_at'], str):
                        inquiry_dict['created_at'] = datetime.fromisoformat(inquiry_dict['created_at'])
                    if 'updated_at' in inquiry_dict and isinstance(inquiry_dict['updated_at'], str):
                        inquiry_dict['updated_at'] = datetime.fromisoformat(inquiry_dict['updated_at'])
                    if 'due_by' in inquiry_dict and inquiry_dict['due_by'] and isinstance(inquiry_dict['due_by'], str):
                        inquiry_dict['due_by'] = datetime.fromisoformat(inquiry_dict['due_by'])
                    
                    # Create Inquiry object and save to database
                    inquiry = Inquiry.from_dict(inquiry_dict)
                    self.save_inquiry(inquiry)
                
                logger.info(f"Migrated {len(inquiries)} inquiries from JSON to PostgreSQL")
            
            # Migrate vendors
            if os.path.exists(os.path.join(self.data_dir, 'vendors.json')):
                with open(os.path.join(self.data_dir, 'vendors.json'), 'r') as f:
                    vendors = json.load(f)
                
                for vendor_dict in vendors:
                    # Convert string dates back to datetime objects for Vendor constructor
                    if 'registration_date' in vendor_dict and isinstance(vendor_dict['registration_date'], str):
                        vendor_dict['registration_date'] = datetime.fromisoformat(vendor_dict['registration_date'])
                    if 'performance' in vendor_dict and vendor_dict['performance'].get('last_updated') and isinstance(vendor_dict['performance']['last_updated'], str):
                        vendor_dict['performance']['last_updated'] = datetime.fromisoformat(vendor_dict['performance']['last_updated'])
                    
                    # Create Vendor object and save to database
                    vendor = Vendor.from_dict(vendor_dict)
                    self.save_vendor(vendor)
                
                logger.info(f"Migrated {len(vendors)} vendors from JSON to PostgreSQL")
                
            return True
        except Exception as e:
            logger.error(f"Error migrating legacy data: {str(e)}")
            return False


# Singleton repository instance
_repository = None

def get_repository() -> Repository:
    """Get the singleton repository instance."""
    global _repository
    if _repository is None:
        _repository = Repository()
        
        # Attempt to migrate legacy data when first accessing the repository
        # Only uncomment this if you want to migrate data automatically on first access
        # _repository._migrate_legacy_data()
        
    return _repository
