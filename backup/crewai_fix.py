"""
Compatibility fixes for CrewAI.
This module provides wrapper classes to handle compatibility issues with newer CrewAI versions
and fixes for the LLM provider selection.
"""

import os
import anthropic
from typing import Any, Dict, List, Optional, Union
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a global Anthropic client
_anthropic_client = None

def get_anthropic_client():
    """Get or create a global Anthropic client"""
    global _anthropic_client
    if _anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        _anthropic_client = anthropic.Anthropic(api_key=api_key)
    return _anthropic_client

class DirectAnthropicExecutor:
    """A utility class to execute tasks using the Anthropic API directly"""
    
    @staticmethod
    def execute_task(agent: Agent, task: Task) -> str:
        """Execute a task using the Anthropic API directly"""
        # Get the Anthropic client
        client = get_anthropic_client()
        
        # Get the task description
        task_description = task.description
        # Add context if available
        if hasattr(task, 'context') and task.context:
            if isinstance(task.context, list):
                context_str = "\n".join(task.context)
                task_description += f"\n\nContext:\n{context_str}"
            else:
                task_description += f"\n\nContext:\n{task.context}"
        
        # Create the prompt
        prompt = f"""
Role: {agent.role}
Goal: {agent.goal}
Backstory: {agent.backstory}

Task: {task_description}

Please complete this task to the best of your abilities.
"""
        
        # Make the API call
        try:
            if agent.verbose:
                print(f"DirectAnthropicExecutor: Agent ({agent.role}) executing task: {task_description[:100]}...")
            
            # Get model from agent's llm_config if available, otherwise use default
            model = "claude-3-haiku-20240307"
            temperature = 0.7
            
            if hasattr(agent, 'llm_config') and agent.llm_config:
                if isinstance(agent.llm_config, dict):
                    model = agent.llm_config.get("model", model)
                    temperature = agent.llm_config.get("temperature", temperature)
            
            message = client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = message.content[0].text
            
            if agent.verbose:
                print(f"DirectAnthropicExecutor: Agent ({agent.role}) completed task")
            
            return response
        except Exception as e:
            error_msg = f"Error executing task with Anthropic API: {str(e)}"
            print(error_msg)
            return error_msg

from typing import Any, Dict, List, Optional, Union
from crewai import Agent, Task, Crew, Process

class CompatibleTask:
    """
    A wrapper around CrewAI's Task class that handles compatibility issues.
    """
    
    @staticmethod
    def create(
        description: str,
        agent: Agent,
        expected_output: Optional[str] = None,
        async_execution: bool = False,
        context: Optional[Union[List[str], Dict[str, Any]]] = None
    ) -> Task:
        """
        Create a Task instance with compatibility fixes.
        
        Args:
            description: Task description
            agent: Agent assigned to the task
            expected_output: Expected output description
            async_execution: Whether to execute the task asynchronously
            context: Additional context for the task
            
        Returns:
            A Task instance
        """
        # Handle context conversion
        processed_context = None
        if context:
            if isinstance(context, dict):
                # Convert dict to list of strings
                processed_context = [f"{k}: {v}" for k, v in context.items()]
            elif isinstance(context, list):
                # Ensure all items are strings
                processed_context = [str(item) for item in context]
            else:
                # Convert to string
                processed_context = [str(context)]
        
        # Create the task with processed parameters
        return Task(
            description=description,
            agent=agent,
            expected_output=expected_output if expected_output else "Provide a well-structured output",
            async_execution=async_execution,
            context=processed_context
        )

class CompatibleCrew:
    """
    A wrapper around CrewAI's Crew class that handles compatibility issues.
    """
    
    @staticmethod
    def create(
        agents: List[Agent],
        tasks: List[Task],
        verbose: int = 2,
        process: Process = Process.sequential
    ) -> Crew:
        """
        Create a Crew instance with compatibility fixes.
        
        Args:
            agents: List of agents
            tasks: List of tasks
            verbose: Verbosity level
            process: Process type
            
        Returns:
            A Crew instance
        """
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=verbose,
            process=process
        )
    
    @staticmethod
    def process_result(result: Any) -> Dict[str, Any]:
        """
        Process the result from a crew execution to ensure it's a dictionary.
        
        Args:
            result: Result from crew.kickoff()
            
        Returns:
            Dictionary representation of the result
        """
        if isinstance(result, dict):
            return result
        elif isinstance(result, str):
            # Try to parse as JSON
            import json
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Return as a simple dictionary
                return {"output": result}
        else:
            # Convert to string and return
            return {"output": str(result)}
