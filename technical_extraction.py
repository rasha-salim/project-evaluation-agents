import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import re
from direct_agents.agent import Agent
from direct_agents.task import Task

def extract_technical_evaluation_with_llm(technical_eval_text, user_priority_focus=None):
    """
    Extract structured technical evaluation data from technical evaluation text using LLM
    
    Args:
        technical_eval_text (str): Technical evaluation text
        user_priority_focus (str, optional): User priority focus
        
    Returns:
        dict: Dictionary with features and user priority focus
    """
    # Create an agent to extract technical evaluation
    tech_evaluator = Agent(
        role="Technical Evaluator",
        goal="Extract structured technical evaluation data from the provided text",
        backstory="You are an expert in analyzing technical evaluations and extracting structured data about each feature.",
        verbose=False
    )
    
    # Adjust the task description based on whether there's a user priority focus
    priority_instruction = ""
    if user_priority_focus:
        priority_instruction = "\n\nIMPORTANT: The user has requested to " + user_priority_focus + ". For each feature, also indicate whether it aligns with this priority focus (Yes or No)."
    
    # Create the task with the appropriate description
    task_description = """Extract structured technical evaluation data from the following technical evaluation text.
    For each feature mentioned, identify:
    1. Feature name
    2. Technical complexity (1-5 scale)
    3. Implementation challenges
    4. Estimated effort (in person-days)
    5. Difficulty level (High, Medium, or Low)"""
    
    # Add priority instruction if needed
    task_description += priority_instruction
    
    # Add format instructions
    task_description += """
    
    Format your response exactly as follows:
    
    FEATURE 1:
    Name: [feature name]
    Complexity: [1-5 rating]
    Challenges: [list of technical challenges]
    Effort: [estimated person-days]
    Difficulty: [High/Medium/Low]"""
    
    # Add alignment line if user priority focus is specified
    if user_priority_focus:
        task_description += "\nAligns with User Priority: [Yes/No]"
    
    # Add second feature example
    task_description += """
    
    FEATURE 2:
    Name: [feature name]
    Complexity: [1-5 rating]
    Challenges: [list of technical challenges]
    Effort: [estimated person-days]
    Difficulty: [High/Medium/Low]"""
    
    # Add alignment line for second feature if needed
    if user_priority_focus:
        task_description += "\nAligns with User Priority: [Yes/No]"
    
    # Add final instructions and technical evaluation text
    task_description += """
    
    And so on for all features.
    
    Here's the technical evaluation text to analyze:
    """
    
    # Add the actual technical evaluation text
    task_description += technical_eval_text
    
    extraction_task = Task(
        description=task_description,
        agent=tech_evaluator,
        expected_output="Structured technical evaluation data"
    )
    
    # Execute the task
    result = extraction_task.execute()
    
    # Parse the result to extract structured technical evaluation data
    features = parse_technical_evaluation_result(result, user_priority_focus)
    
    # Calculate average complexity
    complexities = [feature.get('complexity', 3) for feature in features if 'complexity' in feature]
    avg_complexity = sum(complexities) / len(complexities) if complexities else 3
    
    return {
        'features': features,
        'avg_complexity': avg_complexity,
        'user_priority_focus': user_priority_focus
    }


def parse_technical_evaluation_result(result_text, user_priority_focus=None):
    """
    Parse the technical evaluation result text into structured data.
    
    Args:
        result_text (str): The text result from the LLM
        user_priority_focus (str, optional): User's priority focus
        
    Returns:
        list: List of feature dictionaries
    """
    features = []
    
    try:
        # First try to parse as JSON (in case the LLM returned JSON)
        try:
            json_data = json.loads(result_text)
            if isinstance(json_data, list):
                return json_data
            elif isinstance(json_data, dict) and 'features' in json_data:
                return json_data['features']
        except:
            pass  # Not JSON, continue with text parsing
        
        # Split the result text by feature sections
        feature_sections = re.split(r'FEATURE\s+\d+:', result_text)
        
        # Remove any empty sections
        feature_sections = [section.strip() for section in feature_sections if section.strip()]
        
        # Parse each feature section
        for section in feature_sections:
            feature = {}
            
            # Extract feature name
            name_match = re.search(r'Name:\s*(.*?)(?:\n|$)', section)
            if name_match:
                feature['name'] = name_match.group(1).strip()
            
            # Extract complexity (1-5 rating)
            complexity_match = re.search(r'Complexity:\s*(\d+)', section)
            if complexity_match:
                try:
                    feature['complexity'] = int(complexity_match.group(1).strip())
                except:
                    feature['complexity'] = 3  # Default to medium complexity
            
            # Extract challenges
            challenges_match = re.search(r'Challenges:\s*(.*?)(?:\n|$)', section)
            if challenges_match:
                challenges_text = challenges_match.group(1).strip()
                # Split challenges by commas or bullet points
                if ',' in challenges_text:
                    feature['challenges'] = [c.strip() for c in challenges_text.split(',')]
                elif '•' in challenges_text:
                    feature['challenges'] = [c.strip() for c in challenges_text.split('•') if c.strip()]
                else:
                    feature['challenges'] = [challenges_text]
            
            # Extract effort (person-days)
            effort_match = re.search(r'Effort:\s*(\d+(?:\.\d+)?)', section)
            if effort_match:
                try:
                    feature['effort'] = float(effort_match.group(1).strip())
                except:
                    feature['effort'] = 1.0  # Default to 1 person-day
            
            # Extract difficulty
            difficulty_match = re.search(r'Difficulty:\s*(High|Medium|Low)', section, re.IGNORECASE)
            if difficulty_match:
                feature['difficulty'] = difficulty_match.group(1).capitalize()
            
            # Extract alignment with user priority if applicable
            if user_priority_focus:
                align_match = re.search(r'Aligns with User Priority:\s*(Yes|No)', section, re.IGNORECASE)
                if align_match:
                    feature['aligns_with_priority'] = align_match.group(1).lower() == 'yes'
                else:
                    # Check if feature name or challenges contain the priority focus
                    feature_name = feature.get('name', '').lower()
                    feature_challenges = ' '.join(feature.get('challenges', [])).lower()
                    priority_focus = user_priority_focus.lower()
                    
                    feature['aligns_with_priority'] = (priority_focus in feature_name or 
                                                    priority_focus in feature_challenges)
            
            # Add the feature to the list if it has at least a name
            if 'name' in feature:
                features.append(feature)
        
        return features
    except Exception as e:
        st.error(f"Error parsing technical evaluation data: {str(e)}")
        return []

