import streamlit as st
import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_fix import DirectAnthropicExecutor, CompatibleTask

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Fixed CrewAI Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "output" not in st.session_state:
    st.session_state.output = ""
if "mode" not in st.session_state:
    st.session_state.mode = "sequential"

def run_crew():
    """Run the crew with DirectAnthropicExecutor"""
    try:
        # Create agents with Anthropic config
        researcher = Agent(
            role="Researcher",
            goal="Research and analyze user feedback data",
            backstory="You are an AI research analyst with expertise in data analysis and user feedback interpretation.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.7,
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        )
        
        feature_planner = Agent(
            role="Feature Planner",
            goal="Generate feature proposals based on user feedback",
            backstory="You are a product manager who specializes in translating user feedback into actionable feature proposals.",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.7,
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        )
        
        # Create tasks
        feedback_task = CompatibleTask.create(
            description="Analyze user feedback data and identify key patterns and priorities.",
            agent=researcher,
            expected_output="A detailed analysis of user feedback with key insights and priorities."
        )
        
        feature_task = CompatibleTask.create(
            description="Based on the feedback analysis, generate 3-5 feature proposals that address the most important user needs.",
            agent=feature_planner,
            expected_output="A list of 3-5 feature proposals with descriptions and justifications."
        )
        
        # Execute tasks directly with DirectAnthropicExecutor
        st.write("Executing feedback analysis task...")
        start_time = time.time()
        feedback_result = DirectAnthropicExecutor.execute_task(researcher, feedback_task)
        feedback_time = time.time() - start_time
        
        # Pass the feedback result as context to the feature task
        feature_task.context = [f"Feedback Analysis: {feedback_result}"]
        
        st.write("Executing feature proposal task...")
        start_time = time.time()
        feature_result = DirectAnthropicExecutor.execute_task(feature_planner, feature_task)
        feature_time = time.time() - start_time
        
        # Format the result
        result = {
            "feedback_analysis": {
                "agent": "Researcher",
                "execution_time": f"{feedback_time:.2f} seconds",
                "result": feedback_result
            },
            "feature_proposals": {
                "agent": "Feature Planner",
                "execution_time": f"{feature_time:.2f} seconds",
                "result": feature_result
            },
            "total_execution_time": f"{feedback_time + feature_time:.2f} seconds"
        }
        
        return result
    except Exception as e:
        return f"Error running crew: {str(e)}"

# Streamlit UI
st.title("Fixed CrewAI Demo with DirectAnthropicExecutor")
st.write("This app demonstrates a simplified version of the Project Evolution Crew system using DirectAnthropicExecutor.")

# Start button
if st.button("Run Crew", disabled=st.session_state.running):
    st.session_state.running = True
    with st.spinner("Running crew..."):
        result = run_crew()
        st.session_state.output = result
        st.session_state.running = False

# Display results
if st.session_state.output:
    st.subheader("Crew Output")
    
    if isinstance(st.session_state.output, dict):
        st.write(f"**Total Execution Time:** {st.session_state.output['total_execution_time']}")
        
        st.subheader("Feedback Analysis")
        st.write(f"**Agent:** {st.session_state.output['feedback_analysis']['agent']}")
        st.write(f"**Execution Time:** {st.session_state.output['feedback_analysis']['execution_time']}")
        st.markdown(st.session_state.output['feedback_analysis']['result'])
        
        st.subheader("Feature Proposals")
        st.write(f"**Agent:** {st.session_state.output['feature_proposals']['agent']}")
        st.write(f"**Execution Time:** {st.session_state.output['feature_proposals']['execution_time']}")
        st.markdown(st.session_state.output['feature_proposals']['result'])
    else:
        st.error(st.session_state.output)
