import streamlit.components.v1 as components
import re
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_sprint_plan_visualization(sprint_plan_text):
    """
    Create visualizations for the sprint plan tab
    
    Args:
        sprint_plan_text: The sprint plan text from the AI
    """
    # Extract sprints and tasks
    sprints, tasks = extract_sprint_data(sprint_plan_text)
    
    # Only create visualizations if we have real data
    if sprints and tasks:
        # Create a sprint timeline visualization
        timeline_html = create_sprint_timeline(sprints, tasks)
        components.html(timeline_html, height=700)
        
        # Create a sprint summary table
        table_html = create_sprint_summary_table(sprints)
        components.html(table_html, height=700)
    else:
        # Display a message when no data could be extracted
        components.html(
            '<div style="padding: 20px; background-color: #f5f5f5; border-radius: 8px; text-align: center;">' +
            '<h3 style="color: #666;">No sprint plan data could be extracted</h3>' +
            '<p>The visualization will appear when sprint plan data is available.</p>' +
            '</div>',
            height=200
        )

def extract_sprint_data(text):
    """Extract sprint data from sprint plan text"""
    sprints = []
    tasks = []
    
    # Try to find sprints
    sprint_pattern = r'Sprint\s+(\d+)[:\s]+([^\n]+)'
    sprint_matches = re.findall(sprint_pattern, text, re.IGNORECASE)
    
    # Try to find tasks within sprints
    task_pattern = r'(?:Task|Feature)\s*(?:\d+)?\s*[:\-]\s*([^\n]+)\s*(?:\n|$)'
    
    # If we found sprints, extract tasks for each sprint
    if sprint_matches:
        for sprint_num, sprint_desc in sprint_matches:
            sprint_num = int(sprint_num)
            sprint_section = re.search(f"Sprint\\s+{sprint_num}[:\\s].*?(?=Sprint\\s+\\d+[:\\s]|$)", text, re.DOTALL)
            
            if sprint_section:
                sprint_content = sprint_section.group(0)
                task_matches = re.findall(task_pattern, sprint_content)
                
                # Add tasks to the list
                for i, task_name in enumerate(task_matches):
                    tasks.append({
                        "Task": task_name.strip(),
                        "Sprint": f"Sprint {sprint_num}",
                        "Start": sprint_num * 10 - 9 + i,  # Approximate start day
                        "Duration": 5,  # Default duration
                        "Resource": "Team"
                    })
                
                # Add sprint to the list
                sprints.append({
                    "Sprint": sprint_num,
                    "Description": sprint_desc.strip(),
                    "Tasks": len(task_matches)
                })
    
    return sprints, tasks

def create_sprint_timeline(sprints, tasks):
    """Create a sprint timeline visualization"""
    # Group tasks by sprint
    tasks_by_sprint = {}
    for task in tasks:
        sprint = task["Sprint"]
        if sprint not in tasks_by_sprint:
            tasks_by_sprint[sprint] = []
        tasks_by_sprint[sprint].append(task)
    
    # Create the HTML for the timeline
    html = '''
    <div style="margin-top: 20px; margin-bottom: 20px;">
    '''
    
    # Sort sprints by number
    sorted_sprints = sorted(sprints, key=lambda x: x["Sprint"])
    
    # Create a timeline for each sprint
    for i, sprint in enumerate(sorted_sprints):
        sprint_num = sprint["Sprint"]
        sprint_name = f"Sprint {sprint_num}"
        
        # Generate a color based on the sprint number
        hue = (i * 60) % 360
        color = f"hsl({hue}, 70%, 65%)"
        
        html += f'''
        <div style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center;">
                <div style="background-color: {color}; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; width: 100px; text-align: center;">{sprint_name}</div>
                <div style="height: 2px; background-color: {color}; flex-grow: 1; margin-left: 10px;"></div>
            </div>
            <div style="margin-left: 20px; margin-top: 10px;">
        '''
        
        # Add tasks for this sprint
        if sprint_name in tasks_by_sprint:
            for j, task in enumerate(tasks_by_sprint[sprint_name]):
                html += f'''
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 20px; height: 20px; background-color: {color}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; margin-right: 10px;">{j+1}</div>
                    <div>{task["Task"]}</div>
                </div>
                '''
        
        html += '''
            </div>
        </div>
        '''
    
    html += '</div>'
    
    return html

