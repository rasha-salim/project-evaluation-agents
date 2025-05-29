"""
Task module for direct Anthropic integration.
This module provides the Task class for defining and executing tasks.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from .agent import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Task:
    """
    Task class for defining and executing tasks.
    """
    
    def __init__(
        self,
        description: str,
        agent: Agent,
        expected_output: Optional[str] = None,
        context: Optional[Union[List[str], Dict[str, Any], str]] = None,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize a Task.
        
        Args:
            description: The description of the task
            agent: The agent assigned to the task
            expected_output: Description of the expected output
            context: Additional context for the task
            dependencies: List of task IDs that this task depends on
        """
        self.description = description
        self.agent = agent
        self.expected_output = expected_output or "Provide a well-structured output"
        self.context = context
        self.dependencies = dependencies or []
        
        # Add expected output to description
        if expected_output:
            self.description += f"\n\nExpected Output: {expected_output}"
    
    def execute(self, additional_context: Optional[Union[List[str], Dict[str, Any], str]] = None) -> str:
        """
        Execute the task using the assigned agent.
        
        Args:
            additional_context: Additional context to add to the task
            
        Returns:
            The result of the task execution
        """
        # Combine existing context with additional context
        combined_context = self.context
        
        if additional_context:
            if combined_context is None:
                combined_context = additional_context
            elif isinstance(combined_context, list) and isinstance(additional_context, list):
                combined_context.extend(additional_context)
            elif isinstance(combined_context, dict) and isinstance(additional_context, dict):
                combined_context.update(additional_context)
            else:
                # Convert to strings and combine
                context_str = str(combined_context) if combined_context else ""
                additional_str = str(additional_context)
                combined_context = f"{context_str}\n{additional_str}" if context_str else additional_str
        
        # Execute the task
        return self.agent.execute_task(self.description, combined_context)