def create_rating_bar(rating, type_name):
    """Create HTML for a rating bar"""
    # Determine color based on rating and type
    if type_name == 'technical':
        # For technical complexity, higher is red (more complex)
        if rating >= 4:
            color = '#F44336'  # Red
        elif rating >= 3:
            color = '#FFC107'  # Yellow
        else:
            color = '#4CAF50'  # Green
    else:
        # For feasibility, higher is green (more feasible)
        if rating >= 4:
            color = '#4CAF50'  # Green
        elif rating >= 3:
            color = '#FFC107'  # Yellow
        else:
            color = '#F44336'  # Red
    
    # Create HTML for the rating bar
    html = f'''
    <div style="width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden;">
        <div style="width: {rating * 20}%; height: 100%; background-color: {color};"></div>
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
        <span style="font-size: 12px;">Low</span>
        <span style="font-size: 12px;">Medium</span>
        <span style="font-size: 12px;">High</span>
    </div>
    '''
    
    return html

def create_difficulty_bars(features):
    """Create implementation difficulty bars"""
    # Count features by difficulty
    difficulty_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    
    for feature in features:
        # Use technical rating to determine difficulty
        technical = feature.get('technical', 3)
        
        if technical >= 4:
            difficulty = 'High'
        elif technical >= 2:
            difficulty = 'Medium'
        else:
            difficulty = 'Low'
        
        difficulty_counts[difficulty] += 1
    
    # Create HTML for the difficulty bars
    html = '<div style="padding: 20px; background-color: #f8f9fa; border-radius: 8px;">'
    
    # Add title
    html += '<h3 style="margin-top: 0;">Implementation Difficulty</h3>'
    
    # Calculate total features
    total_features = sum(difficulty_counts.values())
    
    if total_features > 0:
        # Add bars for each difficulty level
        for difficulty, count in difficulty_counts.items():
            # Calculate percentage
            percentage = (count / total_features) * 100
            
            # Determine color based on difficulty
            if difficulty == 'High':
                color = '#F44336'  # Red
            elif difficulty == 'Medium':
                color = '#FFC107'  # Yellow
            else:
                color = '#4CAF50'  # Green
            
            html += f'''
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: bold;">{difficulty} Difficulty</span>
                    <span>{count} feature{'' if count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div style="height: 24px; background-color: #f0f0f0; border-radius: 12px; overflow: hidden;">
                    <div style="height: 100%; width: {percentage}%; background-color: {color};"></div>
                </div>
            </div>
            '''
        
        html += '</div>'
    else:
        html += '<p>No feature difficulty data available</p>'
    
    html += '</div>'
    
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
    user_priority_focus = tech_eval_data.get('user_priority_focus')
    
    # Display priority focus if available
    if user_priority_focus:
        st.markdown(f"<div class='priority-focus-banner'>Priority Focus: {user_priority_focus}</div>", unsafe_allow_html=True)
    
    # Create columns for the visualizations
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Render complexity chart
        render_complexity_chart(features, user_priority_focus is not None)
    
    with col2:
        # Render effort chart
        render_effort_chart(features, user_priority_focus is not None)
    
    # Render challenges table
    render_challenges_table(features, user_priority_focus is not None)


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
        name = feature.get('name', 'Unnamed')
        complexity = feature.get('complexity', 3)
        
        # Check if this feature aligns with priority focus
        is_priority = has_priority_focus and feature.get('aligns_with_priority', False)
        
        feature_names.append(f"⭐ {name}" if is_priority else name)
        complexity_values.append(complexity)
        
        # Set color based on complexity and priority alignment
        if is_priority:
            colors.append('#4CAF50')  # Green for priority-aligned features
        elif complexity >= 4:
            colors.append('#F44336')  # Red for high complexity
        elif complexity >= 3:
            colors.append('#FFC107')  # Yellow for medium complexity
        else:
            colors.append('#2196F3')  # Blue for low complexity
    
    # Create the bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=feature_names,
        y=complexity_values,
        marker_color=colors,
        text=complexity_values,
        textposition='auto'
    ))
    
    # Update layout
    fig.update_layout(
        title="Feature Complexity Ratings (1-5)",
        xaxis_title="Feature",
        yaxis_title="Complexity Rating",
        yaxis=dict(range=[0, 5.5]),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)


