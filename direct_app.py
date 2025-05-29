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
import time
import os
import re
from dotenv import load_dotenv
from feature_visualizations import render_feature_details_table, render_feature_details
from technical_visualizations import render_technical_evaluation_visualization
from stakeholder_visualizations import render_stakeholder_update_visualization
from feedback_visualizations import render_feedback_analysis_visualization
from sprint_visualizations import render_sprint_plan_visualization
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
if "progress" not in st.session_state:
    st.session_state.progress = {}
if "current_task" not in st.session_state:
    st.session_state.current_task = None
if "task_status" not in st.session_state:
    st.session_state.task_status = {}

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
    Update progress in session state.
    
    Args:
        task_id: ID of the current task
        status: Status of the task ('running', 'completed', 'error')
        index: Index of the current task
        total: Total number of tasks
    """
    # Update progress percentage
    st.session_state.progress[task_id] = {
        "status": status,
        "index": index,
        "total": total
    }
    st.session_state.current_task = task_id
    st.session_state.task_status[task_id] = status

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
    analyze_feedback_task = Task(
        description=f"Analyze the following user feedback and identify key patterns, priorities, and insights:\n\n{feedback_data}",
        agent=feedback_analyst,
        expected_output="A detailed analysis of user feedback with key patterns, priorities, and actionable insights."
    )
    
    generate_features_task = Task(
        description="Based on the feedback analysis, generate 3-5 feature proposals that address the most important user needs.",
        agent=feature_planner,
        expected_output="A list of 3-5 feature proposals with descriptions, justifications, and expected impact.",
        dependencies=["analyze_feedback"]
    )
    
    evaluate_feasibility_task = Task(
        description="Evaluate the technical feasibility of the proposed features. For each feature, assess complexity, potential challenges, and estimated effort.",
        agent=technical_evaluator,
        expected_output="A technical evaluation of each proposed feature, including complexity rating, potential challenges, and estimated effort.",
        dependencies=["generate_features"]
    )
    
    create_sprint_plan_task = Task(
        description="Create a sprint plan based on the feature proposals and technical evaluation. Organize features into sprints and create a timeline for implementation.",
        agent=sprint_planner,
        expected_output="A sprint plan with features organized into sprints, estimated timelines, and resource allocation.",
        dependencies=["evaluate_feasibility"]
    )
    
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

def run_workflow():
    """Run the project evolution workflow"""
    try:
        # Reset progress
        st.session_state.progress = {}
        st.session_state.current_task = None
        st.session_state.task_status = {}
        
        # Create crew with agents and tasks
        crew = create_agents_and_tasks(st.session_state.feedback_data)
        
        # Run the crew
        start_time = time.time()
        result = crew.run()
        end_time = time.time()
        
        # Add execution time to result
        result["execution_time"] = f"{end_time - start_time:.2f} seconds"
        result["execution_log"] = crew.get_execution_log()
        
        return result
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
    
    # Execution mode
    st.markdown('<div class="task-header">🔄 Execution Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Select execution mode:", ["sequential", "parallel"])
    st.session_state.mode = mode
    
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
    
    # Start/Stop buttons
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("▶️ Start", disabled=st.session_state.running)
    with col2:
        stop_button = st.button("⏹️ Stop", disabled=not st.session_state.running)
    
    if start_button:
        if not st.session_state.feedback_data:
            st.error("Please provide feedback data")
        else:
            st.session_state.running = True
            with st.spinner("Running agents..."):
                st.session_state.result = run_workflow()
                st.session_state.running = False
    
    if stop_button:
        st.session_state.running = False
        st.success("Agents stopped")

# Main content area
if st.session_state.running:
    st.markdown('''
<div class="content-box" style="background-color: #E3F2FD; border-color: #2196F3;">
    <div class="task-header" style="color: #2196F3;">🔄 Agents are running...</div>
    <div class="info-text">The AI agents are analyzing your feedback data. This process may take a few minutes depending on the complexity of the data.</div>
</div>
''', unsafe_allow_html=True)
    
    # Display progress
    if st.session_state.progress:
        # Create a container for progress display
        progress_container = st.container()
        
        with progress_container:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            # Show current task
            if st.session_state.current_task:
                st.markdown(f'<div class="subheader">🔄 Current Task: {st.session_state.current_task}</div>', unsafe_allow_html=True)
            
            # Show task statuses
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="task-header">📊 Task Progress:</div>', unsafe_allow_html=True)
                task_names = [
                    "analyze_feedback",
                    "generate_features",
                    "evaluate_feasibility",
                    "create_sprint_plan",
                    "generate_update"
                ]
                
                task_icons = {
                    "analyze_feedback": "🔍",
                    "generate_features": "💡",
                    "evaluate_feasibility": "⚙️",
                    "create_sprint_plan": "📅",
                    "generate_update": "📢"
                }
                
                for task_id in task_names:
                    icon = task_icons.get(task_id, "📋")
                    if task_id in st.session_state.task_status:
                        status = st.session_state.task_status[task_id]
                        if status == 'running':
                            st.markdown(f'<div class="status-running">{icon} {task_id}: 🔄 In Progress</div>', unsafe_allow_html=True)
                        elif status == 'completed':
                            st.markdown(f'<div class="status-completed">{icon} {task_id}: ✅ Completed</div>', unsafe_allow_html=True)
                        elif status == 'error':
                            st.markdown(f'<div class="status-error">{icon} {task_id}: ❌ Error</div>', unsafe_allow_html=True)
                        elif status == 'skipped':
                            st.markdown(f'<div class="status-pending">{icon} {task_id}: ⏭️ Skipped</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-pending">{icon} {task_id}: ⏳ Pending</div>', unsafe_allow_html=True)
            
            with col2:
                # Calculate overall progress
                completed = sum(1 for status in st.session_state.task_status.values() 
                               if status in ['completed', 'error', 'skipped'])
                total = len(task_names)
                progress = completed / total if total > 0 else 0
                
                st.markdown('<div class="task-header">📈 Overall Progress:</div>', unsafe_allow_html=True)
                st.progress(progress)
                st.markdown(f'<div style="text-align: center; font-size: 1.2rem; font-weight: bold; color: #673AB7;">{int(progress * 100)}% Complete</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
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
                
                # Render the feedback analysis visualizations
                render_feedback_analysis_visualization(feedback_analysis)
                
                # Display the raw text below the visualizations
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📖 Detailed Analysis</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown(feedback_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No feedback analysis available</div>', unsafe_allow_html=True)
        
        # Feature Proposals tab
        with tabs[1]:
            st.markdown('<div class="subheader">💡 Feature Proposals</div>', unsafe_allow_html=True)
            
            # Get feature proposals text
            feature_proposals = st.session_state.result.get("generate_features", "")
            
            if feature_proposals:
                # Extract features and their details using regex
                features = []
                
                # Try to find numbered features (1. Feature Name:)
                feature_pattern = r'\d+\.\s+([^:\n]+)(?::|\n)([^\n]+)'
                matches = re.findall(feature_pattern, feature_proposals)
                
                if matches:
                    for match in matches:
                        feature_name = match[0].strip()
                        feature_desc = match[1].strip() if len(match) > 1 else ""
                        
                        # Try to determine priority and complexity
                        priority = "Medium"
                        if re.search(r'high\s+priority|critical|urgent', feature_desc.lower()):
                            priority = "High"
                        elif re.search(r'low\s+priority|nice\s+to\s+have', feature_desc.lower()):
                            priority = "Low"
                        
                        complexity = "Medium"
                        if re.search(r'complex|difficult|challenging|hard', feature_desc.lower()):
                            complexity = "High"
                        elif re.search(r'simple|easy|straightforward', feature_desc.lower()):
                            complexity = "Low"
                        
                        features.append({
                            "name": feature_name,
                            "description": feature_desc,
                            "priority": priority,
                            "complexity": complexity
                        })
                
                # If we have features, create visualizations at the top
                if features:
                    st.markdown('<div class="section-title">📊 Feature Visualizations</div>', unsafe_allow_html=True)
                    
                    # Create a simplified visualization using HTML instead of Plotly
                    # This should be more lightweight and reduce freezing
                    
                    # Count features by priority and complexity
                    priority_counts = {"Low": 0, "Medium": 0, "High": 0}
                    complexity_counts = {"Low": 0, "Medium": 0, "High": 0}
                    priority_complexity_matrix = {
                        "Low": {"Low": [], "Medium": [], "High": []},
                        "Medium": {"Low": [], "Medium": [], "High": []},
                        "High": {"Low": [], "Medium": [], "High": []}
                    }
                    
                    for feature in features:
                        priority = feature["priority"]
                        complexity = feature["complexity"]
                        priority_counts[priority] += 1
                        complexity_counts[complexity] += 1
                        priority_complexity_matrix[priority][complexity].append(feature["name"])
                    
                    # Create a matrix visualization using HTML
                    matrix_html = '''
                    <div style="margin-top: 20px; margin-bottom: 20px;">
                        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                            <tr>
                                <th style="border: 1px solid #ddd; padding: 15px; background-color: #673AB7; color: white;">Priority / Complexity</th>
                                <th style="border: 1px solid #ddd; padding: 15px; background-color: #673AB7; color: white;">Low Complexity</th>
                                <th style="border: 1px solid #ddd; padding: 15px; background-color: #673AB7; color: white;">Medium Complexity</th>
                                <th style="border: 1px solid #ddd; padding: 15px; background-color: #673AB7; color: white;">High Complexity</th>
                            </tr>
                    '''
                    
                    # Priority rows
                    for priority in ["High", "Medium", "Low"]:
                        matrix_html += f'''
                        <tr>
                            <td style="border: 1px solid #ddd; padding: 15px; font-weight: bold; background-color: {'#EF5350' if priority == 'High' else '#FFB74D' if priority == 'Medium' else '#90CAF9'}; color: white;">{priority} Priority</td>
                        '''
                        
                        # Complexity columns
                        for complexity in ["Low", "Medium", "High"]:
                            features_in_cell = priority_complexity_matrix[priority][complexity]
                            cell_color = "#E8F5E9" if priority == "High" and complexity == "Low" else \
                                         "#FFF9C4" if (priority == "High" and complexity == "Medium") or (priority == "Medium" and complexity == "Low") else \
                                         "#FFEBEE" if priority == "High" and complexity == "High" else \
                                         "#E3F2FD" if priority == "Low" and complexity == "Low" else \
                                         "#F5F5F5"
                            
                            feature_list = "<br>".join([f"• {name}" for name in features_in_cell]) if features_in_cell else "None"
                            
                            matrix_html += f'''
                            <td style="border: 1px solid #ddd; padding: 15px; vertical-align: top; background-color: {cell_color};">
                                {feature_list}
                            </td>
                            '''
                        
                        matrix_html += "</tr>"
                    
                    matrix_html += "</table></div>"
                    
                    # Display the matrix using components.html instead of markdown
                    components.html(matrix_html, height=300)
                    
                    # Create a table of features with color coding
                    st.markdown('<div class="section-title">📝 Feature Details</div>', unsafe_allow_html=True)
                    
                    # Use our new component to render the feature details table
                    render_feature_details_table(features)
                    
                    # Display the raw text below the visualizations
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                    st.markdown('<div class="section-title">📖 Detailed Feature Proposals</div>', unsafe_allow_html=True)
                    st.markdown('<div class="result-container">', unsafe_allow_html=True)
                    st.markdown(feature_proposals)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No feature proposals available</div>', unsafe_allow_html=True)
        
        # Technical Evaluation tab
        with tabs[2]:
            st.markdown('<div class="subheader">⚙️ Technical Evaluation</div>', unsafe_allow_html=True)
            
            # Get technical evaluation text
            tech_eval = st.session_state.result.get("evaluate_feasibility", "")
            
            if tech_eval:
                # Add visualization at the top
                st.markdown('<div class="section-title">📊 Technical Feasibility Analysis</div>', unsafe_allow_html=True)
                render_technical_evaluation_visualization(tech_eval)
                
                # Display the raw text below the visualizations
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📖 Detailed Technical Evaluation</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown(tech_eval)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No technical evaluation available</div>', unsafe_allow_html=True)
        
        # Sprint Plan tab
        with tabs[3]:
            st.markdown('<div class="subheader">📅 Sprint Plan</div>', unsafe_allow_html=True)
            
            # Get sprint plan text
            sprint_plan = st.session_state.result.get("create_sprint_plan", "")
            
            if sprint_plan:
                # Add visualization at the top
                st.markdown('<div class="section-title">📅 Sprint Timeline</div>', unsafe_allow_html=True)
                render_sprint_plan_visualization(sprint_plan)
                
                # Display the raw text below the visualizations
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📖 Detailed Sprint Plan</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown(sprint_plan)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No sprint plan available</div>', unsafe_allow_html=True)
        
        # Stakeholder Update tab
        with tabs[4]:
            st.markdown('<div class="subheader">📢 Stakeholder Update</div>', unsafe_allow_html=True)
            
            # Get stakeholder update text
            stakeholder_update = st.session_state.result.get("generate_update", "")
            
            if stakeholder_update:
                # Add visualization at the top
                st.markdown('<div class="section-title">📊 Project Status Overview</div>', unsafe_allow_html=True)
                render_stakeholder_update_visualization(stakeholder_update)
                
                # Display the raw text below the visualizations
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📖 Detailed Stakeholder Update</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.markdown(stakeholder_update)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-container">No stakeholder update available</div>', unsafe_allow_html=True)
        
        # Execution Log tab
        with tabs[5]:
            st.markdown('<div class="subheader">📋 Execution Log</div>', unsafe_allow_html=True)
            log_container = st.container()
            with log_container:
                for log_entry in st.session_state.result.get("execution_log", []):
                    st.text(log_entry)
