"""
Test script for the direct Anthropic integration.
"""

import os
import time
from dotenv import load_dotenv
from direct_agents.agent import Agent
from direct_agents.task import Task
from direct_agents.crew import Crew

# Load environment variables
load_dotenv()

def main():
    """Test the direct Anthropic integration"""
    print("Testing direct Anthropic integration")
    
    try:
        # Create agents
        researcher = Agent(
            role="Researcher",
            goal="Research and analyze user feedback data",
            backstory="You are an AI research analyst with expertise in data analysis and user feedback interpretation.",
            verbose=True
        )
        
        feature_planner = Agent(
            role="Feature Planner",
            goal="Generate feature proposals based on user feedback",
            backstory="You are a product manager who specializes in translating user feedback into actionable feature proposals.",
            verbose=True
        )
        
        print("Agents created successfully")
        
        # Create tasks
        feedback_task = Task(
            description="Analyze the following user feedback and identify key patterns and priorities:\n\n" +
                       "User 1: 'The app crashes when I try to upload large files.'\n" +
                       "User 2: 'I love the new UI, but it's a bit slow to load.'\n" +
                       "User 3: 'Would be great to have a dark mode option.'\n" +
                       "User 4: 'The search function doesn't work well for partial matches.'\n" +
                       "User 5: 'App crashes on startup sometimes.'\n",
            agent=researcher,
            expected_output="A detailed analysis of user feedback with key insights and priorities."
        )
        
        feature_task = Task(
            description="Based on the feedback analysis, generate 3-5 feature proposals that address the most important user needs.",
            agent=feature_planner,
            expected_output="A list of 3-5 feature proposals with descriptions and justifications.",
            dependencies=["analyze_feedback"]
        )
        
        print("Tasks created successfully")
        
        # Create a crew
        crew = Crew(mode="sequential")
        crew.add_agent("researcher", researcher)
        crew.add_agent("feature_planner", feature_planner)
        crew.add_task("analyze_feedback", feedback_task)
        crew.add_task("feature_proposals", feature_task)
        
        print("Crew created successfully")
        
        # Run the crew
        print("Running the crew...")
        start_time = time.time()
        result = crew.run()
        end_time = time.time()
        
        print(f"\nWorkflow completed in {end_time - start_time:.2f} seconds")
        
        # Print results
        print("\nFeedback Analysis:")
        print(result["analyze_feedback"])
        
        print("\nFeature Proposals:")
        print(result["feature_proposals"])
        
        print("\nTest completed successfully")
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
