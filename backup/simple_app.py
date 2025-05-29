import streamlit as st
import os
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Simple CrewAI Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "output" not in st.session_state:
    st.session_state.output = ""

# Get API key from environment
def get_api_key():
    return os.getenv("ANTHROPIC_API_KEY")

def run_simple_crew():
    """Run a simple crew with one agent and one task"""
    try:
        # Create a simple agent
        api_key = get_api_key()
        
        if not api_key:
            return "Error: No API key found. Please check your .env file."
        
        # Print for debugging
        st.write(f"Using API provider: anthropic")
        st.write(f"API key exists: {bool(api_key)}")
        
        # Create a simple agent - explicitly use Anthropic
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
        
        # Create a simple task
        research_task = Task(
            description="Research and summarize information about artificial intelligence advancements in 2024.",
            agent=researcher,
            expected_output="A concise summary of AI advancements in 2024."
        )
        
        # Create a crew with the agent and task
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )
        
        # Run the crew
        result = crew.kickoff()
        
        return result
    except Exception as e:
        return f"Error running crew: {str(e)}"

# Streamlit UI
st.title("Simple CrewAI Demo")
st.write("This is a minimal Streamlit app with one CrewAI agent and one task.")

# Start button
if st.button("Run Agent", disabled=st.session_state.running):
    st.session_state.running = True
    with st.spinner("Agent is working..."):
        result = run_simple_crew()
        st.session_state.output = result
        st.session_state.running = False

# Display results
if st.session_state.output:
    st.subheader("Agent Output")
    st.write(st.session_state.output)
