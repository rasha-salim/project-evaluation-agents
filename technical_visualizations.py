import streamlit.components.v1 as components
import re
import math
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_technical_evaluation_visualization(tech_eval_text):
    """
    Create visualizations for the technical evaluation tab
    
    Args:
        tech_eval_text: The technical evaluation text from the AI
    """
    # Try to extract feasibility ratings
    feasibility_data = extract_feasibility_data(tech_eval_text)
    
    # Only create visualizations if we have real data
    if feasibility_data:
        # Create a radar chart for technical feasibility
        radar_html = create_feasibility_radar_chart(feasibility_data)
        components.html(radar_html, height=1000)
        
        # Create implementation difficulty bars
        difficulty_html = create_difficulty_bars(feasibility_data)
        components.html(difficulty_html, height=500)
    else:
        # Display a message when no data could be extracted
        components.html(
            '<div style="padding: 20px; background-color: #f5f5f5; border-radius: 8px; text-align: center;">' +
            '<h3 style="color: #666;">No technical evaluation data could be extracted</h3>' +
            '<p>The visualization will appear when technical evaluation data is available.</p>' +
            '</div>',
            height=200
        )
    

def extract_feasibility_data(text):
    """Extract feasibility data from technical evaluation text"""
    features = []
    
    # Look for feature sections
    feature_pattern = r'(?:Feature|Implementation|Component)(?:\s+\d+)?[:\-]\s+([^\n]+)'
    feature_matches = re.findall(feature_pattern, text, re.IGNORECASE)
    
    for feature_name in feature_matches:
        # Find the section for this feature
        feature_section_pattern = re.escape(feature_name) + r'.*?(?=(?:Feature|Implementation|Component)(?:\s+\d+)?[:\-]|$)'
        feature_section = re.search(feature_section_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if not feature_section:
            continue
            
        section_text = feature_section.group(0)
        
        # Extract ratings
        technical_complexity = extract_rating(section_text, r'(?:Technical Complexity|Complexity)[:\-]\s*(\w+)')
        feasibility = extract_rating(section_text, r'(?:Feasibility|Viability)[:\-]\s*(\w+)')
        risk = extract_rating(section_text, r'(?:Risk|Risks)[:\-]\s*(\w+)')
        effort = extract_rating(section_text, r'(?:Effort|Time|Resources)[:\-]\s*(\w+)')
        
        # Extract dependencies
        dependencies = []
        dep_pattern = r'(?:Dependencies|Requires|Dependent on)[:\-]\s*([^\n]+)'
        dep_match = re.search(dep_pattern, section_text, re.IGNORECASE)
        if dep_match:
            dep_text = dep_match.group(1)
            dependencies = [d.strip() for d in re.split(r',|;', dep_text)]
        
        features.append({
            'name': feature_name.strip(),
            'technical_complexity': normalize_rating(technical_complexity),
            'feasibility': normalize_rating(feasibility),
            'risk': normalize_rating(risk),
            'effort': normalize_rating(effort),
            'dependencies': dependencies
        })
    
    return features

def extract_rating(text, pattern):
    """Extract a rating from text using regex pattern"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip().lower()
    return 'medium'  # Default to medium if not found

def normalize_rating(rating):
    """Convert text ratings to numeric values"""
    if not rating:
        return 3  # Default to medium
        
    rating = rating.lower()
    
    # High values
    if rating in ['high', 'difficult', 'complex', 'hard', 'significant', 'major', 'substantial']:
        return 5
    # Medium-high values
    elif rating in ['medium-high', 'moderate-high', 'above average']:
        return 4
    # Medium values
    elif rating in ['medium', 'moderate', 'average', 'fair', 'reasonable']:
        return 3
    # Low-medium values
    elif rating in ['medium-low', 'moderate-low', 'below average']:
        return 2
    # Low values
    elif rating in ['low', 'easy', 'simple', 'straightforward', 'minimal', 'minor']:
        return 1
    else:
        # Try to extract numeric values
        numeric_match = re.search(r'(\d+)(?:/\d+)?', rating)
        if numeric_match:
            value = int(numeric_match.group(1))
            if '/' in rating:  # It's a fraction like 3/5
                denominator = int(re.search(r'\d+/(\d+)', rating).group(1))
                normalized = (value / denominator) * 5
                return min(5, max(1, round(normalized)))
            elif value <= 5:  # Assume it's already on a 1-5 scale
                return value
            else:  # Assume it's on a 1-10 scale
                return min(5, max(1, round(value / 2)))
                
        return 3  # Default to medium

def create_feasibility_radar_chart(features):
    """Create a radar chart for technical feasibility"""
    # Create the HTML for the radar chart
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Technical Feasibility Assessment</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 20px;">
    '''
    
    # Create a radar chart for each feature
    for feature in features:
        # Calculate points for the radar chart (pentagon)
        points = []
        metrics = [
            ('Technical Complexity', 5 - feature['technical_complexity'] + 1),  # Invert so lower complexity is better
            ('Feasibility', feature['feasibility']),
            ('Risk Level', 5 - feature['risk'] + 1),  # Invert so lower risk is better
            ('Effort Required', 5 - feature['effort'] + 1),  # Invert so lower effort is better
            ('Overall Score', (feature['feasibility'] + (5 - feature['technical_complexity'] + 1) + 
                              (5 - feature['risk'] + 1) + (5 - feature['effort'] + 1)) / 4)
        ]
        
        # Determine color based on overall score
        overall_score = metrics[-1][1]
        color = '#4CAF50' if overall_score >= 4 else '#FFC107' if overall_score >= 3 else '#F44336'
        
        html += f'''
        <div style="flex: 1; min-width: 300px; max-width: 400px; background-color: #f9f9f9; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; color: #333; text-align: center;">{feature['name']}</h4>
            <div style="position: relative; width: 100%; height: 200px; margin: 0 auto;">
                <svg width="100%" height="100%" viewBox="0 0 200 200">
                    <!-- Pentagon background -->
                    <polygon points="100,10 190,75 155,180 45,180 10,75" fill="#f0f0f0" stroke="#ccc" />
                    
                    <!-- Rating lines -->
                    <polygon points="100,82 136,115 124,156 76,156 64,115" fill="none" stroke="#ddd" />
                    <polygon points="100,46 172,95 140,168 60,168 28,95" fill="none" stroke="#ddd" />
                    <polygon points="100,28 181,85 147,174 53,174 19,85" fill="none" stroke="#ddd" />
                    <polygon points="100,10 190,75 155,180 45,180 10,75" fill="none" stroke="#ddd" />
                    
                    <!-- Data pentagon -->
        '''
        
        # Calculate points for the data pentagon
        data_points = []
        for i, (label, value) in enumerate(metrics):
            angle = (2 * 3.14159 * i) / 5 - 3.14159 / 2
            radius = 90 * (value / 5)
            x = 100 + radius * math.cos(angle)
            y = 100 + radius * math.sin(angle)
            data_points.append(f"{x},{y}")
        
        html += f'''
                    <polygon points="{' '.join(data_points)}" fill="{color}80" stroke="{color}" stroke-width="2" />
                    
                    <!-- Labels -->
        '''
        
        # Add labels
        for i, (label, value) in enumerate(metrics):
            angle = (2 * 3.14159 * i) / 5 - 3.14159 / 2
            x = 100 + 105 * math.cos(angle)
            y = 100 + 105 * math.sin(angle)
            
            # Adjust text anchor based on position
            text_anchor = "middle"
            if x < 70:
                text_anchor = "end"
            elif x > 130:
                text_anchor = "start"
                
            dy = "0.3em"
            if y < 50:
                dy = "1em"
            elif y > 150:
                dy = "-0.5em"
                
            html += f'''
                    <text x="{x}" y="{y}" text-anchor="{text_anchor}" dy="{dy}" font-size="10" fill="#333">{label}</text>
            '''
            
            # Add value indicators
            data_x = 100 + 90 * (value / 5) * math.cos(angle)
            data_y = 100 + 90 * (value / 5) * math.sin(angle)
            
            html += f'''
                    <circle cx="{data_x}" cy="{data_y}" r="3" fill="{color}" />
            '''
        
        html += '''
                </svg>
            </div>
        '''
        
        # Add dependencies if any
        if feature['dependencies']:
            html += '''
            <div style="margin-top: 15px;">
                <h5 style="margin-top: 0; color: #555;">Dependencies:</h5>
                <ul style="margin-top: 5px; padding-left: 20px;">
            '''
            
            for dep in feature['dependencies']:
                html += f'''
                <li style="margin-bottom: 5px;">{dep}</li>
                '''
                
            html += '''
                </ul>
            </div>
            '''
            
        html += '''
        </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def create_difficulty_bars(features):
    """Create implementation difficulty bars"""
    html = '''
    <div style="margin-top: 30px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Implementation Difficulty</h3>
        <div style="margin-top: 20px;">
    '''
    
    # Sort features by effort (difficulty)
    sorted_features = sorted(features, key=lambda x: x['effort'], reverse=True)
    
    for feature in sorted_features:
        effort = feature['effort']
        effort_percentage = (effort / 5) * 100
        
        # Determine color based on effort
        color = '#F44336' if effort >= 4 else '#FFC107' if effort >= 3 else '#4CAF50'
        
        html += f'''
        <div style="margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 150px; text-align: right; padding-right: 15px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{feature['name']}">{feature['name']}</div>
                <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                    <div style="width: {effort_percentage}%; height: 100%; background-color: {color}; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: 500;">
                        {['Very Easy', 'Easy', 'Moderate', 'Difficult', 'Very Difficult'][effort-1]}
                    </div>
                </div>
            </div>
        </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def render_technical_evaluation(tech_eval_data):
    """
    Render technical evaluation visualizations
    
    Args:
        tech_eval_data (dict): Technical evaluation data from LLM extraction
    """
    if not tech_eval_data or not tech_eval_data.get('features'):
        st.warning("No technical evaluation data available to visualize.")
        return
    
    features = tech_eval_data.get('features', [])
    
    # Check if we have user priority focus information
    has_priority_focus = any('aligns_with_priority' in feature for feature in features)
    user_priority_focus = None
    
    # Get the user priority focus if available
    if has_priority_focus and features and 'user_priority_focus' in features[0]:
        user_priority_focus = features[0]['user_priority_focus']
        
        # Display a priority focus banner
        st.markdown(f"<div class='priority-focus-banner'>Priority Focus: {user_priority_focus}</div>", unsafe_allow_html=True)
    
    # Create columns for the visualizations
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Create a feature complexity chart
        render_complexity_chart(features, has_priority_focus)
    
    with col2:
        # Create an effort estimation chart
        render_effort_chart(features, has_priority_focus)
    
    # Create a technical challenges table
    render_challenges_table(features, has_priority_focus)

def render_complexity_chart(features, has_priority_focus=False):
    """
    Render a bar chart showing feature complexity
    
    Args:
        features (list): List of feature dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Feature Complexity")
    
    # Prepare data for the chart
    feature_names = []
    complexity_values = []
    colors = []
    
    for feature in features:
        feature_names.append(feature['name'])
        complexity_values.append(feature.get('complexity', 3))
        
        # Set color based on priority alignment
        if has_priority_focus and feature.get('aligns_with_priority', False):
            colors.append('#ff9800')  # Orange for priority-aligned features
        else:
            colors.append('#4CAF50')  # Green for regular features
    
    # Create the bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=feature_names,
        y=complexity_values,
        marker_color=colors,
        text=complexity_values,
        textposition='auto',
    ))
    
    # Update layout
    fig.update_layout(
        title="Technical Complexity (1-5)",
        xaxis_title="Feature",
        yaxis_title="Complexity Rating",
        yaxis=dict(range=[0, 5.5]),
        height=400,
    )
    
    # Add a legend if we have priority focus
    if has_priority_focus:
        fig.add_trace(go.Bar(
            x=[None],
            y=[None],
            marker_color='#ff9800',
            name="Aligns with Priority",
            showlegend=True
        ))
        
        fig.add_trace(go.Bar(
            x=[None],
            y=[None],
            marker_color='#4CAF50',
            name="Regular Feature",
            showlegend=True
        ))
    
    st.plotly_chart(fig, use_container_width=True)

