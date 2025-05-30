import streamlit.components.v1 as components
import re
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_stakeholder_update_visualization(update_text):
    """
    Create visualizations for the stakeholder update tab
    
    Args:
        update_text: The stakeholder update text from the AI
    """
    # Extract key metrics and progress data
    metrics = extract_metrics(update_text)
    
    # Only create visualizations if we have real data
    if metrics and metrics['total_features'] > 0:
        # Create a progress overview visualization
        progress_html = create_progress_overview(metrics)
        components.html(progress_html, height=400)
        
        # Create a key achievements visualization
        achievements_html = create_achievements_visualization(update_text, metrics)
        components.html(achievements_html, height=500)
    else:
        # Display a message when no data could be extracted
        components.html(
            '<div style="padding: 20px; background-color: #f5f5f5; border-radius: 8px; text-align: center;">' +
            '<h3 style="color: #666;">No stakeholder update data could be extracted</h3>' +
            '<p>The visualization will appear when stakeholder update data is available.</p>' +
            '</div>',
            height=200
        )
    

# Sample metrics function removed - we now only use real data

def extract_metrics(text):
    """Extract metrics data from stakeholder update text"""
    metrics = {
        'completed_features': 0,
        'in_progress_features': 0,
        'planned_features': 0,
        'total_features': 0,
        'completion_percentage': 0,
        'key_achievements': [],
        'challenges': [],
        'next_steps': []
    }
    
    # Extract completion metrics
    completed_match = re.search(r'(\d+)\s*(?:features|tasks)?\s*completed', text, re.IGNORECASE)
    if completed_match:
        metrics['completed_features'] = int(completed_match.group(1))
    
    in_progress_match = re.search(r'(\d+)\s*(?:features|tasks)?\s*in\s*progress', text, re.IGNORECASE)
    if in_progress_match:
        metrics['in_progress_features'] = int(in_progress_match.group(1))
    
    planned_match = re.search(r'(\d+)\s*(?:features|tasks)?\s*planned', text, re.IGNORECASE)
    if planned_match:
        metrics['planned_features'] = int(planned_match.group(1))
    
    # Calculate total features
    metrics['total_features'] = metrics['completed_features'] + metrics['in_progress_features'] + metrics['planned_features']
    
    # Calculate completion percentage
    if metrics['total_features'] > 0:
        metrics['completion_percentage'] = int((metrics['completed_features'] / metrics['total_features']) * 100)
    
    # Extract key achievements
    achievements_section = re.search(r'(?:achievements|accomplishments|highlights)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                   text, re.IGNORECASE)
    if achievements_section:
        metrics['key_achievements'] = [a.strip() for a in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', achievements_section.group(1))]
    
    # Extract challenges
    challenges_section = re.search(r'(?:challenges|risks|issues)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                 text, re.IGNORECASE)
    if challenges_section:
        metrics['challenges'] = [c.strip() for c in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', challenges_section.group(1))]
    
    # Extract next steps
    next_steps_section = re.search(r'(?:next steps|future work|recommendations)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                 text, re.IGNORECASE)
    if next_steps_section:
        metrics['next_steps'] = [s.strip() for s in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', next_steps_section.group(1))]
    
    return metrics

def create_progress_overview(metrics):
    """Create a progress overview visualization"""
    # Calculate the values for the progress bars
    completed = metrics['completed_features']
    in_progress = metrics['in_progress_features']
    planned = metrics['planned_features']
    total = metrics['total_features']
    completion_percentage = metrics['completion_percentage']
    
    # Create HTML for the visualization
    html = '<div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">'
    html += '<h3 style="color: #333; margin-bottom: 15px;">Project Progress Overview</h3>'
    
    # Create a progress meter
    html += f'''
    <div style="margin-bottom: 30px; text-align: center;">
        <div style="font-size: 48px; font-weight: bold; color: #4CAF50;">{completion_percentage}%</div>
        <div style="font-size: 16px; color: #666;">Project Completion</div>
    </div>
    '''
    
    # Create feature status breakdown
    html += '<div style="display: flex; justify-content: space-around; margin-bottom: 20px;">'
    
    # Completed features
    html += f'''
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 36px; font-weight: bold; color: #4CAF50;">{completed}</div>
        <div style="font-size: 14px; color: #666;">Completed</div>
    </div>
    '''
    
    # In-progress features
    html += f'''
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 36px; font-weight: bold; color: #2196F3;">{in_progress}</div>
        <div style="font-size: 14px; color: #666;">In Progress</div>
    </div>
    '''
    
    # Planned features
    html += f'''
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 36px; font-weight: bold; color: #9E9E9E;">{planned}</div>
        <div style="font-size: 14px; color: #666;">Planned</div>
    </div>
    '''
    
    html += '</div>'
    
    # Create a progress bar
    html += '<div style="margin-top: 20px;">'
    html += '<div style="margin-bottom: 5px; display: flex; justify-content: space-between;">'
    html += '<span style="font-size: 14px; color: #666;">Overall Progress</span>'
    html += f'<span style="font-size: 14px; color: #666;">{completion_percentage}%</span>'
    html += '</div>'
    
    # Progress bar container
    html += '<div style="height: 24px; background-color: #e0e0e0; border-radius: 12px; overflow: hidden;">'
    
    # Progress bar fill
    html += f'<div style="height: 100%; width: {completion_percentage}%; background-color: #4CAF50; border-radius: 12px;"></div>'
    
    html += '</div>'
    html += '</div>'
    
    html += '</div>'
    
    return html

def create_achievements_visualization(text, metrics=None):
    """Create a visualization for key achievements, challenges, and next steps"""
    # Extract achievements, challenges, and next steps
    achievements = []
    challenges = []
    next_steps = []
    
    if metrics:
        achievements = metrics.get('key_achievements', [])
        challenges = metrics.get('challenges', [])
        next_steps = metrics.get('next_steps', [])
    else:
        # Extract from text if metrics not provided
        achievements_section = re.search(r'(?:achievements|accomplishments|highlights)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                       text, re.IGNORECASE)
        if achievements_section:
            achievements = [a.strip() for a in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', achievements_section.group(1))]
        
        challenges_section = re.search(r'(?:challenges|risks|issues)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                     text, re.IGNORECASE)
        if challenges_section:
            challenges = [c.strip() for c in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', challenges_section.group(1))]
        
        next_steps_section = re.search(r'(?:next steps|future work|recommendations)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                     text, re.IGNORECASE)
        if next_steps_section:
            next_steps = [s.strip() for s in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', next_steps_section.group(1))]
    
    # Create HTML for the visualization
    html = '<div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;">'    
    html += '<h3 style="color: #333; margin-bottom: 15px;">Project Status Overview</h3>'
    
    # Create a grid layout
    html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">'
    
    # Key Achievements section
    html += '<div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'    
    html += '<h4 style="margin-top: 0; color: #4CAF50;">Key Achievements</h4>'
    html += '<ul style="margin-top: 10px; padding-left: 20px;">'
    for achievement in achievements[:5]:  # Show top 5
        html += f'<li>{achievement}</li>'
    if not achievements:
        html += '<li><em>No achievements reported</em></li>'
    html += '</ul>'
    html += '</div>'
    
    # Challenges section
    html += '<div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'    
    html += '<h4 style="margin-top: 0; color: #F44336;">Challenges & Risks</h4>'
    html += '<ul style="margin-top: 10px; padding-left: 20px;">'
    for challenge in challenges[:5]:  # Show top 5
        html += f'<li>{challenge}</li>'
    if not challenges:
        html += '<li><em>No challenges reported</em></li>'
    html += '</ul>'
    html += '</div>'
    
    # Next Steps section
    html += '<div style="background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'    
    html += '<h4 style="margin-top: 0; color: #2196F3;">Next Steps</h4>'
    html += '<ul style="margin-top: 10px; padding-left: 20px;">'
    for step in next_steps[:5]:  # Show top 5
        html += f'<li>{step}</li>'
    if not next_steps:
        html += '<li><em>No next steps reported</em></li>'
    html += '</ul>'
    html += '</div>'
    
    html += '</div>'
    html += '</div>'
    
    return html


def render_stakeholder_update(update_data):
    """
    Render stakeholder update visualizations
    
    Args:
        update_data (dict): Stakeholder update data from LLM extraction
    """
    if not update_data:
        st.warning("No stakeholder update data available to visualize.")
        return
    
    # Check if we have user priority focus information
    has_priority_focus = False
    user_priority_focus = None
    
    # Check for priority focus in the data
    if 'user_priority_focus' in update_data:
        user_priority_focus = update_data['user_priority_focus']
        has_priority_focus = True
        
        # Display a priority focus banner
        st.markdown(f"<div class='priority-focus-banner'>Priority Focus: {user_priority_focus}</div>", unsafe_allow_html=True)
        
        # Display priority focus summary if available
        if 'priority_focus_summary' in update_data and update_data['priority_focus_summary']:
            st.markdown("### Priority Focus Summary")
            st.markdown(f"<div class='priority-summary'>{update_data['priority_focus_summary']}</div>", unsafe_allow_html=True)
    
    # Create columns for the visualizations
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Render highlights
        render_highlights(update_data, has_priority_focus)
    
    with col2:
        # Render risks
        render_risks(update_data, has_priority_focus)
    
    # Render action items
    render_action_items(update_data, has_priority_focus)


def render_highlights(update_data, has_priority_focus=False):
    """
    Render project highlights and metrics
    
    Args:
        update_data (dict): Stakeholder update data
        has_priority_focus (bool): Whether to highlight priority-aligned items
    """
    st.subheader("Project Highlights")
    
    highlights = update_data.get('highlights', [])
    priority_highlights = update_data.get('priority_highlights', []) if has_priority_focus else []
    
    if not highlights:
        st.info("No project highlights available.")
        return
    
    # Create a DataFrame for the highlights
    data = []
    
    for highlight in highlights:
        # Check if this is a priority highlight
        is_priority = highlight in priority_highlights
        priority_indicator = '⭐ ' if is_priority else ''
        
        data.append({
            'Highlight': f"{priority_indicator}{highlight}"
        })
    
    # Create and display the DataFrame
    df = pd.DataFrame(data)
    
    # Apply styling to highlight priority items
    def highlight_priority(row):
        if '⭐' in row['Highlight']:
            return ['background-color: #fff8e1']
        return ['']
    
    # Apply the styling if we have priority focus
    if has_priority_focus and priority_highlights:
        styled_df = df.style.apply(highlight_priority, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=min(400, len(data) * 35 + 38))
    else:
        st.dataframe(df, use_container_width=True, height=min(400, len(data) * 35 + 38))
    
    # Render metrics if available
    metrics = update_data.get('metrics', [])
    priority_metrics = update_data.get('priority_metrics', []) if has_priority_focus else []
    
    if metrics:
        st.subheader("Key Metrics")
        
        # Create metrics columns
        metric_cols = st.columns(min(3, len(metrics)))
        
        for i, metric in enumerate(metrics):
            # Check if this is a priority metric
            is_priority = metric in priority_metrics
            priority_indicator = '⭐ ' if is_priority else ''
            
            # Extract metric name and value
            if ':' in metric:
                name, value = metric.split(':', 1)
            else:
                name, value = metric, 'N/A'
            
            # Display the metric in the appropriate column
            with metric_cols[i % len(metric_cols)]:
                st.metric(
                    label=f"{priority_indicator}{name.strip()}",
                    value=value.strip(),
                    delta=None
                )


def render_risks(update_data, has_priority_focus=False):
    """
    Render project risks and challenges
    
    Args:
        update_data (dict): Stakeholder update data
        has_priority_focus (bool): Whether to highlight priority-aligned items
    """
    st.subheader("Risks & Challenges")
    
    risks = update_data.get('risks', [])
    priority_risks = update_data.get('priority_risks', []) if has_priority_focus else []
    
    if not risks:
        st.info("No risks or challenges identified.")
        return
    
    # Create a DataFrame for the risks
    data = []
    
    for risk in risks:
        # Extract risk text and impact level
        risk_text = risk
        impact = 'Medium'  # Default
        
        if isinstance(risk, dict):
            risk_text = risk.get('text', '')
            impact = risk.get('impact', 'Medium')
        elif ':' in risk:
            risk_parts = risk.split(':', 1)
            risk_text = risk_parts[0].strip()
            impact_text = risk_parts[1].strip().lower()
            
            if 'high' in impact_text:
                impact = 'High'
            elif 'low' in impact_text:
                impact = 'Low'
        
        # Check if this is a priority risk
        is_priority = risk in priority_risks or risk_text in priority_risks
        priority_indicator = '⭐ ' if is_priority else ''
        
        # Set color based on impact level
        if impact.lower() == 'high':
            impact_color = 'red'
        elif impact.lower() == 'medium':
            impact_color = 'orange'
        else:
            impact_color = 'green'
        
        data.append({
            'Risk': f"{priority_indicator}{risk_text}",
            'Impact': impact,
            'Impact_Color': impact_color
        })
    
    # Create and display the DataFrame
    if data:
        df = pd.DataFrame(data)
        
        # Apply styling to color-code impact levels and highlight priority items
        def style_risk_table(row):
            color = row['Impact_Color']
            styles = ['', f'color: {color}; font-weight: bold']
            
            # Add background color for priority items
            if '⭐' in row['Risk'] and has_priority_focus:
                styles = ['background-color: #fff8e1', f'background-color: #fff8e1; color: {color}; font-weight: bold']
                
            return styles
        
        # Apply the styling
        styled_df = df[['Risk', 'Impact']].style.apply(style_risk_table, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=min(400, len(data) * 35 + 38))
    else:
        st.info("No risk data available.")


def render_action_items(update_data, has_priority_focus=False):
    """
    Render next steps and resource needs
    
    Args:
        update_data (dict): Stakeholder update data
        has_priority_focus (bool): Whether to highlight priority-aligned items
    """
    # Get next steps and resources
    next_steps = update_data.get('next_steps', [])
    resources = update_data.get('resources', [])
    
    priority_next_steps = update_data.get('priority_next_steps', []) if has_priority_focus else []
    priority_resources = update_data.get('priority_resources', []) if has_priority_focus else []
    
    # Create columns for next steps and resources
    if next_steps or resources:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Next Steps")
            
            if next_steps:
                # Create a DataFrame for next steps
                data = []
                
                for step in next_steps:
                    # Check if this is a priority step
                    is_priority = step in priority_next_steps
                    priority_indicator = '⭐ ' if is_priority else ''
                    
                    data.append({
                        'Action': f"{priority_indicator}{step}"
                    })
                
                # Create and display the DataFrame
                df = pd.DataFrame(data)
                
                # Apply styling to highlight priority items
                def highlight_priority(row):
                    if '⭐' in row['Action']:
                        return ['background-color: #fff8e1']
                    return ['']
                
                # Apply the styling if we have priority focus
                if has_priority_focus and priority_next_steps:
                    styled_df = df.style.apply(highlight_priority, axis=1)
                    st.dataframe(styled_df, use_container_width=True, height=min(400, len(data) * 35 + 38))
                else:
                    st.dataframe(df, use_container_width=True, height=min(400, len(data) * 35 + 38))
            else:
                st.info("No next steps available.")
        
        with col2:
            st.subheader("Resource Needs")
            
            if resources:
                # Create a DataFrame for resources
                data = []
                
                for resource in resources:
                    # Check if this is a priority resource
                    is_priority = resource in priority_resources
                    priority_indicator = '⭐ ' if is_priority else ''
                    
                    data.append({
                        'Resource': f"{priority_indicator}{resource}"
                    })
                
                # Create and display the DataFrame
                df = pd.DataFrame(data)
                
                # Apply styling to highlight priority items
                def highlight_priority(row):
                    if '⭐' in row['Resource']:
                        return ['background-color: #fff8e1']
                    return ['']
                
                # Apply the styling if we have priority focus
                if has_priority_focus and priority_resources:
                    styled_df = df.style.apply(highlight_priority, axis=1)
                    st.dataframe(styled_df, use_container_width=True, height=min(400, len(data) * 35 + 38))
                else:
                    st.dataframe(df, use_container_width=True, height=min(400, len(data) * 35 + 38))
            else:
                st.info("No resource needs available.")
    else:
        st.info("No action items or resource needs available.")
