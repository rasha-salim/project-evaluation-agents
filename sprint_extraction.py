"""
Sprint plan extraction module for Project Evolution Agents.
Uses LLM to extract structured sprint plan data from sprint plan text.
"""
import re
from direct_agents.agent import Agent
from direct_agents.task import Task
import streamlit.components.v1 as components
import plotly.graph_objects as go
import streamlit as st

def extract_sprint_plan_with_llm(sprint_plan_text, user_priority_focus=None):
    """
    Use the AI agent to extract structured sprint plan data
    
    Args:
        sprint_plan_text (str): Raw sprint plan text from the AI
        user_priority_focus (str, optional): User's priority focus from collaboration step
        
    Returns:
        dict: Dictionary with sprint plan data including sprints, features, and timeline
    """
    # Extract user priority focus if present in the text but not provided as parameter
    if not user_priority_focus and isinstance(sprint_plan_text, str):
        priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", sprint_plan_text)
        if priority_match:
            user_priority_focus = priority_match.group(1).strip()
    
    # Create a sprint plan extraction agent
    sprint_extractor = Agent(
        role="Sprint Planner",
        goal="Extract structured sprint plan data",
        backstory="You are an expert in analyzing sprint plans and extracting structured data about feature scheduling.",
        verbose=False
    )
    
    # Adjust the task description based on whether there's a user priority focus
    priority_instruction = ""
    if user_priority_focus:
        priority_instruction = "\n\nIMPORTANT: The user has requested to " + user_priority_focus + ". For each sprint, also indicate which features align with this priority focus by marking them with an asterisk (*) in the feature list."
    
    # Prepare the format template based on user priority focus
    format_template = """
SPRINT 1:
Duration: [number] weeks
Features: [comma-separated list of features]
Goals: [main goals/focus]
Dependencies: [dependencies or blockers, or "None" if none]"""
    
    # Add priority features line if user priority focus is specified
    if user_priority_focus:
        format_template += "\nPriority Features: [list features that align with user priority]"
    
    # Create the second sprint template
    sprint2_template = """

SPRINT 2:
Duration: [number] weeks
Features: [comma-separated list of features]
Goals: [main goals/focus]
Dependencies: [dependencies or blockers, or "None" if none]"""
    
    # Add priority features line for second sprint if needed
    if user_priority_focus:
        sprint2_template += "\nPriority Features: [list features that align with user priority]"
    
    # Create the task description
    task_description = """Extract structured sprint plan data from the following text.
For each sprint mentioned, identify:
1. Sprint number
2. Duration in weeks
3. Features planned for the sprint
4. Main goals/focus of the sprint
5. Dependencies or blockers"""
    
    # Add priority instruction if needed
    task_description += priority_instruction
    
    # Add format instructions
    task_description += """

Format your response exactly as follows:"""
    
    # Add format template
    task_description += format_template
    
    # Add second sprint template
    task_description += sprint2_template
    
    # Add final instructions and sprint plan text
    task_description += """

And so on for all sprints.

Here's the sprint plan text to analyze:
"""
    
    # Add the actual sprint plan text
    task_description += sprint_plan_text
    
    # Create a task for the agent to extract sprint plan data
    extraction_task = Task(
        description=task_description,
        agent=sprint_extractor,
        expected_output="Structured sprint plan data"
    )
    
    # Execute the task
    result = extraction_task.execute()
    
    # Parse the result to extract sprint plan data
    sprints = []
    current_sprint = {}
    
    # Check if we have user priority focus
    has_priority_focus = user_priority_focus is not None
    
    for line in result.split('\n'):
        line = line.strip()
        
        # Check for new sprint
        if line.startswith('SPRINT') or (not line and current_sprint and 'number' in current_sprint):
            if current_sprint and 'number' in current_sprint:
                sprints.append(current_sprint)
                current_sprint = {}
            
            if line.startswith('SPRINT'):
                try:
                    sprint_number = int(line.split()[1].strip(':'))
                    current_sprint['number'] = sprint_number
                except (IndexError, ValueError):
                    current_sprint['number'] = len(sprints) + 1
            
            continue
            
        # Extract sprint properties
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'duration':
                try:
                    current_sprint['duration'] = int(value.split()[0])  # Extract just the number
                except (ValueError, IndexError):
                    current_sprint['duration'] = 2  # Default to 2 weeks
            elif key == 'features':
                # Process features and check for priority indicators (*)
                features = []
                priority_features = []
                
                for feature in [f.strip() for f in value.split(',')]:
                    if feature.startswith('*') and has_priority_focus:
                        # This is a priority feature
                        clean_feature = feature[1:].strip()
                        features.append(clean_feature)
                        priority_features.append(clean_feature)
                    else:
                        features.append(feature)
                
                current_sprint['features'] = features
                if has_priority_focus:
                    current_sprint['priority_features'] = priority_features
            elif key == 'goals':
                current_sprint['goals'] = value
            elif key == 'dependencies':
                current_sprint['dependencies'] = value
            elif key == 'priority features' and has_priority_focus:
                current_sprint['priority_features'] = [f.strip() for f in value.split(',')]
    
    # Add the last sprint if it exists
    if current_sprint and 'number' in current_sprint:
        sprints.append(current_sprint)
        
    # Store the user priority focus for reference
    if has_priority_focus:
        for sprint in sprints:
            sprint['user_priority_focus'] = user_priority_focus
            
            # Ensure each sprint has a priority_features list
            if 'priority_features' not in sprint:
                sprint['priority_features'] = []
    
    # If no sprints were found, use regex as fallback
    if not sprints:
        sprints = extract_sprint_plan_with_regex(sprint_plan_text)
    
    # Calculate total duration
    total_duration = sum(sprint.get('duration', 2) for sprint in sprints)
    
    # Count features per sprint
    feature_counts = [len(sprint.get('features', [])) for sprint in sprints]
    
    # Collect all features
    all_features = []
    for sprint in sprints:
        all_features.extend(sprint.get('features', []))
    
    return {
        'sprints': sprints,
        'total_duration': total_duration,
        'feature_counts': feature_counts,
        'total_features': len(all_features)
    }

