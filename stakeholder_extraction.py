"""
Stakeholder update extraction module for Project Evolution Agents.
Uses LLM to extract structured stakeholder update data from stakeholder update text.
"""
import re
from direct_agents.agent import Agent
from direct_agents.task import Task
import streamlit.components.v1 as components
import streamlit as st

def extract_stakeholder_update_with_llm(stakeholder_update_text, user_priority_focus=None):
    """
    Use the AI agent to extract structured stakeholder update data
    
    Args:
        stakeholder_update_text (str): Raw stakeholder update text from the AI
        user_priority_focus (str, optional): User's priority focus from collaboration step
        
    Returns:
        dict: Dictionary with stakeholder update data including highlights, risks, and next steps
    """
    # Extract user priority focus if present in the text but not provided as parameter
    if not user_priority_focus and isinstance(stakeholder_update_text, str):
        priority_match = re.search(r"PRIORITY ADJUSTMENT:\s*(.+?)(?:\n|$)", stakeholder_update_text)
        if priority_match:
            user_priority_focus = priority_match.group(1).strip()
    
    # Create a stakeholder update extraction agent
    update_extractor = Agent(
        role="Stakeholder Communication Specialist",
        goal="Extract structured stakeholder update data",
        backstory="You are an expert in analyzing stakeholder updates and extracting key information for executive presentations.",
        verbose=False
    )
    
    # Adjust the task description based on whether there's a user priority focus
    priority_instruction = ""
    if user_priority_focus:
        priority_instruction = "\n\nIMPORTANT: The user has requested to " + user_priority_focus + ". Identify which highlights, metrics, next steps, and resources align with this priority focus by marking them with an asterisk (*) at the beginning of each item."
    
    # Create the task description
    task_description = """Extract structured stakeholder update data from the following text.
Identify:
1. Project highlights/achievements
2. Key metrics and progress indicators
3. Risks and challenges
4. Next steps and recommendations
5. Resource needs or requests"""
    
    # Add priority instruction if needed
    task_description += priority_instruction
    
    # Add format instructions
    task_description += """

Format your response exactly as follows:

HIGHLIGHTS:
- [highlight 1]
- [highlight 2]
...

METRICS:
- [metric 1]: [value/status]
- [metric 2]: [value/status]
...

RISKS:
- [risk 1]: [impact level - High/Medium/Low]
- [risk 2]: [impact level - High/Medium/Low]
...

NEXT STEPS:
- [next step 1]
- [next step 2]
...

RESOURCES:
- [resource need 1]
- [resource need 2]
...

PRIORITY FOCUS SUMMARY:
[A brief summary of how the stakeholder update addresses the user's priority focus]

Here's the stakeholder update text to analyze:
"""
    
    # Add the actual stakeholder update text
    task_description += stakeholder_update_text
    
    # Create a task for the agent to extract stakeholder update data
    extraction_task = Task(
        description=task_description,
        agent=update_extractor,
        expected_output="Structured stakeholder update data"
    )
    
    # Execute the task
    result = extraction_task.execute()
    
    # Parse the result to extract stakeholder update data
    update_data = {
        'highlights': [],
        'metrics': [],
        'risks': [],
        'next_steps': [],
        'resources': []
    }
    
    # Add priority tracking if user priority focus exists
    has_priority_focus = user_priority_focus is not None
    if has_priority_focus:
        update_data['priority_highlights'] = []
        update_data['priority_metrics'] = []
        update_data['priority_risks'] = []
        update_data['priority_next_steps'] = []
        update_data['priority_resources'] = []
        update_data['priority_focus_summary'] = ''
        update_data['user_priority_focus'] = user_priority_focus
    
    current_section = None
    
    for line in result.split('\n'):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check for section headers
        if line.endswith(':'):
            section = line.lower().rstrip(':').strip()
            if section == 'highlights':
                current_section = 'highlights'
            elif section == 'metrics':
                current_section = 'metrics'
            elif section == 'risks':
                current_section = 'risks'
            elif section in ['next steps', 'next_steps']:
                current_section = 'next_steps'
            elif section == 'resources':
                current_section = 'resources'
            elif has_priority_focus and section in ['priority focus summary', 'priority_focus_summary']:
                current_section = 'priority_focus_summary'
            else:
                current_section = None
            continue
            
        # Add items to the appropriate section
        if current_section and line.startswith('-'):
            item = line[1:].strip()
            if item:
                # Check if this is a priority item (marked with *)
                is_priority = False
                if has_priority_focus and item.startswith('*'):
                    is_priority = True
                    item = item[1:].strip()
                
                # Add to regular section
                update_data[current_section].append(item)
                
                # If it's a priority item, also add to priority section
                if has_priority_focus and is_priority and current_section != 'priority_focus_summary':
                    priority_section = f'priority_{current_section}'
                    update_data[priority_section].append(item)
        
        # Handle priority focus summary (not a list item)
        elif current_section == 'priority_focus_summary' and has_priority_focus:
            if update_data['priority_focus_summary']:
                update_data['priority_focus_summary'] += '\n' + line
            else:
                update_data['priority_focus_summary'] = line
    
    # If no data was found, use regex as fallback
    if not any([update_data['highlights'], update_data['metrics'], update_data['risks'], 
                update_data['next_steps'], update_data['resources']]):
        return extract_stakeholder_update_with_regex(stakeholder_update_text)
    
    return update_data

