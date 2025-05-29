import streamlit.components.v1 as components
import re

def render_stakeholder_update_visualization(update_text):
    """
    Create visualizations for the stakeholder update tab
    
    Args:
        update_text: The stakeholder update text from the AI
    """
    # Extract key metrics and progress data
    metrics = extract_metrics(update_text)
    
    # If no data was extracted, use sample data for demonstration
    if not metrics or metrics['total_features'] == 0:
        metrics = get_sample_metrics()
    
    # Create a progress overview visualization
    progress_html = create_progress_overview(metrics)
    components.html(progress_html, height=400)
    
    # Create a key achievements visualization
    achievements_html = create_achievements_visualization(update_text, metrics)
    components.html(achievements_html, height=350)
    

def get_sample_metrics():
    """Provide sample metrics when extraction fails"""
    return {
        'completed_features': 4,
        'in_progress_features': 3,
        'planned_features': 3,
        'total_features': 10,
        'completion_percentage': 40,
        'key_achievements': [
            'Completed Dark Mode implementation',
            'Improved search functionality with partial matching',
            'Fixed critical performance issues on large files',
            'Added user preference storage'
        ],
        'challenges': [
            'File upload system complexity is higher than anticipated',
            'Battery optimization requires additional testing',
            'Integration with legacy systems taking longer than expected'
        ],
        'next_steps': [
            'Complete file upload system implementation',
            'Begin work on analytics dashboard',
            'Implement notification system improvements',
            'Start planning for custom themes feature'
        ]
    }

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
    
    # Try to find completion percentage
    completion_pattern = r'(?:completion|progress|completed).*?(\d+)%'
    completion_match = re.search(completion_pattern, text, re.IGNORECASE)
    if completion_match:
        metrics['completion_percentage'] = int(completion_match.group(1))
    
    # Try to find feature counts
    completed_pattern = r'(\d+)(?:\s+|\s*,\s*)(?:features?|tasks?|items?|stories?|work\s+items?)(?:\s+|\s*,\s*)(?:have\s+been\s+|were\s+|are\s+)?completed'
    completed_match = re.search(completed_pattern, text, re.IGNORECASE)
    if completed_match:
        metrics['completed_features'] = int(completed_match.group(1))
    
    in_progress_pattern = r'(\d+)(?:\s+|\s*,\s*)(?:features?|tasks?|items?|stories?|work\s+items?)(?:\s+|\s*,\s*)(?:are\s+|currently\s+|in\s+|being\s+)?(?:in\s+progress|ongoing|underway)'
    in_progress_match = re.search(in_progress_pattern, text, re.IGNORECASE)
    if in_progress_match:
        metrics['in_progress_features'] = int(in_progress_match.group(1))
    
    planned_pattern = r'(\d+)(?:\s+|\s*,\s*)(?:features?|tasks?|items?|stories?|work\s+items?)(?:\s+|\s*,\s*)(?:are\s+|have\s+been\s+)?planned'
    planned_match = re.search(planned_pattern, text, re.IGNORECASE)
    if planned_match:
        metrics['planned_features'] = int(planned_match.group(1))
    
    total_pattern = r'(?:total\s+of\s+)?(\d+)(?:\s+|\s*,\s*)(?:features?|tasks?|items?|stories?|work\s+items?)(?:\s+|\s*,\s*)?(?:in\s+total|total|overall)'
    total_match = re.search(total_pattern, text, re.IGNORECASE)
    if total_match:
        metrics['total_features'] = int(total_match.group(1))
    else:
        # Calculate total from other metrics
        metrics['total_features'] = metrics['completed_features'] + metrics['in_progress_features'] + metrics['planned_features']
    
    # If we still don't have a completion percentage, calculate it
    if metrics['completion_percentage'] == 0 and metrics['total_features'] > 0:
        metrics['completion_percentage'] = int((metrics['completed_features'] / metrics['total_features']) * 100)
    
    # Extract key achievements
    achievements_section = re.search(r'(?:Key\s+Achievements|Accomplishments|Progress|Highlights)(?:[\s:\-]+)([^#]+?)(?:(?:Key\s+)?(?:Challenges|Issues|Blockers|Risks)|(?:Next\s+Steps)|$)', 
                                    text, re.IGNORECASE | re.DOTALL)
    if achievements_section:
        achievement_text = achievements_section.group(1).strip()
        # Look for bullet points or numbered items
        achievements = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-|\•)\s*([^\n]+)', achievement_text)
        if achievements:
            metrics['key_achievements'] = [a.strip() for a in achievements]
        else:
            # Split by sentences if no bullet points found
            sentences = re.split(r'(?<=[.!?])\s+', achievement_text)
            metrics['key_achievements'] = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Extract challenges
    challenges_section = re.search(r'(?:Key\s+)?(?:Challenges|Issues|Blockers|Risks)(?:[\s:\-]+)([^#]+?)(?:(?:Next\s+Steps)|$)', 
                                 text, re.IGNORECASE | re.DOTALL)
    if challenges_section:
        challenge_text = challenges_section.group(1).strip()
        # Look for bullet points or numbered items
        challenges = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-|\•)\s*([^\n]+)', challenge_text)
        if challenges:
            metrics['challenges'] = [c.strip() for c in challenges]
        else:
            # Split by sentences if no bullet points found
            sentences = re.split(r'(?<=[.!?])\s+', challenge_text)
            metrics['challenges'] = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Extract next steps
    next_steps_section = re.search(r'(?:Next\s+Steps|Future\s+Work|Upcoming|Roadmap)(?:[\s:\-]+)([^#]+?)(?:$)', 
                                 text, re.IGNORECASE | re.DOTALL)
    if next_steps_section:
        next_steps_text = next_steps_section.group(1).strip()
        # Look for bullet points or numbered items
        next_steps = re.findall(r'(?:^|\n)(?:\d+\.|\*|\-|\•)\s*([^\n]+)', next_steps_text)
        if next_steps:
            metrics['next_steps'] = [n.strip() for n in next_steps]
        else:
            # Split by sentences if no bullet points found
            sentences = re.split(r'(?<=[.!?])\s+', next_steps_text)
            metrics['next_steps'] = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    return metrics

