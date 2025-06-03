"""
Streamlit app for Project Evolution Agents using direct Anthropic integration.
"""

import os
import time
import json
import re
import pandas as pd
import io
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from feedback_visualizations import render_feedback_analysis_visualization
from feature_visualizations import render_feature_details_table
from feature_extraction import extract_features_with_llm, render_feature_matrix
from technical_extraction import extract_technical_evaluation_with_llm, render_technical_evaluation
from sprint_extraction import extract_sprint_plan_with_llm, render_sprint_plan
from stakeholder_extraction import extract_stakeholder_update_with_llm, render_stakeholder_update
from technical_visualizations import render_technical_evaluation_visualization
from sprint_visualizations import render_sprint_plan_visualization
from stakeholder_visualizations import render_stakeholder_update_visualization
from direct_agents.agent import Agent
from direct_agents.task import Task
from direct_agents.crew import Crew

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Project Evolution Agents",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    p, li, div {
        line-height: 1.8;
        font-size: 1.05rem;
        color: #333;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #4527A0;
        margin-bottom: 1.5rem;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    
    .subheader {
        font-size: 1.8rem;
        font-weight: 700;
        color: #5E35B1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        line-height: 1.3;
        border-bottom: 2px solid #E0E0E0;
        padding-bottom: 0.5rem;
    }
    
    .task-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #673AB7;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #7E57C2;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Text Elements */
    .info-text {
        font-size: 1.1rem;
        color: #424242;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .highlight-text {
        background-color: #F3E5F5;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* UI Elements */
    .stButton>button {
        background-color: #673AB7;
        color: white;
        border-radius: 5px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #5E35B1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    
    /* Status Indicators */
    .status-running {
        color: #2196F3;
        font-weight: 600;
        padding: 0.3rem 0;
        display: block;
    }
    
    .status-completed {
        color: #4CAF50;
        font-weight: 600;
        padding: 0.3rem 0;
        display: block;
    }
    
    .status-error {
        color: #F44336;
        font-weight: 600;
        padding: 0.3rem 0;
        display: block;
    }
    
    .status-pending {
        color: #757575;
        font-weight: 500;
        padding: 0.3rem 0;
        display: block;
    }
    
    /* Content Containers */
    .content-box {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #E0E0E0;
    }
    
    .result-container {
        background-color: #F5F5F5;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.5rem;
        border-left: 4px solid #673AB7;
    }
    
    /* Dividers */
    .divider {
        height: 1px;
        background-color: #E0E0E0;
        margin: 1.5rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F5F5F5;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #E8EAF6;
        border-bottom: 2px solid #673AB7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "result" not in st.session_state:
    st.session_state.result = None
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = None
if "mode" not in st.session_state:
    st.session_state.mode = "sequential"
if "rerun_trigger" not in st.session_state:
    st.session_state.rerun_trigger = False
# Progress tracking variables removed as we now use a simplified progress UI with spinner

# Simplified user feedback variables
if "feedback_status" not in st.session_state:
    st.session_state.feedback_status = "not_started"  # Possible values: not_started, completed
if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = {
        "notes": "",
        "priority_focus": None,
        "selected_categories": []
    }
# For backward compatibility with existing visualization components and workflow logic
# This variable is maintained alongside the newer feedback_status for now
# Future refactoring should consolidate these into a single approach
if "feedback_analysis_completed" not in st.session_state:
    st.session_state.feedback_analysis_completed = False

# Sample feedback data
SAMPLE_FEEDBACK = """
User 1: The app crashes when I try to upload large files.
User 2: I love the new UI, but it's a bit slow to load.
User 3: Would be great to have a dark mode option.
User 4: The search function doesn't work well for partial matches.
User 5: App crashes on startup sometimes.
User 6: I wish there was a way to save my favorite searches.
User 7: The notification system is too intrusive.
User 8: Love the new features, but the battery drain is significant.
User 9: Can't find the settings menu easily.
User 10: The app is much better than competitors, just needs better performance.
"""

def update_progress(task_id, status, index, total):
    """
    Simplified progress callback function.
    Now only used for logging purposes as we've simplified the UI progress tracking.
    
    Args:
        task_id: ID of the current task
        status: Status of the task ('running', 'completed', 'error')
        index: Index of the current task
        total: Total number of tasks
    """
    # We no longer update session state variables for detailed progress tracking
    # This function is kept for compatibility with the Crew class
    pass

def create_agents_and_tasks(feedback_data):
    """
    Create agents and tasks for the project evolution workflow.
    
    Args:
        feedback_data: User feedback data
        
    Returns:
        A tuple of (crew, agents, tasks)
    """
    # Create agents
    feedback_analyst = Agent(
        role="Feedback Analyst",
        goal="Analyze user feedback to identify patterns, priorities, and insights",
        backstory="You are an expert in data analysis with a focus on user feedback. You excel at identifying patterns and extracting actionable insights from user comments.",
        verbose=True
    )
    
    feature_planner = Agent(
        role="Feature Planner",
        goal="Generate feature proposals based on user feedback analysis",
        backstory="You are a product manager who specializes in translating user feedback into actionable feature proposals. You have a keen sense for prioritizing features that will have the greatest impact.",
        verbose=True
    )
    
    technical_evaluator = Agent(
        role="Technical Evaluator",
        goal="Evaluate the technical feasibility of proposed features",
        backstory="You are a senior software engineer with extensive experience in evaluating the technical complexity and feasibility of new features. You can identify potential challenges and estimate implementation effort.",
        verbose=True
    )
    
    sprint_planner = Agent(
        role="Sprint Planner",
        goal="Create a sprint plan based on feature proposals and technical evaluation",
        backstory="You are a project manager with expertise in agile methodologies. You excel at organizing features into sprints and creating realistic timelines for implementation.",
        verbose=True
    )
    
    stakeholder_communicator = Agent(
        role="Stakeholder Communicator",
        goal="Generate clear and compelling updates for stakeholders",
        backstory="You are a communication specialist who excels at translating technical information into clear, compelling updates for stakeholders. You know how to highlight the value and impact of planned work.",
        verbose=True
    )
    
    # Create tasks
    # Check if the input is enhanced feedback analysis (contains user collaboration)
    is_enhanced_feedback = "USER COLLABORATION NOTES:" in feedback_data if isinstance(feedback_data, str) else False
    
    if is_enhanced_feedback:
        analyze_feedback_task = Task(
            description=f"Analyze the following user feedback which includes user collaboration notes. Pay special attention to the user's priorities and insights:\n\n{feedback_data}",
            agent=feedback_analyst,
            expected_output="A detailed analysis of user feedback with key patterns, priorities, and actionable insights that incorporates the user's collaboration notes."
        )
    else:
        analyze_feedback_task = Task(
            description=f"Analyze the following user feedback and identify key patterns, priorities, and insights:\n\n{feedback_data}",
            agent=feedback_analyst,
            expected_output="A detailed analysis of user feedback with key patterns, priorities, and actionable insights."
        )
    
    # Check if there are priority adjustments in the feedback data
    priority_focus = None
    if isinstance(feedback_data, str) and "PRIORITY ADJUSTMENT:" in feedback_data:
        priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", feedback_data)
        if priority_match:
            priority_focus = priority_match.group(1).strip()
    
    # Create feature generation task with priority consideration
    if priority_focus:
        generate_features_task = Task(
            description=f"Based on the feedback analysis, generate 3-5 feature proposals that address the most important user needs. IMPORTANT: The user has requested to {priority_focus}, so prioritize features that align with this focus.",
            agent=feature_planner,
            expected_output="A list of 3-5 feature proposals with descriptions, justifications, and expected impact that align with the user's priority focus.",
            dependencies=["analyze_feedback"]
        )
    else:
        generate_features_task = Task(
            description="Based on the feedback analysis, generate 3-5 feature proposals that address the most important user needs.",
            agent=feature_planner,
            expected_output="A list of 3-5 feature proposals with descriptions, justifications, and expected impact.",
            dependencies=["analyze_feedback"]
        )
    
    # Create technical evaluation task with priority consideration
    if priority_focus:
        evaluate_feasibility_task = Task(
            description=f"Evaluate the technical feasibility of the proposed features. For each feature, assess complexity, potential challenges, and estimated effort. IMPORTANT: The user has requested to {priority_focus}, so pay special attention to the technical aspects that would support this priority.",
            agent=technical_evaluator,
            expected_output="A technical evaluation of each proposed feature, including complexity rating, potential challenges, and estimated effort, with special consideration for the user's priority focus.",
            dependencies=["generate_features"]
        )
    else:
        evaluate_feasibility_task = Task(
            description="Evaluate the technical feasibility of the proposed features. For each feature, assess complexity, potential challenges, and estimated effort.",
            agent=technical_evaluator,
            expected_output="A technical evaluation of each proposed feature, including complexity rating, potential challenges, and estimated effort.",
            dependencies=["generate_features"]
        )
    
    # Create sprint planning task with priority consideration
    if priority_focus:
        create_sprint_plan_task = Task(
            description=f"Create a sprint plan based on the feature proposals and technical evaluation. Organize features into sprints and create a timeline for implementation. IMPORTANT: The user has requested to {priority_focus}, so prioritize scheduling features that align with this focus in earlier sprints.",
            agent=sprint_planner,
            expected_output="A sprint plan with features organized into sprints, estimated timelines, and resource allocation that reflects the user's priority focus.",
            dependencies=["evaluate_feasibility"]
        )
    else:
        create_sprint_plan_task = Task(
            description="Create a sprint plan based on the feature proposals and technical evaluation. Organize features into sprints and create a timeline for implementation.",
            agent=sprint_planner,
            expected_output="A sprint plan with features organized into sprints, estimated timelines, and resource allocation.",
            dependencies=["evaluate_feasibility"]
        )
    
    # Create stakeholder update task with priority consideration
    if priority_focus:
        generate_update_task = Task(
            description=f"Generate a clear and compelling update for stakeholders based on the feedback analysis, feature proposals, technical evaluation, and sprint plan. IMPORTANT: The user has requested to {priority_focus}, so highlight how the planned work addresses this priority.",
            agent=stakeholder_communicator,
            expected_output="A stakeholder update that clearly communicates the planned work, its value, and expected impact, with emphasis on how it addresses the user's priority focus.",
            dependencies=["create_sprint_plan"]
        )
    else:
        generate_update_task = Task(
            description="Generate a clear and compelling update for stakeholders based on the feedback analysis, feature proposals, technical evaluation, and sprint plan.",
            agent=stakeholder_communicator,
            expected_output="A stakeholder update that clearly communicates the planned work, its value, and expected impact.",
            dependencies=["create_sprint_plan"]
        )
    
    # Create crew with progress callback
    crew = Crew(mode=st.session_state.mode, progress_callback=update_progress)
    
    # Add agents to crew
    crew.add_agent("feedback_analyst", feedback_analyst)
    crew.add_agent("feature_planner", feature_planner)
    crew.add_agent("technical_evaluator", technical_evaluator)
    crew.add_agent("sprint_planner", sprint_planner)
    crew.add_agent("stakeholder_communicator", stakeholder_communicator)
    
    # Add tasks to crew
    crew.add_task("analyze_feedback", analyze_feedback_task)
    crew.add_task("generate_features", generate_features_task)
    crew.add_task("evaluate_feasibility", evaluate_feasibility_task)
    crew.add_task("create_sprint_plan", create_sprint_plan_task)
    crew.add_task("generate_update", generate_update_task)
    
    return crew

def run_feedback_analysis_only():
    """Run only the feedback analysis part of the workflow"""
    try:
        
        # Create feedback analyst agent
        feedback_analyst = Agent(
            role="Feedback Analyst",
            goal="Analyze user feedback to identify patterns, priorities, and insights",
            backstory="You are an expert in data analysis with a focus on user feedback. You excel at identifying patterns and extracting actionable insights from user comments.",
            verbose=True
        )
        
        # Create feedback analysis task
        analyze_feedback_task = Task(
            description=f"Analyze the following user feedback and identify key patterns, priorities, and insights:\n\n{st.session_state.feedback_data}",
            agent=feedback_analyst,
            expected_output="A detailed analysis of user feedback with key patterns, priorities, and insights."
        )
        
        # Create crew
        crew = Crew(mode=st.session_state.mode)
        
        # Add agent to crew
        crew.add_agent("feedback_analyst", feedback_analyst)
        
        # Add task to crew
        crew.add_task("analyze_feedback", analyze_feedback_task)
        
        # Run the feedback analysis
        start_time = time.time()
        result = crew.run()
        end_time = time.time()
        
        # Add execution time to result
        result["execution_time"] = f"{end_time - start_time:.2f} seconds"
        result["execution_log"] = crew.get_execution_log()
        
        # Store the result in session state
        st.session_state.feedback_analysis_result = result
        
        return result
    except Exception as e:
        st.error(f"Error running feedback analysis: {str(e)}")
        return None


def run_remaining_workflow():
    """Run the remaining parts of the workflow after feedback analysis"""
    try:
        
        # Get the enhanced feedback analysis with user input (for backward compatibility)
        feedback_input = st.session_state.enhanced_feedback_analysis
        
        # Create agents
        feature_planner = Agent(
            role="Feature Planner",
            goal="Generate feature proposals based on user feedback analysis",
            backstory="You are a product manager who specializes in translating user feedback into actionable feature proposals. You have a keen sense for prioritizing features that will have the greatest impact.",
            verbose=True
        )
        
        tech_evaluator = Agent(
            role="Technical Evaluator",
            goal="Evaluate the technical feasibility of proposed features",
            backstory="You are a senior software architect with extensive experience in evaluating the technical feasibility of product features. You can quickly assess complexity, potential challenges, and implementation approaches.",
            verbose=True
        )
        
        sprint_planner = Agent(
            role="Sprint Planner",
            goal="Create a sprint plan based on feature proposals and technical evaluation",
            backstory="You are an experienced agile project manager who excels at breaking down features into manageable sprint tasks. You know how to balance technical constraints with business priorities.",
            verbose=True
        )
        
        stakeholder_communicator = Agent(
            role="Stakeholder Communicator",
            goal="Generate clear and compelling updates for stakeholders",
            backstory="You are a communication specialist who excels at translating technical information into clear, compelling updates for stakeholders. You know how to highlight the value and impact of planned work.",
            verbose=True
        )
        
        # Get priority focus from the centralized user feedback structure
        priority_focus = st.session_state.user_feedback.get("priority_focus")
        
        # Get the feedback analysis from the previous run
        feedback_analysis = st.session_state.feedback_analysis_result.get("analyze_feedback", "")
        
        # Create feature generation task with priority consideration
        if priority_focus:
            generate_features_task = Task(
                description=f"Based on the following feedback analysis, generate feature proposals that specifically address the user's priority to {priority_focus}:\n\n{feedback_analysis}",
                agent=feature_planner,
                expected_output="A list of feature proposals with descriptions, priorities, and complexity estimates."
            )
        else:
            generate_features_task = Task(
                description=f"Based on the following feedback analysis, generate feature proposals:\n\n{feedback_analysis}",
                agent=feature_planner,
                expected_output="A list of feature proposals with descriptions, priorities, and complexity estimates."
            )
        
        # Create technical evaluation task
        evaluate_feasibility_task = Task(
            description="Evaluate the technical feasibility of the proposed features. Consider implementation complexity, potential challenges, and required resources.",
            agent=tech_evaluator,
            expected_output="A technical evaluation of each proposed feature with complexity ratings and implementation considerations.",
            dependencies=["generate_features"]
        )
        
        # Create sprint planning task
        create_sprint_plan_task = Task(
            description="Create a sprint plan based on the feature proposals and technical evaluation. Break down features into tasks and allocate them across sprints.",
            agent=sprint_planner,
            expected_output="A sprint plan with features allocated to sprints, task breakdowns, and estimated timelines.",
            dependencies=["generate_features", "evaluate_feasibility"]
        )
        
        # Create stakeholder update task
        generate_update_task = Task(
            description="Generate a stakeholder update based on the feature proposals, technical evaluation, and sprint plan. Highlight the value and impact of the planned work.",
            agent=stakeholder_communicator,
            expected_output="A stakeholder update that clearly communicates the planned work, its value, and expected timeline.",
            dependencies=["generate_features", "evaluate_feasibility", "create_sprint_plan"]
        )
        
        # Create crew
        crew = Crew(mode=st.session_state.mode)
        
        # Add agents to crew
        crew.add_agent("feature_planner", feature_planner)
        crew.add_agent("technical_evaluator", tech_evaluator)
        crew.add_agent("sprint_planner", sprint_planner)
        crew.add_agent("stakeholder_communicator", stakeholder_communicator)
        
        # Add tasks to crew
        crew.add_task("generate_features", generate_features_task)
        crew.add_task("evaluate_feasibility", evaluate_feasibility_task)
        crew.add_task("create_sprint_plan", create_sprint_plan_task)
        crew.add_task("generate_update", generate_update_task)
        
        # Run the crew
        start_time = time.time()
        result = crew.run()
        end_time = time.time()
        
        # Add execution time to result
        result["execution_time"] = f"{end_time - start_time:.2f} seconds"
        result["execution_log"] = crew.get_execution_log()
        
        # Add the feedback analysis to the result
        result["analyze_feedback"] = feedback_analysis
        
        return result
    except Exception as e:
        st.error(f"Error running remaining workflow: {str(e)}")
        return None


def run_workflow():
    """Run the complete project evolution workflow"""
    try:
        # Check if we need to run the feedback analysis only
        if st.session_state.feedback_status == "not_started":
            # Run only the feedback analysis
            result = run_feedback_analysis_only()
            
            if result:
                # Store the feedback analysis result but don't mark as completed yet
                # This allows the user to provide feedback before continuing
                st.session_state.feedback_analysis_result = result
                # Sync with old variable for backward compatibility
                st.session_state.feedback_analysis_completed = False
                return result
            else:
                return None
        else:
            # Sync with old variable for backward compatibility with visualization components
            # This maintains the dual-state tracking (feedback_status and feedback_analysis_completed)
            # which should be consolidated in future refactoring
            st.session_state.feedback_analysis_completed = True
            # Return the feedback analysis result while waiting for user confirmation
            # The Continue Analysis button in the feedback tab will handle running the remaining workflow
            return st.session_state.feedback_analysis_result
    except Exception as e:
        st.error(f"Error running workflow: {str(e)}")
        return None

# Streamlit UI
st.markdown('<div class="main-header">🤖 Project Evolution Agents</div>', unsafe_allow_html=True)
st.markdown('''
<div class="content-box">
    <div class="info-text">This app uses AI agents to analyze user feedback and generate feature proposals, technical evaluations, sprint plans, and stakeholder updates.</div>
    <div class="info-text">The agents work together to process feedback data, identify patterns, and create actionable plans for your project evolution.</div>
</div>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="subheader">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    # API configuration
    st.markdown('<div class="task-header">🔑 API Configuration</div>', unsafe_allow_html=True)
    api_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    # Mode is now fixed to sequential
    st.session_state.mode = "sequential"
    
    # Feedback data
    st.markdown('<div class="task-header">📝 Feedback Data</div>', unsafe_allow_html=True)
    feedback_option = st.radio("Select feedback source:", ["Sample Data", "Custom Input", "Upload CSV"])
    
    if feedback_option == "Sample Data":
        st.session_state.feedback_data = SAMPLE_FEEDBACK
        st.text_area("Sample Feedback", SAMPLE_FEEDBACK, height=200, disabled=True)
    elif feedback_option == "Custom Input":
        custom_feedback = st.text_area("Enter custom feedback:", height=200)
        if custom_feedback:
            st.session_state.feedback_data = custom_feedback
    else:  # Upload CSV
        uploaded_file = st.file_uploader("Upload CSV file with feedback data", type="csv")
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display the dataframe
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                # Check if the dataframe has expected columns
                if 'feedback' in df.columns:
                    # Extract feedback from the 'feedback' column
                    feedback_list = df['feedback'].tolist()
                    # Format as numbered list
                    formatted_feedback = "\n".join([f"User {i+1}: {feedback}" for i, feedback in enumerate(feedback_list)])
                    st.session_state.feedback_data = formatted_feedback
                    
                    # Show the formatted feedback
                    st.text_area("Formatted Feedback", formatted_feedback, height=200, disabled=True)
                else:
                    # If no 'feedback' column, try to use all columns
                    all_feedback = []
                    for i, row in df.iterrows():
                        # Combine all columns in the row
                        row_feedback = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        all_feedback.append(f"User {i+1}: {row_feedback}")
                    
                    formatted_feedback = "\n".join(all_feedback)
                    st.session_state.feedback_data = formatted_feedback
                    
                    # Show the formatted feedback
                    st.text_area("Formatted Feedback", formatted_feedback, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error processing CSV file: {str(e)}")
                st.session_state.feedback_data = None
    
    # Start/Stop buttons - different behavior based on the current state
    col1, col2 = st.columns(2)
    
    # Initialize button_clicked variable to avoid NameError
    button_clicked = False
    
    with col1:
        if not st.session_state.feedback_analysis_completed:
            # Initial run button - only runs feedback analysis
            start_button = st.button("▶️ Run Analysis", disabled=st.session_state.running)
            button_clicked = start_button
        else:
            # Show that feedback analysis is complete
            st.success("Analysis Complete! Please review and provide input in the Feedback Analysis tab.")
            start_button = False
    
    with col2:
        # Initialize stop_button variable to avoid NameError
        stop_button = False
        
        if st.session_state.running:
            stop_button = st.button("⏹️ Stop", disabled=False)
        else:
            # Show reset button when feedback analysis is completed
            if hasattr(st.session_state, "feedback_analysis_result") and st.session_state.feedback_analysis_result:
                reset_button = st.button("↻ Reset Workflow")
                if reset_button:
                    # Reset all feedback-related state variables
                    if hasattr(st.session_state, "feedback_analysis_result"):
                        st.session_state.feedback_analysis_result = None
                    st.session_state.feedback_status = "not_started"
                    st.session_state.user_feedback = {
                        "notes": "",
                        "priority_focus": None,
                        "selected_categories": []
                    }
                    # Reset backward compatibility variables
                    # These variables are maintained for compatibility with existing components
                    # that expect these specific variables and formats
                    st.session_state.feedback_analysis_completed = False
                    if hasattr(st.session_state, "enhanced_feedback_analysis"):
                        st.session_state.enhanced_feedback_analysis = ""
                    st.experimental_rerun()
            else:
                stop_button = st.button("⏹️ Stop", disabled=True)
    
    if button_clicked:
        if not st.session_state.feedback_data:
            st.error("Please provide feedback data")
        else:
            st.session_state.running = True
            with st.spinner("Running analysis..."):
                st.session_state.result = run_workflow()
                st.session_state.running = False
    
    if stop_button:
        st.session_state.running = False
        st.success("Analysis stopped")

# Main content area
if st.session_state.running:
    st.markdown('''
<div class="content-box" style="background-color: #E3F2FD; border-color: #2196F3;">
    <div class="task-header" style="color: #2196F3;">🔄 Analysis in progress...</div>
    <div class="info-text">The AI agents are analyzing your feedback data. This process may take a few minutes.</div>
</div>
''', unsafe_allow_html=True)
    
    # Display a simple spinner instead of detailed progress
    st.spinner("Running analysis...")

else:
    if st.session_state.result:
        st.markdown('''
<div class="content-box" style="background-color: #E8F5E9; border-color: #4CAF50;">
    <div class="task-header" style="color: #4CAF50;">✅ Workflow completed successfully!</div>
    <div class="info-text">All agents have completed their tasks. You can view the results below.</div>
</div>
''', unsafe_allow_html=True)
        
        # Display execution time
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<div class="subheader">⏱️ Execution Time</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-text">Total execution time: <span class="highlight-text">{st.session_state.result.get("execution_time", "Unknown")}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create tabs for each output
        tabs = st.tabs([
            "🔍 Feedback Analysis", 
            "💡 Feature Proposals", 
            "⚙️ Technical Evaluation", 
            "📅 Sprint Plan", 
            "📢 Stakeholder Update",
            "📋 Execution Log"
        ])
        
        # Feedback Analysis tab
        with tabs[0]:
            st.markdown('<div class="subheader">🔍 Feedback Analysis</div>', unsafe_allow_html=True)
            
            # Get feedback analysis text
            feedback_analysis = st.session_state.result.get("analyze_feedback", "")
            
            if feedback_analysis:
                # Add visualizations at the top
                st.markdown('<div class="section-title">📊 Feedback Analysis Visualizations</div>', unsafe_allow_html=True)
                
                # Render the feedback analysis visualizations with raw feedback data
                render_feedback_analysis_visualization(feedback_analysis, st.session_state.feedback_data)
                
                # Text section removed to reduce token usage
                # st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">👥 Feedback & Priorities</div>', unsafe_allow_html=True)
                
                # Check if feedback has already been provided
                if st.session_state.feedback_status == "not_started":
                    # Create a clean, streamlined interface for user feedback
                    with st.expander("Provide your feedback and priorities", expanded=True):
                        # Extract categories from the feedback analysis
                        categories = []
                        category_pattern = r'(?:Category|Theme|Topic|Area|Issue)\s*(?:\d+)?\s*[:\-]\s*([^\n]+)'
                        category_matches = re.findall(category_pattern, feedback_analysis, re.IGNORECASE)
                        categories = [cat.strip() for cat in category_matches[:6]]
                        
                        # If no categories found, provide sample ones
                        if not categories:
                            categories = ["UI/UX Issues", "Performance Problems", "Feature Requests", "Usability Concerns", "Documentation Needs"]
                        
                        # Use a multiselect for categories instead of multiple checkboxes
                        selected_categories = st.multiselect(
                            "Select important categories to focus on:",
                            options=categories,
                            default=categories[:3]
                        )
                        
                        # User notes in a single text area
                        user_notes = st.text_area(
                            "Your notes and insights:",
                            height=100,
                            placeholder="Add your insights or additional context about the feedback..."
                        )
                        
                        # Single action button for submitting feedback and continuing
                        if st.button("Submit Feedback & Continue Analysis", type="primary"):
                            # Save all user feedback in a structured format
                            # Derive priority focus from selected categories if any are selected
                            priority_focus = None
                            if selected_categories:
                                priority_focus = f"Prioritize {', '.join(selected_categories)}"
                                
                            st.session_state.user_feedback = {
                                "notes": user_notes,
                                "priority_focus": priority_focus,
                                "selected_categories": selected_categories
                            }
                            
                            # Mark feedback as completed
                            st.session_state.feedback_status = "completed"
                            # Set feedback_analysis_completed for backward compatibility with existing visualization components
                            # This variable is used by other parts of the application and should be maintained for now
                            st.session_state.feedback_analysis_completed = True
                            
                            # Set running state and run the remaining workflow
                            st.session_state.running = True
                            
                            with st.spinner("Running analysis with your feedback..."):
                                # Create enhanced feedback analysis string format
                                # This maintains backward compatibility with visualization components and other parts of the app
                                # that expect this specific string format for parsing
                                priority_text = ""
                                if priority_focus:
                                    priority_text = f"\n\nPRIORITY ADJUSTMENT: {priority_focus}"
                                
                                # Only include user notes if they're not empty
                                notes_section = ""
                                if user_notes.strip():
                                    notes_section = f"\n\nUSER COLLABORATION NOTES:\n{user_notes}"
                                
                                st.session_state.enhanced_feedback_analysis = f"""
{feedback_analysis}{notes_section}{priority_text}

SELECTED CATEGORIES:
{', '.join(selected_categories) if selected_categories else 'None'}
"""
                                
                                # Run the remaining workflow
                                st.session_state.result = run_remaining_workflow()
                                
                                # Add the feedback analysis to the result
                                if "analyze_feedback" not in st.session_state.result and "analyze_feedback" in st.session_state.feedback_analysis_result:
                                    st.session_state.result["analyze_feedback"] = st.session_state.feedback_analysis_result["analyze_feedback"]
                                
                                # Mark workflow as completed
                                st.session_state.workflow_completed = True
                            
                            # Reset running state
                            st.session_state.running = False
                            # Use a version-compatible way to rerun the app
                            st.session_state.rerun_trigger = not st.session_state.get('rerun_trigger', False)
                    
                    # Option to skip feedback entirely
                    if st.button("Skip Feedback & Continue with AI Analysis"):
                        # Set default values
                        st.session_state.user_feedback = {
                            "notes": "",
                            "priority_focus": None,
                            "selected_categories": []
                        }
                        # Just use the original feedback analysis without any user input
                        st.session_state.enhanced_feedback_analysis = feedback_analysis
                        st.session_state.feedback_status = "completed"
                        # Set feedback_analysis_completed for backward compatibility with existing visualization components
                        # This variable is used by other parts of the application and should be maintained for now
                        st.session_state.feedback_analysis_completed = True
                        
                        # Set running state
                        st.session_state.running = True
                        
                        with st.spinner("Running analysis..."):
                            # Run the remaining workflow
                            st.session_state.result = run_remaining_workflow()
                            
                            # Add the feedback analysis to the result
                            if "analyze_feedback" not in st.session_state.result and "analyze_feedback" in st.session_state.feedback_analysis_result:
                                st.session_state.result["analyze_feedback"] = st.session_state.feedback_analysis_result["analyze_feedback"]
                        
                        # Reset running state and refresh the page
                        st.session_state.running = False
                        # Use a version-compatible way to rerun the app
                        st.session_state.rerun_trigger = not st.session_state.get('rerun_trigger', False)
                
                else:  # Feedback has been provided
                    # Display a summary of the user's feedback
                    priority_focus = st.session_state.user_feedback.get("priority_focus")
                    
                    if priority_focus:
                        # Create a visual indicator for the priority focus
                        # Determine color based on the first category mentioned
                        priority_color = "#9575CD"  # Default purple
                        
                        # Check for specific keywords in the priority focus
                        if "Performance" in priority_focus or "Speed" in priority_focus:
                            priority_color = "#FF7043"  # Orange
                        elif "User Experience" in priority_focus or "UI" in priority_focus or "UX" in priority_focus or "Usability" in priority_focus:
                            priority_color = "#42A5F5"  # Blue
                        elif "New Features" in priority_focus or "Feature" in priority_focus:
                            priority_color = "#66BB6A"  # Green
                        elif "Security" in priority_focus or "Privacy" in priority_focus:
                            priority_color = "#FFC107"  # Yellow
                        elif "Cost" in priority_focus or "Budget" in priority_focus:
                            priority_color = "#E91E63"  # Pink
                        
                        priority_html = f'''
                        <div style="padding: 10px; background-color: {priority_color}; color: white; border-radius: 5px; margin: 10px 0; text-align: center;">
                            <h3 style="margin: 0;">Priority Focus: {priority_focus}</h3>
                        </div>
                        '''
                        components.html(priority_html, height=60)
                    
                    # Show selected categories if any
                    selected_categories = st.session_state.user_feedback.get("selected_categories", [])
                    if selected_categories:
                        st.write("**Selected categories:**", ", ".join(selected_categories))
                    
                    # Show user notes if any
                    user_notes = st.session_state.user_feedback.get("notes", "")
                    if user_notes:
                        with st.expander("Your feedback notes"):
                            st.write(user_notes)
                    
                    else:
                        # User has already confirmed next steps and analysis is running or completed
                        if st.session_state.get("workflow_completed", False):
                            # Workflow is completed
                            st.success("Analysis complete! All tabs have been populated with results.")
                            st.markdown('''
                            <div style="padding: 15px; background-color: #E8F5E9; border-radius: 5px; margin: 10px 0;">  
                                <h4 style="margin-top: 0;">Analysis Complete!</h4>
                                <p>All analysis steps have been completed. You can now explore the results in the tabs above.</p>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            # Analysis is still running
                            st.info("Analysis is in progress... Please wait while the AI processes the remaining steps.")
                            st.markdown('''
                            <div style="padding: 15px; background-color: #E3F2FD; border-radius: 5px; margin: 10px 0;">  
                                <h4 style="margin-top: 0;">Analysis Steps:</h4>
                                <ol>
                                    <li><strong>Feature Proposals</strong> - Generate feature ideas based on the feedback analysis</li>
                                    <li><strong>Technical Evaluation</strong> - Assess the feasibility and complexity of proposed features</li>
                                    <li><strong>Sprint Planning</strong> - Create a sprint plan for implementing the features</li>
                                    <li><strong>Stakeholder Update</strong> - Generate a summary for stakeholders</li>
                                </ol>
                            </div>
                            ''', unsafe_allow_html=True)
                        # Remove this redundant else block as it's already handled above
                    
                    # Option to view the enhanced analysis
                    with st.expander("View Enhanced Analysis", expanded=False):
                        st.markdown(st.session_state.enhanced_feedback_analysis)
                    
                    # Option to restart feedback
                    if st.button("Restart Feedback"):
                        st.session_state.feedback_status = "not_started"
                        st.session_state.user_feedback = {
                            "notes": "",
                            "priority_focus": None,
                            "selected_categories": []
                        }
                        st.experimental_rerun()
            else:
                st.markdown('<div class="result-container">No feedback analysis available</div>', unsafe_allow_html=True)
        
        # Feature Proposals tab
        with tabs[1]:
            st.markdown('<div class="subheader">💡 Feature Proposals</div>', unsafe_allow_html=True)
            
            # Get feature proposals text
            feature_proposals = st.session_state.result.get("generate_features", "")
            
            if feature_proposals:
                # Add visualizations at the top
                st.markdown('<div class="section-title">📊 Feature Visualizations</div>', unsafe_allow_html=True)
                
                # Use LLM to extract features from the feature proposals text
                try:
                    # Extract features using the LLM
                    feature_data = extract_features_with_llm(feature_proposals)
                    
                    # Extract the features list and user priority focus from the returned data
                    features_list = feature_data.get('features', [])
                    user_priority_focus = feature_data.get('user_priority_focus')
                    
                    # Render the priority/complexity matrix
                    render_feature_matrix(features_list)
                    
                    # Create a table of features with color coding
                    st.markdown('<div class="section-title">📝 Feature Details</div>', unsafe_allow_html=True)
                    
                    # Use our component to render the feature details table
                    render_feature_details_table(features_list)
                except Exception as e:
                    st.error(f"Error extracting features: {str(e)}")
                    st.info("Displaying raw feature proposals instead.")
                
                # Text section removed to reduce token usage
                # st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                # st.markdown('<div class="section-title">📖 Detailed Feature Proposals</div>', unsafe_allow_html=True)
                # st.markdown('<div class="result-container">', unsafe_allow_html=True)
                # st.markdown(feature_proposals)
                # st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No feature proposals available</div>', unsafe_allow_html=True)
        
        # Technical Evaluation tab
        with tabs[2]:
            st.markdown('<div class="subheader">🔧 Technical Evaluation</div>', unsafe_allow_html=True)
            
            # Get technical evaluation text
            technical_eval = st.session_state.result.get("evaluate_feasibility", "")
            
            if technical_eval:
                # Add visualizations at the top
                st.markdown('<div class="section-title">📊 Technical Visualizations</div>', unsafe_allow_html=True)
                
                # Check if there's a user priority focus
                user_priority_focus = None
                if "PRIORITY ADJUSTMENT:" in st.session_state.enhanced_feedback_analysis:
                    priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", st.session_state.enhanced_feedback_analysis)
                    if priority_match:
                        user_priority_focus = priority_match.group(1).strip()
                
                # Use LLM to extract technical evaluation data
                try:
                    # Extract technical evaluation data using the LLM with priority focus
                    tech_eval_data = extract_technical_evaluation_with_llm(technical_eval, user_priority_focus)
                    
                    # Make sure the tech_eval_data is in the expected format
                    if isinstance(tech_eval_data, dict) and 'features' in tech_eval_data:
                        # Render the technical evaluation visualizations
                        render_technical_evaluation(tech_eval_data)
                    else:
                        # If the data is not in the expected format, create the expected structure
                        formatted_data = {
                            'features': tech_eval_data if isinstance(tech_eval_data, list) else [],
                            'user_priority_focus': user_priority_focus
                        }
                        render_technical_evaluation(formatted_data)
                except Exception as e:
                    st.error(f"Error extracting technical evaluation data: {str(e)}")
                    st.info("Displaying raw technical evaluation instead.")
                    # Fallback to original visualization
                    render_technical_evaluation_visualization(technical_eval)
                
                # Text section removed to reduce token usage
                # st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                # st.markdown('<div class="section-title">📖 Detailed Technical Evaluation</div>', unsafe_allow_html=True)
                # st.markdown('<div class="result-container">', unsafe_allow_html=True)
                # st.markdown(technical_eval)
                # st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No technical evaluation available</div>', unsafe_allow_html=True)
        
        # Sprint Plan tab
        with tabs[3]:
            st.markdown('<div class="subheader">📅 Sprint Plan</div>', unsafe_allow_html=True)
            
            # Get sprint plan text
            sprint_plan = st.session_state.result.get("create_sprint_plan", "")
            
            if sprint_plan:
                # Add visualizations at the top
                st.markdown('<div class="section-title">📊 Sprint Visualizations</div>', unsafe_allow_html=True)
                
                # Check if there's a user priority focus
                user_priority_focus = None
                if "PRIORITY ADJUSTMENT:" in st.session_state.enhanced_feedback_analysis:
                    priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", st.session_state.enhanced_feedback_analysis)
                    if priority_match:
                        user_priority_focus = priority_match.group(1).strip()
                
                # Use LLM to extract sprint plan data
                try:
                    # Extract sprint plan data using the LLM with priority focus
                    sprint_plan_data = extract_sprint_plan_with_llm(sprint_plan, user_priority_focus)
                    
                    # Make sure the sprint_plan_data is in the expected format
                    if isinstance(sprint_plan_data, dict) and 'sprints' in sprint_plan_data:
                        # Render the sprint plan visualizations
                        render_sprint_plan(sprint_plan_data)
                    else:
                        # If the data is not in the expected format, create the expected structure
                        formatted_data = {
                            'sprints': sprint_plan_data if isinstance(sprint_plan_data, list) else [],
                            'user_priority_focus': user_priority_focus
                        }
                        render_sprint_plan(formatted_data)
                except Exception as e:
                    st.error(f"Error extracting sprint plan data: {str(e)}")
                    st.info("Displaying raw sprint plan instead.")
                    # Fallback to original visualization
                    render_sprint_plan_visualization(sprint_plan)
                
                # Text section removed to reduce token usage
                # st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                # st.markdown('<div class="section-title">📖 Detailed Sprint Plan</div>', unsafe_allow_html=True)
                # st.markdown('<div class="result-container">', unsafe_allow_html=True)
                # st.markdown(sprint_plan)
                # st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No sprint plan available</div>', unsafe_allow_html=True)
        
        # Stakeholder Update tab
        with tabs[4]:
            st.markdown('<div class="subheader">💼 Stakeholder Update</div>', unsafe_allow_html=True)
            
            # Get stakeholder update text
            stakeholder_update = st.session_state.result.get("generate_update", "")
            
            if stakeholder_update:
                # Add visualizations at the top
                st.markdown('<div class="section-title">📊 Stakeholder Insights</div>', unsafe_allow_html=True)
                
                # Check if there's a user priority focus
                user_priority_focus = None
                if "PRIORITY ADJUSTMENT:" in st.session_state.enhanced_feedback_analysis:
                    priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", st.session_state.enhanced_feedback_analysis)
                    if priority_match:
                        user_priority_focus = priority_match.group(1).strip()
                
                # Use LLM to extract stakeholder update data
                try:
                    # Extract stakeholder update data using the LLM with priority focus
                    update_data = extract_stakeholder_update_with_llm(stakeholder_update, user_priority_focus)
                    
                    # Make sure the update_data is in the expected format
                    if isinstance(update_data, dict):
                        # Add user_priority_focus if it's not already in the data
                        if user_priority_focus and 'user_priority_focus' not in update_data:
                            update_data['user_priority_focus'] = user_priority_focus
                        
                        # Render the stakeholder update visualizations
                        render_stakeholder_update(update_data)
                    else:
                        # If the data is not in the expected format, create the expected structure
                        formatted_data = {
                            'highlights': [],
                            'metrics': [],
                            'risks': [],
                            'next_steps': [],
                            'resources': [],
                            'user_priority_focus': user_priority_focus
                        }
                        render_stakeholder_update(formatted_data)
                except Exception as e:
                    st.error(f"Error extracting stakeholder update data: {str(e)}")
                    st.info("Displaying raw stakeholder update instead.")
                    # Fallback to original visualization
                    render_stakeholder_update_visualization(stakeholder_update)
                
                # Text section removed to reduce token usage
                # st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                # st.markdown('<div class="section-title">📖 Detailed Stakeholder Update</div>', unsafe_allow_html=True)
                # st.markdown('<div class="result-container">', unsafe_allow_html=True)
                # st.markdown(stakeholder_update)
                # st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No stakeholder update available</div>', unsafe_allow_html=True)
        
        # Execution Log tab
        with tabs[5]:
            st.markdown('<div class="subheader">📋 Execution Log</div>', unsafe_allow_html=True)
            log_container = st.container()
            with log_container:
                for log_entry in st.session_state.result.get("execution_log", []):
                    st.text(log_entry)