def extract_stakeholder_update_with_regex(stakeholder_update_text):
    """
    Fallback method to extract stakeholder update data using regex
    
    Args:
        stakeholder_update_text (str): Raw stakeholder update text
        
    Returns:
        dict: Dictionary with stakeholder update data
    """
    highlights = []
    metrics = []
    risks = []
    next_steps = []
    resources = []
    
    # Extract highlights
    highlights_section = re.search(r'(?:highlights?|achievements?|accomplishments?)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                 stakeholder_update_text, re.IGNORECASE)
    if highlights_section:
        highlights = [h.strip() for h in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', highlights_section.group(1))]
    
    # Extract metrics
    metrics_section = re.search(r'(?:metrics|progress|status)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                              stakeholder_update_text, re.IGNORECASE)
    if metrics_section:
        metrics = [m.strip() for m in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', metrics_section.group(1))]
    
    # Extract risks
    risks_section = re.search(r'(?:risks?|challenges?|issues?)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                            stakeholder_update_text, re.IGNORECASE)
    if risks_section:
        risk_items = [r.strip() for r in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', risks_section.group(1))]
        for item in risk_items:
            impact = 'Medium'  # Default
            if 'high' in item.lower() or 'critical' in item.lower() or 'severe' in item.lower():
                impact = 'High'
            elif 'low' in item.lower() or 'minor' in item.lower():
                impact = 'Low'
            risks.append({'text': item, 'impact': impact})
    
    # Extract next steps
    next_steps_section = re.search(r'(?:next steps?|recommendations?|future|plan)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                 stakeholder_update_text, re.IGNORECASE)
    if next_steps_section:
        next_steps = [s.strip() for s in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', next_steps_section.group(1))]
    
    # Extract resources
    resources_section = re.search(r'(?:resources?|needs?|requests?)[:\n]+((?:(?:\*|\-|\d+\.)[^\n]+\n?)+)', 
                                stakeholder_update_text, re.IGNORECASE)
    if resources_section:
        resources = [r.strip() for r in re.findall(r'(?:\*|\-|\d+\.)\s*([^\n]+)', resources_section.group(1))]
    
    return {
        'highlights': highlights,
        'metrics': metrics,
        'risks': risks,
        'next_steps': next_steps,
        'resources': resources
    }

def render_stakeholder_update(update_data):
    """
    Render stakeholder update visualizations
    
    Args:
        update_data (dict): Stakeholder update data from LLM extraction
    """
    # Render highlights
    render_highlights(update_data['highlights'])
    
    # Render risks
    render_risks(update_data['risks'])
    
    # Render next steps and resources
    render_action_items(update_data['next_steps'], update_data['resources'])

def render_highlights(highlights):
    """Render project highlights"""
    if not highlights:
        return
        
    # Create HTML for highlights
    html = '''
    <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid #4CAF50;">
        <h3 style="margin-top: 0; color: #333;">Project Highlights</h3>
        <ul style="padding-left: 20px;">
    '''
    
    for highlight in highlights:
        html += f'''
        <li style="margin-bottom: 8px;">
            <span style="color: #4CAF50;">✓</span> {highlight}
        </li>
        '''
    
    html += '''
        </ul>
    </div>
    '''
    
    # Display the HTML
    components.html(html, height=50 + len(highlights) * 40)

def render_risks(risks):
    """Render project risks and challenges"""
    if not risks:
        return
        
    # Create HTML for risks
    html = '''
    <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid #F44336;">
        <h3 style="margin-top: 0; color: #333;">Risks & Challenges</h3>
        <ul style="padding-left: 20px;">
    '''
    
    for risk in risks:
        risk_text = risk['text'] if isinstance(risk, dict) else risk
        impact = risk.get('impact', 'Medium') if isinstance(risk, dict) else 'Medium'
        
        # Determine color based on impact
        color = '#F44336' if impact == 'High' else '#FF9800' if impact == 'Medium' else '#2196F3'
        
        html += f'''
        <li style="margin-bottom: 8px; display: flex; align-items: baseline;">
            <span style="color: {color}; margin-right: 5px;">⚠</span>
            <div>
                <span>{risk_text}</span>
                <span style="margin-left: 5px; padding: 2px 6px; background-color: {color}; color: white; border-radius: 10px; font-size: 0.8em;">{impact}</span>
            </div>
        </li>
        '''
    
    html += '''
        </ul>
    </div>
    '''
    
    # Display the HTML
    components.html(html, height=50 + len(risks) * 50)

def render_action_items(next_steps, resources):
    """Render next steps and resource needs"""
    # Create HTML for action items
    html = '''
    <div style="margin: 20px 0; display: flex; flex-wrap: wrap; gap: 20px;">
    '''
    
    # Next steps section
    if next_steps:
        html += '''
        <div style="flex: 1; min-width: 300px; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid #2196F3;">
            <h3 style="margin-top: 0; color: #333;">Next Steps</h3>
            <ul style="padding-left: 20px;">
        '''
        
        for step in next_steps:
            html += f'''
            <li style="margin-bottom: 8px;">
                <span style="color: #2196F3;">→</span> {step}
            </li>
            '''
        
        html += '''
            </ul>
        </div>
        '''
    
    # Resources section
    if resources:
        html += '''
        <div style="flex: 1; min-width: 300px; padding: 15px; background-color: #f5f5f5; border-radius: 8px; border-left: 5px solid #9C27B0;">
            <h3 style="margin-top: 0; color: #333;">Resource Needs</h3>
            <ul style="padding-left: 20px;">
        '''
        
        for resource in resources:
            html += f'''
            <li style="margin-bottom: 8px;">
                <span style="color: #9C27B0;">•</span> {resource}
            </li>
            '''
        
        html += '''
            </ul>
        </div>
        '''
    
    html += '</div>'
    
    # Display the HTML
    components.html(html, height=100 + max(len(next_steps), len(resources)) * 30)
