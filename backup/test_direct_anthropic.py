import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_fix import DirectAnthropicExecutor, CompatibleTask

# Load environment variables
load_dotenv()

def main():
    """Test the DirectAnthropicExecutor with a simple task"""
    print("Testing DirectAnthropicExecutor with a simple task")
    
    try:
        # Create a standard CrewAI agent with Anthropic config
        researcher = Agent(
            role="Researcher",
            goal="Research and provide information on a topic",
            backstory="You are an AI research assistant with expertise in finding and summarizing information.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.7,
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        )
        
        print("Agent created successfully")
        
        # Create a task using the compatibility wrapper
        research_task = CompatibleTask.create(
            description="Research and summarize information about artificial intelligence advancements in 2024.",
            agent=researcher,
            expected_output="A concise summary of AI advancements in 2024."
        )
        
        print("Task created successfully")
        
        # Execute the task directly using our DirectAnthropicExecutor
        print("Executing task directly with DirectAnthropicExecutor...")
        result = DirectAnthropicExecutor.execute_task(researcher, research_task)
        
        print("\nResult from direct execution:")
        print(result)
        
        print("\nTest completed successfully")
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
