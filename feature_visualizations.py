import streamlit.components.v1 as components

def render_feature_details_table(features):
    """
    Render a feature details table using components.html
    
    Args:
        features: List of feature dictionaries with name, priority, complexity, and description
    """
    # Check if we have user priority focus
    has_priority_focus = any('user_priority_focus' in feature for feature in features if isinstance(feature, dict))
    user_priority_focus = None
    
    if has_priority_focus:
        for feature in features:
            if 'user_priority_focus' in feature:
                user_priority_focus = feature['user_priority_focus']
                break
    
    # Create a priority focus banner if applicable
    priority_banner = ""
    priority_color = "#9575CD"  # Default color
    
    if has_priority_focus and user_priority_focus:
        priority_color = "#FF7043" if "performance" in user_priority_focus.lower() else \
                         "#42A5F5" if "user experience" in user_priority_focus.lower() else \
                         "#66BB6A" if "new features" in user_priority_focus.lower() else "#9575CD"
        
        priority_banner = f'''
        <div style="padding: 10px; background-color: {priority_color}; color: white; border-radius: 5px; margin-bottom: 15px; text-align: center;">
            <h3 style="margin: 0;">Priority Focus: {user_priority_focus}</h3>
            <p style="margin: 5px 0 0 0;">Features aligned with this priority are highlighted</p>
        </div>
        '''
    
    # Create a styled table
    html_table = f'''
    <div style="overflow-x: auto;">
    {priority_banner}
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background-color: #673AB7; color: white;">
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Feature</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Priority</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Complexity</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Description</th>
                {f'<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Aligns with Priority</th>' if has_priority_focus else ''}
            </tr>
        </thead>
        <tbody>
    '''
    
    for feature in features:
        # Set colors based on priority and complexity
        priority_color = "#90CAF9" if feature["priority"] == "Low" else "#FFB74D" if feature["priority"] == "Medium" else "#EF5350"
        complexity_color = "#A5D6A7" if feature["complexity"] == "Low" else "#FFE082" if feature["complexity"] == "Medium" else "#FFAB91"
        
        # Check if feature aligns with priority
        aligns_with_priority = feature.get("aligns_with_priority", False) if has_priority_focus else False
        row_style = f"background-color: {f'rgba({int(priority_color[1:3], 16)}, {int(priority_color[3:5], 16)}, {int(priority_color[5:7], 16)}, 0.2)' if aligns_with_priority else '#f9f9f9'};"
        
        # Create alignment indicator
        alignment_cell = f'''
            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">
                {f'<span style="color: {priority_color}; font-weight: bold;">✓</span>' if aligns_with_priority else '–'}
            </td>
        ''' if has_priority_focus else ''
        
        html_table += f'''
        <tr style="{row_style}">
            <td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{feature["name"]}</td>
            <td style="padding: 12px; text-align: center; border: 1px solid #ddd; background-color: {priority_color};">{feature["priority"]}</td>
            <td style="padding: 12px; text-align: center; border: 1px solid #ddd; background-color: {complexity_color};">{feature["complexity"]}</td>
            <td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{feature["description"]}</td>
            {alignment_cell}
        </tr>
        '''
    
    html_table += '''
        </tbody>
    </table>
    </div>
    '''
    
    # Use components.html for the table
    components.html(html_table, height=len(features) * 50 + 350)

def render_feature_details(feature):
    """
    Render detailed information about a single feature using components.html
    
    Args:
        feature: Dictionary with feature details
    """
    # Default values if not provided
    name = feature.get("name", "Feature Name")
    description = feature.get("description", "No description available")
    priority = feature.get("priority", "Medium")
    complexity = feature.get("complexity", "Medium")
    user_impact = feature.get("user_impact", "Medium")
    benefits = feature.get("benefits", ["Improves user experience"])
    considerations = feature.get("considerations", ["Requires thorough testing"])
    
    # Set colors based on priority
    priority_color = "#4CAF50" if priority == "High" else "#FFC107" if priority == "Medium" else "#2196F3"
    
    # Create HTML for feature details
    feature_html = f'''
    <div style="margin-top: 20px; margin-bottom: 20px;">
        <div style="background-color: #F5F5F5; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid {priority_color}; padding-bottom: 10px;">{name}</h3>
            
            <div style="margin-top: 15px;">
                <div style="display: flex; margin-bottom: 15px;">
                    <div style="width: 120px; font-weight: bold; color: #555;">Priority:</div>
                    <div>
                        <span style="background-color: {priority_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">{priority}</span>
                    </div>
                </div>
                
                <div style="display: flex; margin-bottom: 15px;">
                    <div style="width: 120px; font-weight: bold; color: #555;">Complexity:</div>
                    <div>
                        <span style="background-color: {"#A5D6A7" if complexity == "Low" else "#FFE082" if complexity == "Medium" else "#FFAB91"}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">{complexity}</span>
                    </div>
                </div>
                
                <div style="display: flex; margin-bottom: 15px;">
                    <div style="width: 120px; font-weight: bold; color: #555;">User Impact:</div>
                    <div>
                        <span style="background-color: {"#90CAF9" if user_impact == "Low" else "#FFB74D" if user_impact == "Medium" else "#EF5350"}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">{user_impact}</span>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <div style="font-weight: bold; color: #555; margin-bottom: 10px;">Description:</div>
                    <div style="background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid {priority_color};">
                        {description}
                    </div>
                </div>
    '''
    
    # Add benefits if available
    if benefits:
        feature_html += '''
                <div style="margin-top: 20px;">
                    <div style="font-weight: bold; color: #555; margin-bottom: 10px;">Key Benefits:</div>
                    <ul style="margin-top: 5px; padding-left: 20px;">
        '''
        
        for benefit in benefits:
            feature_html += f'<li style="margin-bottom: 8px;">{benefit}</li>'
        
        feature_html += '''
                    </ul>
                </div>
        '''
    
    # Add implementation considerations if available
    if considerations:
        feature_html += '''
                <div style="margin-top: 20px;">
                    <div style="font-weight: bold; color: #555; margin-bottom: 10px;">Implementation Considerations:</div>
                    <ul style="margin-top: 5px; padding-left: 20px;">
        '''
        
        for consideration in considerations:
            feature_html += f'<li style="margin-bottom: 8px;">{consideration}</li>'
        
        feature_html += '''
                    </ul>
                </div>
        '''
    
    # Close the HTML
    feature_html += '''
            </div>
        </div>
    </div>
    '''
    
    # Use components.html for the feature details
    components.html(feature_html, height=500)

def render_sample_feature_details():
    """
    Render a sample feature detail for demonstration purposes
    """
    sample_feature = {
        "name": "Dark Mode Implementation",
        "description": "Implement a dark mode option for the application to reduce eye strain during night-time usage and provide a modern UI option that many users have requested. The implementation should include a toggle in the settings menu and persist the user's preference across sessions.",
        "priority": "High",
        "complexity": "Medium",
        "user_impact": "High",
        "benefits": [
            "Reduces eye strain in low-light environments",
            "Improves battery life on OLED/AMOLED screens",
            "Addresses one of the most requested features from user feedback",
            "Provides a modern aesthetic option for users"
        ],
        "considerations": [
            "Create a comprehensive dark theme CSS",
            "Ensure all UI elements have appropriate contrast ratios",
            "Add theme toggle in settings with auto-detection option",
            "Store user preference in local storage"
        ]
    }
    
    render_feature_details(sample_feature)
