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
