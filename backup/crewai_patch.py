"""
Patch for CrewAI to fix the 'str' object has no attribute 'get' error.
This module should be imported before any other CrewAI imports.
"""

import sys
import importlib
import types
import logging

logger = logging.getLogger(__name__)

def apply_patches():
    """Apply patches to fix CrewAI compatibility issues."""
    # Patch 1: Fix 'str' object has no attribute 'get' in process_config
    try:
        # Import the module that contains the problematic function
        import crewai.utilities.config as config_module
        
        # Store the original function
        original_process_config = config_module.process_config
        
        # Define a replacement for the process_config function
        def patched_process_config(values, cls):
            """Patched version of process_config that handles string values."""
            # Handle case where values is a string
            if isinstance(values, str):
                logger.warning(f"Received string instead of dict in process_config: {values[:50]}...")
                return {}
            
            # Original function logic
            config = values.get("config", {})
            if isinstance(config, dict):
                for key, value in config.items():
                    if key not in values:
                        values[key] = value
            return values
        
        # Replace the original function with our patched version
        config_module.process_config = patched_process_config
        logger.info("Successfully patched CrewAI's process_config function")
        
        # Patch 2: Fix any other potential issues in the Task class
        import crewai.task as task_module
        
        # Store the original Task.__init__ method
        original_task_init = task_module.Task.__init__
        
        # Define a replacement for the Task.__init__ method
        def patched_task_init(self, *args, **kwargs):
            """Patched version of Task.__init__ that handles string values."""
            # Ensure context is a list of strings
            if 'context' in kwargs:
                context = kwargs['context']
                if context is None:
                    kwargs['context'] = []
                elif isinstance(context, dict):
                    kwargs['context'] = [f"{k}: {v}" for k, v in context.items()]
                elif isinstance(context, list):
                    kwargs['context'] = [str(item) for item in context]
                else:
                    kwargs['context'] = [str(context)]
            
            # Ensure expected_output is a string
            if 'expected_output' in kwargs and not isinstance(kwargs['expected_output'], str):
                kwargs['expected_output'] = str(kwargs['expected_output'])
            
            # Call the original __init__ method
            try:
                original_task_init(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in Task.__init__: {str(e)}")
                # Fallback initialization with minimal parameters
                self.description = kwargs.get('description', '')
                self.agent = kwargs.get('agent', None)
                self.expected_output = kwargs.get('expected_output', '')
                self.async_execution = kwargs.get('async_execution', False)
                self.context = kwargs.get('context', [])
        
        # Replace the original method with our patched version
        task_module.Task.__init__ = patched_task_init
        logger.info("Successfully patched CrewAI's Task.__init__ method")
        
        return True
    except Exception as e:
        logger.error(f"Failed to patch CrewAI: {str(e)}")
        return False

# Apply patches when this module is imported
patch_successful = apply_patches()
