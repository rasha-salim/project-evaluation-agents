"""
Test script for the CrewAI patch.
"""

import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the patch first
print("Importing CrewAI patch...")
import crewai_patch

# Now import CrewAI
print("Importing CrewAI...")
from crewai import Agent, Task, Crew, Process
from config import get_config

def run_test():
    """Run a simple test with the patched CrewAI."""
    print("Starting test with patched CrewAI...")
    
    # Get configuration
    config = get_config()
    
    try:
        # Create a simple agent
        print("Creating agent...")
        agent = Agent(
            role="Test Agent",
            goal="Test the CrewAI patch",
            backstory="I am a test agent created to verify the CrewAI patch.",
            verbose=True,
            llm_config={
                'provider': config['api']['provider'],
                'model': config['api']['default_model'],
                'temperature': 0.7
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
        
        print("Task created successfully!")
        
        # Create a crew
        print("Creating crew...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=2,
            process=Process.sequential
        )
        
        print("Crew created successfully!")
        
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
            
            # Try to parse as JSON
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
    run_test()
