"""
ProjectCompass - Robocorp Task Runner

A simple script to run Robocorp tasks directly without going through the rcc environment.
This can help avoid environment creation issues when running tasks.
"""
import sys
import importlib.util
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_task(task_name):
    """
    Run a specific task from the tasks module
    
    Args:
        task_name: The name of the task function to run
    """
    try:
        # Import the tasks module
        logger.info(f"Importing tasks module...")
        
        # Add the current directory to the Python path if not already there
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import the tasks module
        import tasks
        
        # Get the task function
        task_func = getattr(tasks, task_name, None)
        if task_func is None:
            logger.error(f"Task '{task_name}' not found in tasks.py")
            print(f"Error: Task '{task_name}' not found in tasks.py")
            print(f"Available tasks: {[name for name in dir(tasks) if callable(getattr(tasks, name)) and not name.startswith('_')]}")
            return
        
        # Run the task
        logger.info(f"Running task '{task_name}'...")
        print(f"Running ProjectCompass task: {task_name}")
        print("-" * 50)
        task_func()
        
    except Exception as e:
        logger.error(f"Error running task: {str(e)}")
        print(f"Error running task: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python run_robocorp_task.py <task_name>")
        print("Available tasks:")
        print("  - email_inquiry_processor")
        print("  - run_dashboard")
        sys.exit(1)
    
    task_name = sys.argv[1]
    run_task(task_name)
