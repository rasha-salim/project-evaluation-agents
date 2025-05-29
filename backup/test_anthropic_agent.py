import os
from dotenv import load_dotenv
from crewai import Task, Crew, Process
from crewai_fix import AnthropicAgent, CompatibleTask

# Load environment variables
load_dotenv()

def main():
    """Test the AnthropicAgent with a simple task"""
    print("Testing AnthropicAgent with a simple task")
    
    try:
        # Create an AnthropicAgent
        researcher = AnthropicAgent(
            role="Researcher",
            goal="Research and provide information on a topic",
            backstory="You are an AI research assistant with expertise in finding and summarizing information.",
            verbose=True
        )
        
        print("AnthropicAgent created successfully")
        
        # Create a task using the compatibility wrapper
        research_task = CompatibleTask.create(
            description="Research and summarize information about artificial intelligence advancements in 2024.",
            agent=researcher,
            expected_output="A concise summary of AI advancements in 2024."
        )
        
        print("Task created successfully")
        
        # Create a crew with the agent and task
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True,
            process=Process.sequential
        )
        
        print("Crew created successfully")
        
        # Run the crew
        print("Running the crew...")
        result = crew.kickoff()
        
        print("\nResult from crew execution:")
        print(result)
        
        print("\nTest completed successfully")
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
