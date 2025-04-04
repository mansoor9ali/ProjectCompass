"""
Test script for categories and departments database tables.
"""
import logging
import sys
from data.repository import get_repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test categories and departments tables."""
    try:
        # Get repository instance
        repository = get_repository()
        logger.info("Successfully connected to repository.")
        
        # Test categories
        categories = repository.get_categories()
        logger.info(f"Retrieved {len(categories)} categories:")
        for category in categories:
            logger.info(f"Category: {category['name']}, Count: {category['count']}, Percentage: {category['percentage']}%")
        
        # Test departments
        departments = repository.get_departments()
        logger.info(f"Retrieved {len(departments)} departments:")
        for dept in departments:
            logger.info(f"Department: {dept['name']}, Inquiry Count: {dept['inquiry_count']}, Response Time: {dept['avg_response_time']}")
        
        # Test category update
        if categories:
            test_category_id = categories[0]['id']
            logger.info(f"Testing update for category: {test_category_id}")
            
            # Update count and verify
            update_data = {'count': categories[0]['count'] + 5}
            success = repository.update_category(test_category_id, update_data)
            logger.info(f"Category update success: {success}")
            
            # Recalculate percentages
            repository.recalculate_category_percentages()
            
            # Verify update
            updated_categories = repository.get_categories()
            updated_category = next((cat for cat in updated_categories if cat['id'] == test_category_id), None)
            
            if updated_category:
                logger.info(f"Updated category count: {updated_category['count']}")
                logger.info(f"Updated category percentage: {updated_category['percentage']}%")
        
        # Test department update
        if departments:
            test_dept_id = departments[0]['id']
            logger.info(f"Testing update for department: {test_dept_id}")
            
            # Update inquiry count and verify
            update_data = {'inquiry_count': departments[0]['inquiry_count'] + 10}
            success = repository.update_department(test_dept_id, update_data)
            logger.info(f"Department update success: {success}")
            
            # Verify update
            updated_departments = repository.get_departments()
            updated_dept = next((dept for dept in updated_departments if dept['id'] == test_dept_id), None)
            
            if updated_dept:
                logger.info(f"Updated department inquiry count: {updated_dept['inquiry_count']}")
        
        logger.info("Category and department tests completed successfully.")
        
    except Exception as e:
        logger.error(f"Error testing categories and departments: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