def extract_sprint_plan_with_regex(sprint_plan_text):
    """
    Fallback method to extract sprint plan data using regex
    
    Args:
        sprint_plan_text (str): Raw sprint plan text
        
    Returns:
        list: List of sprint dictionaries with sprint plan data
    """
    sprints = []
    
    # Try to find sprint sections
    sprint_sections = re.split(r'sprint\s+(\d+)', sprint_plan_text, flags=re.IGNORECASE)
    
    if len(sprint_sections) > 1:
        # First element is text before first sprint, skip it
        for i in range(1, len(sprint_sections), 2):
            if i + 1 < len(sprint_sections):
                sprint_number = int(sprint_sections[i])
                sprint_content = sprint_sections[i + 1]
                
                # Default values
                duration = 2
                features = []
                goals = "Complete planned features"
                dependencies = "None"
                
                # Extract duration
                duration_match = re.search(r'(\d+)\s*(?:week|wk)s?', sprint_content, re.IGNORECASE)
                if duration_match:
                    try:
                        duration = int(duration_match.group(1))
                    except ValueError:
                        pass
                
                # Extract features
                features_match = re.search(r'features?[:\-]([^\n]+)', sprint_content, re.IGNORECASE)
                if features_match:
                    features = [f.strip() for f in features_match.group(1).split(',')]
                else:
                    # Try to find bullet points or numbered lists
                    feature_items = re.findall(r'(?:^|\n)(?:\*|\-|\d+\.)\s*([^\n]+)', sprint_content)
                    features = [f.strip() for f in feature_items]
                
                # Extract goals
                goals_match = re.search(r'goals?[:\-]([^\n]+)', sprint_content, re.IGNORECASE)
                if goals_match:
                    goals = goals_match.group(1).strip()
                
                # Extract dependencies
                dependencies_match = re.search(r'dependenc(?:y|ies)[:\-]([^\n]+)', sprint_content, re.IGNORECASE)
                if dependencies_match:
                    dependencies = dependencies_match.group(1).strip()
                
                sprints.append({
                    'number': sprint_number,
                    'duration': duration,
                    'features': features,
                    'goals': goals,
                    'dependencies': dependencies
                })
    
    # If no sprints found, try another approach
    if not sprints:
        # Look for numbered sections that might be sprints
        sprint_matches = re.finditer(r'(?:^|\n)(\d+)[\.:\)]\s*([^\n]+)', sprint_plan_text)
        
        for match in sprint_matches:
            sprint_number = int(match.group(1))
            sprint_title = match.group(2).strip()
            
            sprints.append({
                'number': sprint_number,
                'duration': 2,  # Default
                'features': [sprint_title],  # Use the title as a feature
                'goals': "Complete planned features",
                'dependencies': "None"
            })
    
    return sprints

