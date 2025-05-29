"""
Minimal test app to debug CrewAI issues.
This app creates a simple agent and task to identify where the error is occurring.
"""

import os
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from crewai import Agent, Crew, Process
from crewai_fix import CompatibleTask, CompatibleCrew
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        
        # Create a simple task using the compatibility wrapper
        print("Creating task...")
        task = CompatibleTask.create(
            description="Return a simple JSON object with a 'test' key and 'success' value.",
            agent=agent,
            expected_output="A JSON object with a test key",
            async_execution=False,
            context=["This is a test task", "Please return a simple JSON object"]
        )
        
        # Create a crew with just this agent and task using the compatibility wrapper
        print("Creating crew...")
        crew = CompatibleCrew.create(
            agents=[agent],
            tasks=[task],
            verbose=2,
            process=Process.sequential
        )
        
        # Run the crew
        print("Running crew...")
        start_time = datetime.now()
        raw_result = crew.kickoff()
        end_time = datetime.now()
        
        print(f"Crew completed in {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Process the result using our compatibility wrapper
        print("Processing result with compatibility wrapper...")
        result = CompatibleCrew.process_result(raw_result)
        
        # Print the raw result type and content
        print(f"Raw result type: {type(raw_result)}")
        if isinstance(raw_result, str):
            print("Raw result is a string!")
            print(f"Raw result content: {raw_result[:200]}..." if len(raw_result) > 200 else raw_result)
        elif isinstance(raw_result, dict):
            print("Raw result is a dictionary!")
            print(json.dumps(raw_result, indent=2))
        else:
            print(f"Raw result is of type {type(raw_result)}")
            print(str(raw_result)[:200])
        
        # Print the processed result
        print("\nProcessed result:")
        print(json.dumps(result, indent=2))
        
        # Test accessing attributes
        print("\nTesting attribute access:")
        try:
            # Now we can safely use .get() since we've ensured result is a dictionary
            test_value = result.get('test', 'not found')
            print(f"Accessed 'test' attribute: {test_value}")
            
            # Try accessing 'output' if test is not found
            if test_value == 'not found':
                output_value = result.get('output', 'no output')
                print(f"Accessed 'output' attribute: {output_value[:100]}..." if len(output_value) > 100 else output_value)
        except Exception as e:
            print(f"Error accessing attributes: {str(e)}")
        
        return result
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_simple_test()
