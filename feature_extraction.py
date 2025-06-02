"""
Feature extraction module for Project Evolution Agents.
Uses LLM to extract structured feature data from feature proposals text.
"""
import re
from direct_agents.agent import Agent
from direct_agents.task import Task
from anthropic import Anthropic
import json
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd

def extract_features_with_llm(feature_proposals_text, user_priority_focus=None):
    """
    Extract structured feature data from feature proposals text using LLM.
    
    Args:
        feature_proposals_text (str): The text containing feature proposals
        user_priority_focus (str, optional): User's priority focus
        
    Returns:
        dict: Structured feature data
    """
    # Create an agent to extract features
    feature_extractor = Agent(
        role="Feature Analyst",
        goal="Extract structured feature data from feature proposals text",
        backstory="You are an expert in analyzing feature proposals and extracting structured data about each feature.",
        verbose=False
    )
    
    # Adjust the task description based on whether there's a user priority focus
    priority_instruction = ""
    if user_priority_focus:
        priority_instruction = "\n\nIMPORTANT: The user has requested to " + user_priority_focus + ". For each feature, also indicate whether it aligns with this priority focus (Yes or No)."
    
    # Create a task for the agent to extract features
    # Prepare the format template based on user priority focus
    format_template = """
FEATURE 1:
Name: [feature name]
Description: [feature description]
Priority: [High/Medium/Low]
Complexity: [High/Medium/Low]"""
    
    # Add alignment line if user priority focus is specified
    if user_priority_focus:
        format_template += "\nAligns with User Priority: [Yes/No]"
    
    # Create the task with the appropriate description
    task_description = """Extract structured feature data from the following feature proposals text.
For each feature mentioned, identify:
1. Feature name
2. Feature description
3. Priority level (High, Medium, or Low)
4. Complexity level (High, Medium, or Low)"""
    
    # Add priority instruction if needed
    task_description += priority_instruction
    
    # Add format instructions
    task_description += """

Format your response exactly as follows:
"""
    
    # Add format template
    task_description += format_template
    
    # Add second feature example
    feature2_template = """

FEATURE 2:
Name: [feature name]
Description: [feature description]
Priority: [High/Medium/Low]
Complexity: [High/Medium/Low]"""
    
    # Add alignment line for second feature if needed
    if user_priority_focus:
        feature2_template += "\nAligns with User Priority: [Yes/No]"
    
    task_description += feature2_template
    
    # Add final instructions and feature proposals text
    task_description += """

And so on for all features.

Here's the feature proposals text to analyze:
"""
    
    # Add the actual feature proposals text
    task_description += feature_proposals_text
    
    extraction_task = Task(
        description=task_description,
        agent=feature_extractor,
        expected_output="Structured feature data"
    )
    
    # Execute the task
    result = extraction_task.execute()
    
    # Parse the result to extract structured feature data
    features = parse_feature_extraction_result(result, user_priority_focus)
    
    return {
        "features": features,
        "user_priority_focus": user_priority_focus
    }