def render_sprint_plan(sprint_plan_data):
    """
    Render sprint plan visualizations
    
    Args:
        sprint_plan_data (dict): Sprint plan data from LLM extraction
    """
    sprints = sprint_plan_data['sprints']
    
    # Render timeline visualization
    render_sprint_timeline(sprints)
    
    # Render feature distribution
    render_feature_distribution(sprint_plan_data['feature_counts'])
    
    # Render sprint details
    render_sprint_details(sprints)

def render_sprint_timeline(sprints):
    """Render a timeline visualization for sprints"""
    # Create a Gantt chart
    fig = go.Figure()
    
    # Calculate start and end dates for each sprint
    current_week = 0
    for sprint in sprints:
        sprint_number = sprint.get('number', 0)
        duration = sprint.get('duration', 2)
        
        # Add a task for the sprint
        fig.add_trace(go.Bar(
            x=[duration],
            y=[f"Sprint {sprint_number}"],
            orientation='h',
            marker=dict(
                color='#673AB7',
                line=dict(color='rgba(0,0,0,0)', width=3)
            ),
            hoverinfo='text',
            hovertext=f"Sprint {sprint_number}: {duration} weeks<br>Features: {', '.join(sprint.get('features', [])[:3])}{'...' if len(sprint.get('features', [])) > 3 else ''}",
            name=f"Sprint {sprint_number}"
        ))
        
        current_week += duration
    
    # Update layout
    fig.update_layout(
        title="Sprint Timeline",
        xaxis=dict(
            title="Weeks",
            showgrid=True,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        yaxis=dict(
            autorange="reversed"
        ),
        height=300,
        margin=dict(l=150, r=20, t=30, b=30),
        showlegend=False
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def render_feature_distribution(feature_counts):
    """Render a bar chart for feature distribution across sprints"""
    # Create HTML for feature distribution
    html = '''
    <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
        <h3 style="margin-top: 0; color: #333;">Features per Sprint</h3>
    '''
    
    # Add bars for each sprint
    for i, count in enumerate(feature_counts):
        # Calculate percentage for bar width (max 100%)
        percentage = min(count * 10, 100)  # Assuming max 10 features per sprint
        
        html += f'''
        <div style="margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 80px; text-align: right; padding-right: 10px;">Sprint {i+1}</div>
                <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                    <div style="width: {percentage}%; height: 100%; background-color: #673AB7;"></div>
                </div>
                <div style="width: 50px; text-align: left; padding-left: 10px;">{count}</div>
            </div>
        </div>
        '''
    
    html += '</div>'
    
    # Display the HTML
    components.html(html, height=100 + len(feature_counts) * 30)

def render_sprint_details(sprints):
    """Render detailed information for each sprint"""
    # Create HTML for sprint details
    html = '''
    <div style="margin: 20px 0;">
    '''
    
    for sprint in sprints:
        sprint_number = sprint.get('number', 0)
        duration = sprint.get('duration', 2)
        features = sprint.get('features', [])
        goals = sprint.get('goals', "Complete planned features")
        dependencies = sprint.get('dependencies', "None")
        
        html += f'''
        <div style="margin-bottom: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid #673AB7;">
            <h3 style="margin-top: 0; color: #333;">Sprint {sprint_number} ({duration} weeks)</h3>
            
            <div style="margin-top: 10px;">
                <div style="font-weight: bold; color: #555;">Goals:</div>
                <div style="margin-left: 10px;">{goals}</div>
            </div>
            
            <div style="margin-top: 10px;">
                <div style="font-weight: bold; color: #555;">Features:</div>
                <ul style="margin-top: 5px; padding-left: 25px;">
        '''
        
        for feature in features:
            html += f'<li>{feature}</li>'
        
        html += f'''
                </ul>
            </div>
            
            <div style="margin-top: 10px;">
                <div style="font-weight: bold; color: #555;">Dependencies:</div>
                <div style="margin-left: 10px;">{dependencies}</div>
            </div>
        </div>
        '''
    
    html += '</div>'
    
    # Display the HTML
    components.html(html, height=700 + len(sprints) * 150)
