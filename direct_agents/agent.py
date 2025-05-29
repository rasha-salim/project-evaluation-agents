"""
Agent module for direct Anthropic integration.
This module provides the core Agent class that uses Anthropic's API directly.
"""

import os
import anthropic
import logging
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Agent:
    """
    Agent class that uses Anthropic's API directly.
    """
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = False,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialize an Agent.
        
        Args:
            role: The role of the agent (e.g., "Researcher", "Product Manager")
            goal: The goal of the agent
            backstory: The backstory of the agent
            verbose: Whether to print verbose output
            model: The Anthropic model to use
            temperature: The temperature for generation
            anthropic_api_key: The Anthropic API key (will use env var if not provided)
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.model = model
        self.temperature = temperature
        
        # Get API key from environment if not provided
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and not found in environment variables")
        
        # Initialize the Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        if self.verbose:
            logger.info(f"Initialized agent: {self.role}")
    
    def execute_task(self, task_description: str, context: Optional[Union[List[str], Dict[str, Any], str]] = None) -> str:
        """
        Execute a task using the Anthropic API directly.
        
        Args:
            task_description: The description of the task to execute
            context: Additional context for the task
            
        Returns:
            The result of the task execution
        """
        # Process context
        context_str = ""
        if context:
            if isinstance(context, list):
                context_str = "\n".join(context)
            elif isinstance(context, dict):
                context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
            else:
                context_str = str(context)
        
        # Create the prompt
        prompt = f"""
Role: {self.role}
Goal: {self.goal}
Backstory: {self.backstory}

Task: {task_description}
"""
        
        if context_str:
            prompt += f"\nContext:\n{context_str}\n"
        
        prompt += "\nPlease complete this task to the best of your abilities."
        
        # Make the API call
        try:
            if self.verbose:
                logger.info(f"Agent ({self.role}) executing task: {task_description[:100]}...")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = message.content[0].text
            
            if self.verbose:
                logger.info(f"Agent ({self.role}) completed task")
            
            return response
        except Exception as e:
            error_msg = f"Error executing task with Anthropic API: {str(e)}"
            logger.error(error_msg)
            return error_msg