def parse_feature_extraction_result(result_text, user_priority_focus=None):
    """
    Parse the feature extraction result text into structured data.
    
    Args:
        result_text (str): The text result from the LLM
        user_priority_focus (str, optional): User's priority focus
        
    Returns:
        list: List of feature dictionaries
    """
    features = []
    
    # First try to parse using regex patterns
    try:
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
            
            # Extract feature description
            desc_match = re.search(r'Description:\s*(.*?)(?:\n|$)', section)
            if desc_match:
                feature['description'] = desc_match.group(1).strip()
            
            # Extract priority with fallback to Medium if not found
            priority_match = re.search(r'Priority:\s*(High|Medium|Low)', section, re.IGNORECASE)
            feature['priority'] = priority_match.group(1).capitalize() if priority_match else "Medium"
            
            # Extract complexity with fallback to Medium if not found
            complexity_match = re.search(r'Complexity:\s*(High|Medium|Low)', section, re.IGNORECASE)
            feature['complexity'] = complexity_match.group(1).capitalize() if complexity_match else "Medium"
            
            # Extract alignment with user priority if applicable
            if user_priority_focus:
                align_match = re.search(r'Aligns with User Priority:\s*(Yes|No)', section, re.IGNORECASE)
                if align_match:
                    feature['aligns_with_priority'] = align_match.group(1).lower() == 'yes'
                else:
                    feature['aligns_with_priority'] = False
            
            # Add the feature to the list if it has at least a name
            if 'name' in feature:
                features.append(feature)
    
    except Exception as e:
        # If regex parsing fails, use LLM to extract features
        if not features:
            # Create a backup extraction using LLM
            features = extract_features_with_llm_fallback(result_text, user_priority_focus)
    
    # If we still don't have features with required fields, create a minimal valid structure
    if not features or any('priority' not in feature or 'complexity' not in feature for feature in features):
        # Create a minimal set of features with required fields
        cleaned_features = []
        for i, feature in enumerate(features):
            cleaned_feature = {
                'name': feature.get('name', f"Feature {i+1}"),
                'description': feature.get('description', "No description available"),
                'priority': feature.get('priority', "Medium"),
                'complexity': feature.get('complexity', "Medium")
            }
            if user_priority_focus and 'aligns_with_priority' in feature:
                cleaned_feature['aligns_with_priority'] = feature['aligns_with_priority']
            cleaned_features.append(cleaned_feature)
        
        # If we have no features at all, create a placeholder
        if not cleaned_features:
            cleaned_features = [{
                'name': "Feature extraction incomplete",
                'description': "The feature extraction process couldn't identify specific features. Please review the raw text.",
                'priority': "Medium",
                'complexity': "Medium"
            }]
        
        features = cleaned_features
    
    return features

def extract_features_with_llm_fallback(feature_text, user_priority_focus=None):
    """
    Fallback method to extract features using LLM when regex parsing fails.
    
    Args:
        feature_text (str): The text containing feature information
        user_priority_focus (str, optional): User's priority focus
        
    Returns:
        list: List of feature dictionaries
    """
    # Create an agent to extract features in a structured format
    feature_extractor = Agent(
        role="Feature Extraction Specialist",
        goal="Extract structured feature data from text",
        backstory="You are an expert in parsing and structuring feature information from text.",
        verbose=False
    )
    
    # Create a task for the agent to extract features
    task_description = f"""
    Parse the following text and extract structured feature data.
    For each feature, identify:
    1. Feature name
    2. Feature description
    3. Priority level (High, Medium, or Low)
    4. Complexity level (High, Medium, or Low)
    
    If any information is missing, use your best judgment to assign reasonable values.
    
    Format your response as a JSON array of feature objects with the following structure:
    [{{"name": "Feature Name", "description": "Feature description", "priority": "High/Medium/Low", "complexity": "High/Medium/Low"}}]
    
    Here's the text to parse:
    {feature_text}
    """
    
    extraction_task = Task(
        description=task_description,
        agent=feature_extractor,
        expected_output="JSON array of feature objects"
    )
    
    # Execute the task
    try:
        result = extraction_task.execute()
        
        # Try to parse the result as JSON
        import json
        try:
            # Find JSON array in the text if it's embedded in other text
            json_match = re.search(r'\[\s*{.*}\s*\]', result, re.DOTALL)
            if json_match:
                result = json_match.group(0)
            
            features = json.loads(result)
            
            # Ensure all features have required fields
            for feature in features:
                if 'name' not in feature:
                    feature['name'] = "Unnamed Feature"
                if 'description' not in feature:
                    feature['description'] = "No description available"
                if 'priority' not in feature:
                    feature['priority'] = "Medium"
                if 'complexity' not in feature:
                    feature['complexity'] = "Medium"
                
                # Capitalize priority and complexity
                feature['priority'] = feature['priority'].capitalize()
                feature['complexity'] = feature['complexity'].capitalize()
                
                # Add alignment with user priority if applicable
                if user_priority_focus and 'aligns_with_priority' not in feature:
                    feature['aligns_with_priority'] = False
            
            return features
        except json.JSONDecodeError:
            # If JSON parsing fails, create a minimal structure
            return [{
                'name': "Feature from unstructured text",
                'description': result[:200] + "...",  # Use part of the result as description
                'priority': "Medium",
                'complexity': "Medium"
            }]
    except Exception as e:
        # If extraction fails completely, return a minimal structure
        return [{
            'name': "Feature extraction failed",
            'description': f"Could not extract features: {str(e)}",
            'priority': "Medium",
            'complexity': "Medium"
        }]