def create_progress_overview(metrics):
    """Create a progress overview visualization"""
    # Calculate percentages for the chart
    completed_percent = metrics['completed_features'] / max(metrics['total_features'], 1) * 100
    in_progress_percent = metrics['in_progress_features'] / max(metrics['total_features'], 1) * 100
    planned_percent = metrics['planned_features'] / max(metrics['total_features'], 1) * 100
    
    # Create the HTML for the progress overview
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Project Progress Overview</h3>
        
        <!-- Progress Circle -->
        <div style="display: flex; flex-wrap: wrap; align-items: center; margin-top: 20px;">
            <div style="flex: 0 0 200px; position: relative; margin: 0 auto;">
                <svg width="200" height="200" viewBox="0 0 200 200">
                    <!-- Background circle -->
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="15"/>
                    
                    <!-- Progress circle -->
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#4CAF50" stroke-width="15"
                            stroke-dasharray="565.48" stroke-dashoffset="''' + str(565.48 - (565.48 * metrics['completion_percentage'] / 100)) + '''"
                            transform="rotate(-90 100 100)"/>
                            
                    <!-- Percentage text -->
                    <text x="100" y="100" text-anchor="middle" dominant-baseline="middle" font-size="36" font-weight="bold" fill="#333">
                        ''' + str(metrics['completion_percentage']) + '''%
                    </text>
                    <text x="100" y="130" text-anchor="middle" dominant-baseline="middle" font-size="14" fill="#666">
                        Complete
                    </text>
                </svg>
            </div>
            
            <!-- Feature Status Breakdown -->
            <div style="flex: 1; min-width: 300px; margin-left: 20px;">
                <div style="margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #333; margin-bottom: 15px;">Feature Status</h4>
                    
                    <!-- Completed Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">Completed</div>
                            <div>''' + str(metrics['completed_features']) + ''' of ''' + str(metrics['total_features']) + '''</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: ''' + str(completed_percent) + '''%; height: 100%; background-color: #4CAF50;"></div>
                        </div>
                    </div>
                    
                    <!-- In Progress Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">In Progress</div>
                            <div>''' + str(metrics['in_progress_features']) + ''' of ''' + str(metrics['total_features']) + '''</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: ''' + str(in_progress_percent) + '''%; height: 100%; background-color: #2196F3;"></div>
                        </div>
                    </div>
                    
                    <!-- Planned Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">Planned</div>
                            <div>''' + str(metrics['planned_features']) + ''' of ''' + str(metrics['total_features']) + '''</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: ''' + str(planned_percent) + '''%; height: 100%; background-color: #FF9800;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return html

def create_achievements_visualization(text, metrics=None):
    """Create a visualization for key achievements, challenges, and next steps"""
    if metrics is None:
        metrics = extract_metrics(text)
    
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
    '''
    
    # Key Achievements section
    if metrics['key_achievements']:
        html += '''
        <div style="flex: 1; min-width: 300px; background-color: #E8F5E9; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 8px;">Key Achievements</h3>
            <ul style="margin-top: 10px; padding-left: 20px;">
        '''
        
        for achievement in metrics['key_achievements'][:5]:  # Limit to 5 achievements
            html += f'''
            <li style="margin-bottom: 10px;">{achievement}</li>
            '''
            
        html += '''
            </ul>
        </div>
        '''
    
    # Challenges section
    if metrics['challenges']:
        html += '''
        <div style="flex: 1; min-width: 300px; background-color: #FFF3E0; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #E65100; border-bottom: 2px solid #E65100; padding-bottom: 8px;">Challenges</h3>
            <ul style="margin-top: 10px; padding-left: 20px;">
        '''
        
        for challenge in metrics['challenges'][:5]:  # Limit to 5 challenges
            html += f'''
            <li style="margin-bottom: 10px;">{challenge}</li>
            '''
            
        html += '''
            </ul>
        </div>
        '''
    
    # Next Steps section
    if metrics['next_steps']:
        html += '''
        <div style="flex: 1; min-width: 300px; background-color: #E3F2FD; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #1565C0; border-bottom: 2px solid #1565C0; padding-bottom: 8px;">Next Steps</h3>
            <ul style="margin-top: 10px; padding-left: 20px;">
        '''
        
        for step in metrics['next_steps'][:5]:  # Limit to 5 next steps
            html += f'''
            <li style="margin-bottom: 10px;">{step}</li>
            '''
            
        html += '''
            </ul>
        </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html