def render_effort_chart(features, has_priority_focus=False):
    """
    Render a pie chart showing effort distribution
    
    Args:
        features (list): List of feature dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Effort Distribution")
    
    # Group features by difficulty
    difficulty_groups = {"High": [], "Medium": [], "Low": []}
    
    for feature in features:
        difficulty = feature.get('difficulty', 'Medium')
        if difficulty not in difficulty_groups:
            difficulty = 'Medium'  # Default to Medium if invalid
        
        difficulty_groups[difficulty].append(feature)
    
    # Calculate total effort for each difficulty level
    labels = []
    values = []
    colors = []
    priority_labels = []
    
    for difficulty, group_features in difficulty_groups.items():
        if not group_features:
            continue
        
        # Calculate total effort for this difficulty level
        total_effort = sum(feature.get('effort', 0) for feature in group_features)
        
        if total_effort > 0:
            # Count priority-aligned features
            priority_features = [f for f in group_features if has_priority_focus and f.get('aligns_with_priority', False)]
            priority_effort = sum(feature.get('effort', 0) for feature in priority_features)
            
            # Add to the chart data
            if priority_effort > 0 and has_priority_focus:
                labels.append(f"{difficulty} Difficulty (Priority)")
                values.append(priority_effort)
                colors.append('#4CAF50')  # Green for priority
                priority_labels.append(True)
                
                # Add non-priority effort
                non_priority_effort = total_effort - priority_effort
                if non_priority_effort > 0:
                    labels.append(f"{difficulty} Difficulty")
                    values.append(non_priority_effort)
                    priority_labels.append(False)
                    
                    # Set color based on difficulty
                    if difficulty == 'High':
                        colors.append('#F44336')  # Red
                    elif difficulty == 'Medium':
                        colors.append('#FFC107')  # Yellow
                    else:
                        colors.append('#2196F3')  # Blue
            else:
                # Add all effort as non-priority
                labels.append(f"{difficulty} Difficulty")
                values.append(total_effort)
                priority_labels.append(False)
                
                # Set color based on difficulty
                if difficulty == 'High':
                    colors.append('#F44336')  # Red
                elif difficulty == 'Medium':
                    colors.append('#FFC107')  # Yellow
                else:
                    colors.append('#2196F3')  # Blue
    
    # Create the pie chart
    if values:
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textinfo='percent+label',
            pull=[0.1 if is_priority else 0 for is_priority in priority_labels]  # Pull out priority slices
        ))
        
        # Update layout
        fig.update_layout(
            title="Distribution of Implementation Effort (person-days)",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No effort data available to visualize.")


def render_challenges_table(features, has_priority_focus=False):
    """
    Render a table showing technical challenges for each feature
    
    Args:
        features (list): List of feature dictionaries
        has_priority_focus (bool): Whether to highlight priority-aligned features
    """
    st.subheader("Technical Challenges")
    
    # Create a DataFrame for the challenges
    data = []
    
    for feature in features:
        name = feature.get('name', 'Unnamed')
        challenges = feature.get('challenges', [])
        
        # Check if this feature aligns with priority focus
        is_priority = has_priority_focus and feature.get('aligns_with_priority', False)
        
        # Add priority indicator if applicable
        feature_name = f"⭐ {name}" if is_priority else name
        
        # Add each challenge to the table
        if challenges:
            challenge_text = "<br>".join([f"• {challenge}" for challenge in challenges])
        else:
            challenge_text = "No specific challenges identified"
        
        data.append({
            "Feature": feature_name,
            "Challenges": challenge_text
        })
    
    # Create and display the DataFrame
    if data:
        df = pd.DataFrame(data)
        
        # Apply styling to highlight priority-aligned features
        def highlight_priority(row):
            if '⭐' in row['Feature']:
                return ['background-color: #e6f7e6', 'background-color: #e6f7e6']
            return ['', '']
        
        # Apply the styling if we have priority focus
        if has_priority_focus:
            styled_df = df.style.apply(highlight_priority, axis=1)
            st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.write(df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("No challenge data available to visualize.")