def render_feature_visualization(feature_data):
    """
    Create visualizations for the feature extraction tab
    
    Args:
        feature_data: The feature data from the AI
    """
    features = feature_data.get('features', [])
    user_priority_focus = feature_data.get('user_priority_focus')
    
    # Only create visualizations if we have features
    if features:
        # Create a feature table
        st.subheader("Extracted Features")
        
        # Create a DataFrame for the features
        df_data = []
        for feature in features:
            feature_row = {
                "Feature": feature.get('name', 'Unnamed'),
                "Description": feature.get('description', ''),
                "Priority": feature.get('priority', 'Medium'),
                "Complexity": feature.get('complexity', 'Medium')
            }
            
            # Add priority alignment if applicable
            if user_priority_focus and 'aligns_with_priority' in feature:
                feature_row["Aligns with Priority"] = "✅" if feature['aligns_with_priority'] else "❌"
            
            df_data.append(feature_row)
        
        # Create a DataFrame and display it
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        
        # Create a priority-complexity matrix
        create_priority_complexity_matrix(features, user_priority_focus)
        
        # Create a priority distribution chart
        create_priority_distribution_chart(features, user_priority_focus)

def create_priority_complexity_matrix(features, user_priority_focus=None):
    """
    Create a priority-complexity matrix visualization
    
    Args:
        features (list): List of feature dictionaries
        user_priority_focus (str, optional): User's priority focus
    """
    # Create a 3x3 matrix for Priority (High, Medium, Low) vs Complexity (High, Medium, Low)
    st.markdown('<div class="section-title">📊 Priority-Complexity Matrix</div>', unsafe_allow_html=True)
    
    # Count features in each cell
    matrix_data = {
        priority: {complexity: 0 for complexity in ["Low", "Medium", "High"]}
        for priority in ["High", "Medium", "Low"]
    }
    
    # Count features in each cell
    for feature in features:
        priority = feature.get('priority', 'Medium')
        complexity = feature.get('complexity', 'Medium')
        matrix_data[priority][complexity] += 1
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[[matrix_data["High"]["Low"], matrix_data["High"]["Medium"], matrix_data["High"]["High"]],
           [matrix_data["Medium"]["Low"], matrix_data["Medium"]["Medium"], matrix_data["Medium"]["High"]],
           [matrix_data["Low"]["Low"], matrix_data["Low"]["Medium"], matrix_data["Low"]["High"]]],
        x=["Low", "Medium", "High"],
        y=["High", "Medium", "Low"],
        hoverongaps=False,
        colorscale=[
            [0, "#CCFFCC"],  # Light green for 0
            [0.5, "#FFB74D"],  # Orange for middle values
            [1, "#EF5350"]   # Red for highest values
        ],
        showscale=False,
        text=[[f"{matrix_data['High']['Low']} features", f"{matrix_data['High']['Medium']} features", f"{matrix_data['High']['High']} features"],
              [f"{matrix_data['Medium']['Low']} features", f"{matrix_data['Medium']['Medium']} features", f"{matrix_data['Medium']['High']} features"],
              [f"{matrix_data['Low']['Low']} features", f"{matrix_data['Low']['Medium']} features", f"{matrix_data['Low']['High']} features"]],
        texttemplate="%{text}",
        textfont={"size":12}
    ))
    
    fig.update_layout(
        title="Feature Distribution by Priority and Complexity",
        xaxis_title="Complexity",
        yaxis_title="Priority",
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(side="bottom"),
        yaxis=dict(side="left")
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_priority_distribution_chart(features, user_priority_focus=None):
    """
    Create a priority distribution chart
    
    Args:
        features (list): List of feature dictionaries
        user_priority_focus (str, optional): User's priority focus
    """
    # Count features by priority
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    
    for feature in features:
        priority = feature.get('priority', 'Medium')
        priority_counts[priority] += 1
    
    # Create the chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(priority_counts.keys()),
            y=list(priority_counts.values()),
            marker_color=["#EF5350", "#FFB74D", "#66BB6A"],
            text=list(priority_counts.values()),
            textposition="auto"
        )
    ])
    
    fig.update_layout(
        title="Feature Distribution by Priority",
        xaxis_title="Priority Level",
        yaxis_title="Number of Features",
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_feature_matrix(features):
    """
    Render a priority-complexity matrix for features
    
    Args:
        features (list): List of feature dictionaries with name, priority, and complexity
    """
    # Create a 3x3 matrix for Priority (High, Medium, Low) vs Complexity (High, Medium, Low)
    st.markdown('<div class="section-title">🔄 Priority-Complexity Matrix</div>', unsafe_allow_html=True)
    
    # Create the matrix as an HTML table
    matrix_html = """
    <div style="margin: 20px 0;">
    <table style="width: 100%; border-collapse: collapse; text-align: center;">
        <tr>
            <th style="border: 1px solid #ddd; padding: 15px;"></th>
            <th style="border: 1px solid #ddd; padding: 15px; background-color: #f2f2f2;">Low Complexity</th>
            <th style="border: 1px solid #ddd; padding: 15px; background-color: #f2f2f2;">Medium Complexity</th>
            <th style="border: 1px solid #ddd; padding: 15px; background-color: #f2f2f2;">High Complexity</th>
        </tr>
    """
    
    # Define cell colors
    cell_colors = {
        "High": {
            "High": "#FFCCCC",  # Red for High Priority, High Complexity
            "Medium": "#FFE5CC", # Orange for High Priority, Medium Complexity
            "Low": "#FFFFCC"     # Yellow for High Priority, Low Complexity
        },
        "Medium": {
            "High": "#E5CCFF",   # Purple for Medium Priority, High Complexity
            "Medium": "#E5E5E5", # Gray for Medium Priority, Medium Complexity
            "Low": "#CCFFFF"     # Cyan for Medium Priority, Low Complexity
        },
        "Low": {
            "High": "#CCCCFF",   # Blue for Low Priority, High Complexity
            "Medium": "#CCE5FF", # Light Blue for Low Priority, Medium Complexity
            "Low": "#CCFFCC"     # Green for Low Priority, Low Complexity
        }
    }
    
    # Check if we have user priority focus information
    has_priority_focus = any('aligns_with_priority' in feature for feature in features)
    
    # Add rows for each priority level
    for priority in ["High", "Medium", "Low"]:
        matrix_html += f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 15px; font-weight: bold; background-color: #f2f2f2;">{priority} Priority</td>
        """
        
        # Add cells for each complexity level
        for complexity in ["Low", "Medium", "High"]:
            # Get features that match this priority and complexity with defaults for missing fields
            features_in_cell = [f for f in features if f.get('priority', 'Medium') == priority and f.get('complexity', 'Medium') == complexity]
            
            # Get the cell color
            cell_color = cell_colors[priority][complexity]
            
            # Create a list of feature names for this cell
            feature_items = []
            for feature in features_in_cell:
                if has_priority_focus and feature.get("aligns_with_priority", False):
                    # Add a star for priority-aligned features
                    feature_items.append(f"• <span style=\"font-weight: bold; color: #4CAF50;\">{feature.get('name', 'Unnamed')} ⭐</span>")
                else:
                    feature_items.append(f"• {feature.get('name', 'Unnamed')}")
            
            feature_list = "<br>".join(feature_items) if feature_items else "No features"
            
            matrix_html += f"""
            <td style="border: 1px solid #ddd; padding: 15px; vertical-align: top; background-color: {cell_color};">
                {feature_list}
            </td>
            """
        
        matrix_html += "</tr>"
    
    matrix_html += "</table></div>"
    
    # Display the matrix
    components.html(matrix_html, height=350)
