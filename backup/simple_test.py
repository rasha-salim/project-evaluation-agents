"""
Simple test script to identify the exact issue with CrewAI.
"""

import os
import json
from datetime import datetime

# Monkey patch the problematic function in CrewAI before importing it
import sys
import types

def patch_crewai():
    """Patch the CrewAI library to fix the 'str' object has no attribute 'get' error."""
    try:
        # Import the module that contains the problematic function
        import crewai.utilities.config as config_module
        
        # Define a replacement for the process_config function
        def patched_process_config(values, cls):
            """Patched version of process_config that handles string values."""
            if isinstance(values, str):
                print(f"WARNING: Received string instead of dict in process_config: {values[:50]}...")
                # Return empty dict as fallback
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
        print("Successfully patched CrewAI's process_config function")
        return True
    except Exception as e:
        print(f"Failed to patch CrewAI: {str(e)}")
        return False

# Apply the patch
patch_successful = patch_crewai()

# Now import CrewAI
from crewai import Agent, Task, Crew, Process
from config import get_config

def get_api_key(provider):
    """Get API key for the specified provider."""
    if provider == 'anthropic':
        return os.environ.get('ANTHROPIC_API_KEY')
    elif provider == 'openai':
        return os.environ.get('OPENAI_API_KEY')
    return None

def run_simple_test():
    """Run a simple test with one agent and one task."""
    print("Starting simple CrewAI test...")
    
    # Get configuration
    config = get_config()
    api_provider = config['api']['provider']
    api_key = get_api_key(api_provider)
    
    if not api_key:
        print(f"No API key found for {api_provider}. Using default.")
    
    try:
        # Create a simple agent
        print("Creating agent...")
        agent = Agent(
            role="Test Agent",
            goal="Test the CrewAI framework",
            backstory="I am a test agent created to debug CrewAI issues.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                'provider': api_provider,
                'model': config['api']['default_model'],
                'temperature': 0.7,
                'api_key': api_key
            }
        )
        
        # Create a simple task
        print("Creating task...")
        task = Task(
            description="Return a simple JSON object with a 'test' key and 'success' value.",
            agent=agent,
            expected_output="A JSON object with a test key",
            async_execution=False,
            context=["This is a test task", "Please return a simple JSON object"]
        )
        
        # Create a crew with just this agent and task
        print("Creating crew...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=2,
            process=Process.sequential
        )
        
        # Run the crew
        print("Running crew...")
        start_time = datetime.now()
        result = crew.kickoff()
        end_time = datetime.now()
        
        print(f"Crew completed in {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Process the result
        print(f"Result type: {type(result)}")
        if isinstance(result, str):
            print("Result is a string!")
            print(f"Result content: {result[:200]}..." if len(result) > 200 else result)
            
            # Try to parse the string as JSON
            try:
                json_result = json.loads(result)
                print("Successfully parsed result as JSON:")
                print(json.dumps(json_result, indent=2))
                return json_result
            except json.JSONDecodeError:
                print("Result is not valid JSON")
                return {"output": result}
        elif isinstance(result, dict):
            print("Result is a dictionary!")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Result is of type {type(result)}")
            print(str(result)[:200])
            return {"output": str(result)}
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_simple_test()
