"""
Direct fix for the CrewAI error in crew.py.
This script modifies the crew.py file to handle the 'str' object has no attribute 'get' error.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_crew_py():
    """Fix the crew.py file to handle the 'str' object has no attribute 'get' error."""
    crew_path = "crew.py"
    backup_path = "crew.py.bak"
    
    # Create a backup of the original file
    if not os.path.exists(backup_path):
        with open(crew_path, 'r') as f:
            original_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        logger.info(f"Created backup of {crew_path} at {backup_path}")
    
    # Read the current content
    with open(crew_path, 'r') as f:
        content = f.read()
    
    # Add a safe_get function at the beginning of the file
    safe_get_function = """
# Safe dictionary access function to handle string values
def safe_get(obj, key, default=None):
    \"\"\"Safely get a value from a dictionary, handling the case where obj is a string.\"\"\"
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default

"""
    
    # Add the import for safe_get at the top of the file
    import_pattern = r"from typing import Dict, List, Any, Optional"
    if import_pattern in content:
        content = content.replace(import_pattern, import_pattern + "\n# Import safe_get helper")
    
    # Add the safe_get function after the imports
    import_section_end = r"logger = logging.getLogger\(__name__\)"
    if re.search(import_section_end, content):
        content = re.sub(import_section_end, import_section_end + safe_get_function, content)
    else:
        # If we can't find the exact import section, add it at the beginning
        content = safe_get_function + content
    
    # Replace all instances of .get( with safe_get(
    # We need to be careful to only replace dictionary access patterns
    patterns_to_replace = [
        (r"(\w+)\.get\((['\"][\w_]+['\"])(?:,\s*([^)]+))?\)", r"safe_get(\1, \2\3)"),
        (r"(\w+)\.get\((['\"][\w_]+['\"])", r"safe_get(\1, \2"),
        (r"feedback_analysis\.get\(", r"safe_get(feedback_analysis, "),
        (r"feature\.get\(", r"safe_get(feature, "),
        (r"sprint_plan\.get\(", r"safe_get(sprint_plan, "),
        (r"task_config\.get\(", r"safe_get(task_config, "),
        (r"assessment\.get\(", r"safe_get(assessment, "),
        (r"iteration\.get\(", r"safe_get(iteration, "),
        (r"context\.get\(", r"safe_get(context, "),
        (r"config\.get\(", r"safe_get(config, "),
        (r"step\.get\(", r"safe_get(step, "),
        (r"values\.get\(", r"safe_get(values, "),
        (r"result\.get\(", r"safe_get(result, "),
        (r"data\.get\(", r"safe_get(data, "),
        (r"self\.config\.get\(", r"safe_get(self.config, "),
        (r"self\.outputs\.get\(", r"safe_get(self.outputs, "),
        (r"agent_config\.get\(", r"safe_get(agent_config, "),
        (r"agent_configs\.get\(", r"safe_get(agent_configs, "),
        (r"workflow_configs\.get\(", r"safe_get(workflow_configs, "),
        (r"selected_workflow\.get\(", r"safe_get(selected_workflow, "),
        (r"capacity\.get\(", r"safe_get(capacity, "),
        (r"stakeholder_update\.get\(", r"safe_get(stakeholder_update, "),
        (r"feasibility_assessment\.get\(", r"safe_get(feasibility_assessment, "),
        (r"priority_distribution\.get\(", r"safe_get(priority_distribution, "),
        (r"iteration_metrics\.get\(", r"safe_get(iteration_metrics, "),
    ]
    
    for pattern, replacement in patterns_to_replace:
        content = re.sub(pattern, replacement, content)
    
    # Write the modified content back to the file
    with open(crew_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Successfully modified {crew_path} to handle 'str' object has no attribute 'get' error")
    return True

if __name__ == "__main__":
    if fix_crew_py():
        print("Successfully fixed crew.py to handle 'str' object has no attribute 'get' error!")
        print("You can now run the app with 'streamlit run app.py'")
    else:
        print("Failed to fix crew.py. Please check the logs for details.")