def create_sprint_summary_table(sprints):
    """Create a sprint summary table"""
    html = '<div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;">'    
    html += '<h3 style="color: #333; margin-bottom: 15px;">Sprint Summary</h3>'
    html += '<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">'    
    html += '<tr style="background-color: #4CAF50; color: white;">'    
    html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Sprint</th>'
    html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Duration</th>'
    html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Features</th>'
    html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Goals</th>'
    html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Dependencies</th>'
    html += '</tr>'
    
    for sprint in sprints:
        html += f'<tr style="background-color: white;">'
        html += f'<td style="padding: 12px; text-align: left; border: 1px solid #ddd;">Sprint {sprint["number"]}</td>'
        html += f'<td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{sprint.get("duration", 2)} weeks</td>'
        
        # Format features as a list
        features = sprint.get("features", [])
        features_html = '<ul style="margin: 0; padding-left: 20px;">'    
        for feature in features:
            features_html += f'<li>{feature}</li>'
        features_html += '</ul>'
        html += f'<td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{features_html}</td>'
        
        # Add goals
        html += f'<td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{sprint.get("goals", "Not specified")}</td>'
        
        # Add dependencies
        html += f'<td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{sprint.get("dependencies", "None")}</td>'
        
        html += '</tr>'
    
    html += '</table>'
    html += '</div>'
    
    return html

def render_sprint_plan(sprint_plan_data):
    """
    Render sprint plan visualizations
    
    Args:
        sprint_plan_data (dict): Sprint plan data from LLM extraction
    """
    if not sprint_plan_data or not sprint_plan_data.get('sprints'):
        st.warning("No sprint plan data available to visualize.")
        return
    
    sprints = sprint_plan_data.get('sprints', [])
    
    # Check if we have user priority focus information
    has_priority_focus = any('priority_features' in sprint for sprint in sprints)
    user_priority_focus = None
    
    # Get the user priority focus if available
    if has_priority_focus and sprints and 'user_priority_focus' in sprints[0]:
        user_priority_focus = sprints[0]['user_priority_focus']
        
        # Display a priority focus banner
        st.markdown(f"<div class='priority-focus-banner'>Priority Focus: {user_priority_focus}</div>", unsafe_allow_html=True)
    
    # Render sprint timeline
    render_sprint_timeline(sprints, has_priority_focus)
    
    # Render feature distribution
    render_feature_distribution(sprints, has_priority_focus)
    
    # Render sprint details table
    render_sprint_details(sprints, has_priority_focus)

