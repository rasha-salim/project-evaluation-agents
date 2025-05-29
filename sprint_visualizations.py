import streamlit.components.v1 as components
import re

def render_sprint_plan_visualization(sprint_plan_text):
    """
    Create visualizations for the sprint plan tab
    
    Args:
        sprint_plan_text: The sprint plan text from the AI
    """
    # Extract sprints and tasks
    sprints, tasks = extract_sprint_data(sprint_plan_text)
    
    # If no data was extracted, use sample data for demonstration
    if not sprints or not tasks:
        sprints, tasks = get_sample_sprint_data()
    
    # Create a sprint timeline visualization
    timeline_html = create_sprint_timeline(sprints, tasks)
    components.html(timeline_html, height=400)
    
    # Create a sprint summary table
    table_html = create_sprint_summary_table(sprints)
    components.html(table_html, height=300)

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

def get_sample_sprint_data():
    """Provide sample sprint data when extraction fails"""
    sprints = [
        {
            "Sprint": 1,
            "Description": "Core UI Improvements",
            "Tasks": 2
        },
        {
            "Sprint": 2,
            "Description": "Performance Optimization",
            "Tasks": 2
        },
        {
            "Sprint": 3,
            "Description": "Advanced Features",
            "Tasks": 3
        }
    ]
    
    tasks = [
        {
            "Task": "Implement Dark Mode",
            "Sprint": "Sprint 1",
            "Start": 1,
            "Duration": 5,
            "Resource": "UI Team"
        },
        {
            "Task": "Improve Search Functionality",
            "Sprint": "Sprint 1",
            "Start": 2,
            "Duration": 7,
            "Resource": "Backend Team"
        },
        {
            "Task": "Performance Optimization",
            "Sprint": "Sprint 2",
            "Start": 11,
            "Duration": 5,
            "Resource": "Core Team"
        },
        {
            "Task": "User Preferences",
            "Sprint": "Sprint 2",
            "Start": 12,
            "Duration": 4,
            "Resource": "UI Team"
        },
        {
            "Task": "File Upload System",
            "Sprint": "Sprint 3",
            "Start": 21,
            "Duration": 8,
            "Resource": "Backend Team"
        },
        {
            "Task": "Analytics Dashboard",
            "Sprint": "Sprint 3",
            "Start": 22,
            "Duration": 7,
            "Resource": "Data Team"
        },
        {
            "Task": "Notification System",
            "Sprint": "Sprint 3",
            "Start": 23,
            "Duration": 5,
            "Resource": "UI Team"
        }
    ]
    
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
    html = '''
    <div style="margin-top: 20px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Sprint Summary</h3>
        <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <thead>
                <tr style="background-color: #673AB7; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Sprint</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Tasks</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Description</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    # Sort sprints by number
    sorted_sprints = sorted(sprints, key=lambda x: x["Sprint"])
    
    for sprint in sorted_sprints:
        html += f'''
        <tr style="background-color: #f9f9f9;">
            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">Sprint {sprint["Sprint"]}</td>
            <td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{sprint["Tasks"]}</td>
            <td style="padding: 12px; text-align: left; border: 1px solid #ddd;">{sprint["Description"]}</td>
        </tr>
        '''
    
    html += '''
            </tbody>
        </table>
        </div>
    </div>
    '''
    
    return html
