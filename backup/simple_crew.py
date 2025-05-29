import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SimpleCrewManager:
    """A simplified version of the project evolution crew manager"""
    
    def __init__(self, mode: str = 'sequential'):
        """Initialize the SimpleCrewManager"""
        self.mode = mode
        self.agents = {}
        self.tasks = {}
        self.outputs = {}
        
        # Initialize components
        self._initialize_agents()
        self._initialize_tasks()
        
        logger.info(f"SimpleCrewManager initialized in {mode} mode")
    
    def _initialize_agents(self):
        """Initialize a simple agent"""
        logger.info("Initializing agent")
        
        # Get API configuration - explicitly use Anthropic
        api_provider = "anthropic"  # Force to use Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Print for debugging
        logger.info(f"Using API provider: {api_provider}")
        logger.info(f"API key exists: {bool(api_key)}")
        
        if not api_key:
            logger.warning(f"No API key found for {api_provider}. Agent will not be able to make API calls.")
        
        # Create a researcher agent
        researcher = Agent(
            role="Researcher",
            goal="Research and provide information on a topic",
            backstory="You are an AI research assistant with expertise in finding and summarizing information.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "provider": "anthropic",  # Force to use Anthropic
                "model": "claude-3-haiku-20240307",  # Explicitly set model
                "temperature": 0.7,
                "api_key": api_key
            }
        )
        
        # Add agent to the collection
        self.agents["researcher"] = researcher
        logger.info("Initialized researcher agent")
    
    def _initialize_tasks(self):
        """Initialize a simple task"""
        logger.info("Initializing task")
        
        # Get the agent
        agent = self.agents.get("researcher")
        
        if not agent:
            logger.error("Researcher agent not found")
            return
        
        # Create research task
        research_task = Task(
            description="Research and summarize information about artificial intelligence advancements in 2024.",
            agent=agent,
            expected_output="A concise summary of AI advancements in 2024.",
            async_execution=self.mode == 'parallel'
        )
        
        # Add task to the collection
        self.tasks["research"] = research_task
        logger.info("Initialized research task")
    
    def run(self) -> Dict[str, Any]:
        """Run the crew in the specified mode"""
        logger.info(f"Starting {self.mode} workflow")
        
        # Create the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[self.tasks["research"]],
            verbose=True,
            process=Process.sequential if self.mode == 'sequential' else Process.hierarchical
        )
        
        # Run the crew
        result = crew.kickoff()
        
        logger.info(f"{self.mode.capitalize()} workflow completed")
        
        return result

# For testing
if __name__ == "__main__":
    crew_manager = SimpleCrewManager(mode='sequential')
    result = crew_manager.run()
    print("Result:", result)
