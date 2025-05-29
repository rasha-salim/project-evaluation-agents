import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
import json

# Load environment variables
load_dotenv()

def main():
    """Test creating an agent with Anthropic"""
    print("Testing agent creation with Anthropic")
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: No Anthropic API key found in environment variables")
        return
    
    print(f"API key exists: {bool(api_key)}")
    print(f"API key (first 5 chars): {api_key[:5]}...")
    
    try:
        # Create agent with explicit Anthropic config
        agent = Agent(
            role="Tester",
            goal="Test Anthropic integration",
            backstory="I am a test agent for Anthropic integration",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.7,
                "api_key": api_key
            }
        )
        
        # Print agent configuration
        print("\nAgent created successfully")
        print(f"Agent role: {agent.role}")
        
        # Check if the agent is using Anthropic
        print("\nAgent LLM configuration:")
        # Try to access the LLM config
        if hasattr(agent, 'llm') and hasattr(agent.llm, 'model_name'):
            print(f"Model name: {agent.llm.model_name}")
        if hasattr(agent, 'llm') and hasattr(agent.llm, 'provider'):
            print(f"Provider: {agent.llm.provider}")
        
        # Create a task for the agent
        print("\nCreating a task for the agent...")
        task = Task(
            description="Say hello and identify yourself as an Anthropic Claude model.",
            agent=agent,
            expected_output="A greeting and self-identification"
        )
        
        # Create a crew with the agent and task
        print("Creating a crew with the agent and task...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        # Run the crew
        print("Running the crew...")
        result = crew.kickoff()
        print(f"Result: {result}")
        
        print("\nTest completed successfully")
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