def render_sprint_timeline(sprints, has_priority_focus=False):
    """
    Render a Gantt chart showing the sprint timeline
    
    Args:
        sprints (list): List of sprint dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Sprint Timeline")
    
    # Prepare data for the chart
    tasks = []
    start_dates = []
    end_dates = []
    colors = []
    current_week = 0
    
    for sprint in sprints:
        sprint_number = sprint.get('number', 0)
        duration = sprint.get('duration', 2)
        
        # Calculate start and end dates (in weeks)
        start_week = current_week
        end_week = current_week + duration
        current_week = end_week
        
        # Add the sprint to the timeline
        tasks.append(f"Sprint {sprint_number}")
        start_dates.append(start_week)
        end_dates.append(end_week)
        colors.append('#4CAF50')  # Green for sprints
        
        # Add priority features if available
        if has_priority_focus and 'priority_features' in sprint and sprint['priority_features']:
            for feature in sprint['priority_features']:
                # Add a slightly indented task for each priority feature
                tasks.append(f"  {feature}")
                start_dates.append(start_week)
                end_dates.append(end_week)
                colors.append('#ff9800')  # Orange for priority features
    
    # Create the Gantt chart
    fig = go.Figure()
    
    for i in range(len(tasks)):
        fig.add_trace(go.Bar(
            y=[tasks[i]],
            x=[end_dates[i] - start_dates[i]],  # Duration
            base=start_dates[i],  # Start position
            orientation='h',
            marker=dict(color=colors[i]),
            text=[f"Weeks {start_dates[i]}-{end_dates[i]}"],
            textposition='inside',
            insidetextanchor='middle',
            width=0.6,
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title="Sprint Timeline (in weeks)",
        xaxis_title="Weeks",
        yaxis=dict(
            title="",
            autorange="reversed"  # To show tasks from top to bottom
        ),
        height=max(300, len(tasks) * 40),  # Adjust height based on number of tasks
        margin=dict(l=150)  # Add left margin for task names
    )
    
    # Add a legend if we have priority focus
    if has_priority_focus:
        fig.add_trace(go.Bar(
            y=[None],
            x=[None],
            marker_color='#ff9800',
            name="Priority Feature",
            showlegend=True
        ))
        
        fig.add_trace(go.Bar(
            y=[None],
            x=[None],
            marker_color='#4CAF50',
            name="Sprint",
            showlegend=True
        ))
        
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
    
    st.plotly_chart(fig, use_container_width=True)

def render_feature_distribution(sprints, has_priority_focus=False):
    """
    Render a bar chart showing feature distribution across sprints
    
    Args:
        sprints (list): List of sprint dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Feature Distribution")
    
    # Prepare data for the chart
    sprint_labels = [f"Sprint {sprint.get('number', 0)}" for sprint in sprints]
    regular_features = []
    priority_features = []
    
    for sprint in sprints:
        features = sprint.get('features', [])
        
        if has_priority_focus and 'priority_features' in sprint:
            # Count priority features
            priority_count = len(sprint.get('priority_features', []))
            priority_features.append(priority_count)
            
            # Count regular features (total - priority)
            regular_features.append(len(features) - priority_count)
        else:
            # All features are regular if no priority focus
            regular_features.append(len(features))
            priority_features.append(0)
    
    # Create the stacked bar chart
    fig = go.Figure()
    
    # Add regular features
    fig.add_trace(go.Bar(
        x=sprint_labels,
        y=regular_features,
        name='Regular Features',
        marker_color='#4CAF50'
    ))
    
    # Add priority features if we have priority focus
    if has_priority_focus and any(priority_features):
        fig.add_trace(go.Bar(
            x=sprint_labels,
            y=priority_features,
            name='Priority Features',
            marker_color='#ff9800'
        ))
    
    # Update layout
    fig.update_layout(
        title="Features per Sprint",
        xaxis_title="Sprint",
        yaxis_title="Number of Features",
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_sprint_details(sprints, has_priority_focus=False):
    """
    Render a table showing detailed information for each sprint
    
    Args:
        sprints (list): List of sprint dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Sprint Details")
    
    # Create a DataFrame for the table
    data = []
    
    for sprint in sprints:
        sprint_number = sprint.get('number', 0)
        duration = sprint.get('duration', 2)
        features = sprint.get('features', [])
        goals = sprint.get('goals', 'Not specified')
        dependencies = sprint.get('dependencies', 'None')
        
        # Format features with priority indicators
        feature_list = []
        for feature in features:
            if has_priority_focus and 'priority_features' in sprint and feature in sprint['priority_features']:
                feature_list.append(f" {feature}")
            else:
                feature_list.append(feature)
        
        features_text = ', '.join(feature_list)
        
        data.append({
            'Sprint': f"Sprint {sprint_number}",
            'Duration': f"{duration} weeks",
            'Features': features_text,
            'Goals': goals,
            'Dependencies': dependencies
        })
    
    # Create and display the DataFrame
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sprint details available.")