def render_effort_chart(features, has_priority_focus=False):
    """
    Render a pie chart showing effort distribution
    
    Args:
        features (list): List of feature dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Effort Distribution")
    
    # Prepare data for the chart
    feature_names = []
    effort_values = []
    colors = []
    
    for feature in features:
        feature_names.append(feature['name'])
        effort_values.append(feature.get('effort', 5))
        
        # Set color based on priority alignment
        if has_priority_focus and feature.get('aligns_with_priority', False):
            colors.append('#ff9800')  # Orange for priority-aligned features
        else:
            colors.append('#4CAF50')  # Green for regular features
    
    # Create the pie chart
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=feature_names,
        values=effort_values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hole=0.3,
    ))
    
    # Update layout
    fig.update_layout(
        title="Estimated Effort (person-days)",
        height=400,
    )
    
    # Add a legend if we have priority focus
    if has_priority_focus:
        fig.update_layout(
            legend_title="Feature Type",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
    
    st.plotly_chart(fig, use_container_width=True)

def render_challenges_table(features, has_priority_focus=False):
    """
    Render a table showing technical challenges for each feature
    
    Args:
        features (list): List of feature dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Technical Challenges")
    
    # Create a DataFrame for the table
    data = []
    
    for feature in features:
        # Get the challenges list or default to empty list
        challenges = feature.get('challenges', [])
        challenges_text = ', '.join(challenges) if challenges else 'None identified'
        
        # Add priority indicator if needed
        priority_indicator = '⭐ ' if has_priority_focus and feature.get('aligns_with_priority', False) else ''
        
        data.append({
            'Feature': f"{priority_indicator}{feature['name']}",
            'Difficulty': feature.get('difficulty', 'Medium'),
            'Challenges': challenges_text
        })
    
    # Create and display the DataFrame
    if data:
        df = pd.DataFrame(data)
        
        # Apply styling to highlight priority-aligned features
        def highlight_priority(row):
            if '⭐' in row['Feature']:
                return ['background-color: #fff8e1'] * len(row)
            return [''] * len(row)
        
        # Apply the styling if we have priority focus
        if has_priority_focus:
            styled_df = df.style.apply(highlight_priority, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No technical challenges data available.")

