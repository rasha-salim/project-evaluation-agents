import streamlit.components.v1 as components
import re

def render_feedback_analysis_visualization(feedback_analysis_text, raw_feedback=None):
    """
    Create visualizations for the feedback analysis tab
    
    Args:
        feedback_analysis_text: The feedback analysis text from the AI
        raw_feedback: Optional raw feedback data to analyze if extraction fails
    """
    # Import the sample feedback if raw_feedback is not provided
    if not raw_feedback:
        try:
            # Try to import the sample feedback from direct_app.py
            from direct_app import SAMPLE_FEEDBACK
            raw_feedback = SAMPLE_FEEDBACK
        except ImportError:
            # If import fails, use None (will fall back to sample data)
            pass
    
    # First try to use the LLM to analyze the raw feedback directly
    categories = None
    sentiment = None
    
    if raw_feedback:
        try:
            # Use the LLM to analyze the raw feedback directly
            llm_categories, llm_sentiment = analyze_feedback_with_llm(raw_feedback)
            if llm_categories and sum(llm_sentiment.values()) == 100:
                categories = llm_categories
                sentiment = llm_sentiment
        except Exception as e:
            print(f"Error using LLM for feedback analysis: {str(e)}")
    
    # If LLM analysis failed, fall back to regex extraction
    if not categories or not sentiment:
        categories, sentiment = extract_feedback_data(feedback_analysis_text, raw_feedback)
    
    # Create a bar chart for categories
    category_html = create_category_bars(categories)
    components.html(category_html, height=len(categories) * 50 + 100)
    
    # Create a sentiment analysis visualization with increased height
    sentiment_html = create_sentiment_bars(sentiment)
    components.html(sentiment_html, height=200)  # Increased height for better visibility

def extract_feedback_data(text, raw_feedback=None):
    """Extract categories and sentiment from feedback analysis text
    
    Args:
        text: Feedback analysis text
        raw_feedback: Optional raw feedback data to analyze if extraction fails
        
    Returns:
        tuple: (categories, sentiment)
    """
    # Initialize with default values
    categories = []
    sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    # Get default sentiment values
    default_sentiment = get_default_sentiment()
    default_percentages = [default_sentiment['positive'], default_sentiment['neutral'], default_sentiment['negative']]
    
    # Try to extract categories
    category_pattern = r'(?:Category|Theme|Topic|Area|Issue)\s*(?:\d+)?\s*[:\-]\s*([^\n]+)\s*\(?(?:(\d+)\s*(?:mentions|comments|occurrences|%|percent)?)?\)?'
    category_matches = re.findall(category_pattern, text, re.IGNORECASE)
    
    for match in category_matches:
        category_name = match[0].strip()
        try:
            count = int(match[1]) if len(match) > 1 and match[1].isdigit() else 1
            categories.append({"category": category_name, "count": count})
        except (IndexError, ValueError):
            categories.append({"category": category_name, "count": 1})
    
    # Try to extract sentiment percentages
    positive_pattern = r'(?:Positive|Favorable)\s*(?:sentiment|feedback)?\s*[:\-]?\s*(\d+)\s*(?:%|percent)'
    neutral_pattern = r'(?:Neutral|Balanced)\s*(?:sentiment|feedback)?\s*[:\-]?\s*(\d+)\s*(?:%|percent)'
    negative_pattern = r'(?:Negative|Critical|Unfavorable)\s*(?:sentiment|feedback)?\s*[:\-]?\s*(\d+)\s*(?:%|percent)'
    
    positive_match = re.search(positive_pattern, text, re.IGNORECASE)
    neutral_match = re.search(neutral_pattern, text, re.IGNORECASE)
    negative_match = re.search(negative_pattern, text, re.IGNORECASE)
    
    if positive_match and neutral_match and negative_match:
        sentiment['positive'] = int(positive_match.group(1))
        sentiment['neutral'] = int(neutral_match.group(1))
        sentiment['negative'] = int(negative_match.group(1))
    else:
        sentiment['positive'] = default_percentages[0]
        sentiment['neutral'] = default_percentages[1]
        sentiment['negative'] = default_percentages[2]
    
    # If extraction failed and we have raw feedback, use LLM to analyze it
    if (not categories or all(v == 0 for v in sentiment.values())) and raw_feedback:
        try:
            # Use the LLM to analyze the raw feedback
            llm_categories, llm_sentiment = analyze_feedback_with_llm(raw_feedback)
            
            # Use LLM results if available
            if not categories and llm_categories:
                categories = llm_categories
            
            if (all(v == 0 for v in sentiment.values()) or sentiment['positive'] == default_percentages[0]) and sum(llm_sentiment.values()) == 100:
                sentiment = llm_sentiment
        except Exception as e:
            print(f"Error using LLM for feedback analysis: {str(e)}")
            # If LLM analysis fails, use default categories
            if not categories:
                categories = get_default_categories()
    # If extraction failed and no raw feedback is provided, use default categories
    elif not categories:
        categories = get_default_categories()
    
    return categories, sentiment

def analyze_feedback_with_llm(feedback_text):
    """Use the AI agent to analyze feedback data for categories and sentiment
    
    Args:
        feedback_text (str): Raw feedback data
        
    Returns:
        tuple: (categories, sentiment)
    """
    from direct_agents.agent import Agent
    from direct_agents.task import Task
    
    # Create a feedback analysis agent
    feedback_analyst = Agent(
        role="Feedback Analyst",
        goal="Analyze user feedback to identify patterns, priorities, and insights",
        backstory="You are an expert in data analysis with a focus on user feedback. You excel at identifying patterns and extracting actionable insights from user comments.",
        verbose=False
    )
    
    # Define the standard categories we want to use
    standard_categories = [
        "UI/UX Issues", 
        "Performance Problems", 
        "Feature Requests", 
        "Usability Concerns", 
        "Documentation Needs"
    ]
    
    # Create a task for the agent to analyze the feedback
    analysis_task = Task(
        description=f"""Analyze the following user feedback and provide:
1. Count how many comments fall into each of these categories: {', '.join(standard_categories)}. A comment can belong to multiple categories.
2. Calculate the sentiment percentage (positive, neutral, negative) across all comments.

Format your response exactly as follows:

CATEGORIES:
UI/UX Issues: [count]
Performance Problems: [count]
Feature Requests: [count]
Usability Concerns: [count]
Documentation Needs: [count]

SENTIMENT:
Positive: [percentage]%
Neutral: [percentage]%
Negative: [percentage]%

Here's the feedback to analyze:
{feedback_text}""",
        agent=feedback_analyst,
        expected_output="Categorized feedback counts and sentiment percentages"
    )
    
    # Execute the task
    result = analysis_task.execute()
    
    # Parse the result to extract categories and sentiment
    categories = []
    sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    # Extract categories
    category_pattern = r'([\w\s/]+):\s*(\d+)'
    category_section = False
    sentiment_section = False
    
    for line in result.split('\n'):
        if 'CATEGORIES:' in line:
            category_section = True
            sentiment_section = False
            continue
        elif 'SENTIMENT:' in line:
            category_section = False
            sentiment_section = True
            continue
        
        if category_section:
            category_match = re.search(category_pattern, line)
            if category_match:
                category_name = category_match.group(1).strip()
                count = int(category_match.group(2))
                if count > 0:  # Only include categories with counts > 0
                    categories.append({"category": category_name, "count": count})
        
        if sentiment_section:
            if 'Positive:' in line:
                match = re.search(r'Positive:\s*(\d+)%', line)
                if match:
                    sentiment['positive'] = int(match.group(1))
            elif 'Neutral:' in line:
                match = re.search(r'Neutral:\s*(\d+)%', line)
                if match:
                    sentiment['neutral'] = int(match.group(1))
            elif 'Negative:' in line:
                match = re.search(r'Negative:\s*(\d+)%', line)
                if match:
                    sentiment['negative'] = int(match.group(1))
    
    # Sort categories by count in descending order
    categories = sorted(categories, key=lambda x: x["count"], reverse=True)
    
    # If no categories were found, use default categories
    if not categories:
        categories = get_default_categories()
    
    # If sentiment doesn't add up to 100%, use default sentiment
    if sum(sentiment.values()) != 100:
        sentiment = get_default_sentiment()
    
    return categories, sentiment

def get_default_categories():
    """Provide default empty categories with the standard structure"""
    return [
        {"category": "UI/UX Issues", "count": 0},
        {"category": "Performance Problems", "count": 0},
        {"category": "Feature Requests", "count": 0},
        {"category": "Usability Concerns", "count": 0},
        {"category": "Documentation Needs", "count": 0}
    ]

def get_default_sentiment():
    """Provide balanced default sentiment when analysis fails"""
    return {
        'positive': 33,
        'neutral': 34,
        'negative': 33
    }

# This function has been removed as we now use the LLM for sentiment analysis

def get_sample_sentiment():
    """Provide sample sentiment when extraction fails"""
    return {
        'positive': 40,
        'neutral': 35,
        'negative': 25
    }

def create_category_bars(categories):
    """Create bar chart for feedback categories"""
    # Calculate max count for percentage calculation
    max_count = max([c["count"] for c in categories])
    
    # Define colors for bars
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#607D8B"]
    
    # Create HTML for the bar chart
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Feedback Categories</h3>
    '''
    
    # Add bars
    for i, cat in enumerate(categories):
        percentage = (cat["count"] / max_count) * 100
        color = colors[i % len(colors)]
        
        html += f'''
        <div style="margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 150px; text-align: right; padding-right: 15px; font-weight: 500;">{cat["category"]}</div>
                <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                    <div style="width: {percentage}%; height: 100%; background-color: {color}; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: 500;">{cat["count"]}</div>
                </div>
            </div>
        </div>
        '''
    
    html += "</div>"
    
    return html

def create_sentiment_bars(sentiment):
    """Create sentiment analysis bars"""
    html = '''
    <div style="margin-top: 20px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Sentiment Analysis</h3>
    '''
    
    # Positive
    html += f'''
    <div style="display: flex; align-items: center; margin-top: 15px;">
        <div style="width: 120px; text-align: right; padding-right: 10px;">Positive ({sentiment['positive']}%)</div>
        <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
            <div style="width: {sentiment['positive']}%; height: 100%; background-color: #4CAF50;"></div>
        </div>
    </div>
    '''
    
    # Neutral
    html += f'''
    <div style="display: flex; align-items: center; margin-top: 10px;">
        <div style="width: 120px; text-align: right; padding-right: 10px;">Neutral ({sentiment['neutral']}%)</div>
        <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
            <div style="width: {sentiment['neutral']}%; height: 100%; background-color: #2196F3;"></div>
        </div>
    </div>
    '''
    
    # Negative
    html += f'''
    <div style="display: flex; align-items: center; margin-top: 10px;">
        <div style="width: 120px; text-align: right; padding-right: 10px;">Negative ({sentiment['negative']}%)</div>
        <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
            <div style="width: {sentiment['negative']}%; height: 100%; background-color: #F44336;"></div>
        </div>
    </div>
    '''
    
    html += "</div>"
    
    return html

def create_feedback_trends_graph(categories, sentiment):
    """Create a feedback trends graph visualization"""
    # Create a scatter plot showing category count vs sentiment impact
    html = '''
    <div style="margin-top: 30px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Feedback Impact Analysis</h3>
        
        <div style="position: relative; width: 100%; height: 300px; margin-top: 20px; border: 1px solid #ddd; border-radius: 8px; padding: 10px;">
            <!-- Y-axis label -->
            <div style="position: absolute; left: -40px; top: 50%; transform: translateY(-50%) rotate(-90deg); font-weight: 500; color: #555;">Impact Severity</div>
            
            <!-- X-axis label -->
            <div style="position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%); font-weight: 500; color: #555;">Mention Frequency</div>
            
            <!-- Y-axis -->
            <div style="position: absolute; left: 50px; top: 20px; bottom: 50px; width: 1px; background-color: #aaa;"></div>
            
            <!-- X-axis -->
            <div style="position: absolute; left: 50px; right: 20px; bottom: 50px; height: 1px; background-color: #aaa;"></div>
            
            <!-- Y-axis ticks -->
            <div style="position: absolute; left: 45px; top: 20px; width: 10px; height: 1px; background-color: #aaa;"></div>
            <div style="position: absolute; left: 35px; top: 20px; font-size: 12px; color: #777;">High</div>
            
            <div style="position: absolute; left: 45px; top: 50%; width: 10px; height: 1px; background-color: #aaa;"></div>
            <div style="position: absolute; left: 35px; top: calc(50% - 10px); font-size: 12px; color: #777;">Med</div>
            
            <div style="position: absolute; left: 45px; bottom: 50px; width: 10px; height: 1px; background-color: #aaa;"></div>
            <div style="position: absolute; left: 35px; bottom: 40px; font-size: 12px; color: #777;">Low</div>
            
            <!-- X-axis ticks -->
            <div style="position: absolute; left: 50px; bottom: 45px; width: 1px; height: 10px; background-color: #aaa;"></div>
            <div style="position: absolute; left: 45px; bottom: 30px; font-size: 12px; color: #777;">0</div>
            
            <div style="position: absolute; left: 50%; bottom: 45px; width: 1px; height: 10px; background-color: #aaa;"></div>
            <div style="position: absolute; left: calc(50% - 5px); bottom: 30px; font-size: 12px; color: #777;">5</div>
            
            <div style="position: absolute; right: 20px; bottom: 45px; width: 1px; height: 10px; background-color: #aaa;"></div>
            <div style="position: absolute; right: 15px; bottom: 30px; font-size: 12px; color: #777;">10</div>
    '''
    
    # Calculate the available width and height for plotting
    plot_width = "calc(100% - 70px)"
    plot_height = "calc(100% - 70px)"
    
    # Calculate max count for normalization
    max_count = max([c["count"] for c in categories]) if categories else 10
    
    # Add data points (bubbles)
    for i, category in enumerate(categories):
        # Calculate position based on count and sentiment impact
        # X-position based on count
        x_percent = (category["count"] / max_count) * 100
        
        # Y-position based on sentiment impact (using negative sentiment percentage as a proxy for severity)
        # Higher negative sentiment means higher on the y-axis (more severe)
        severity = sentiment['negative'] / 100
        y_percent = 100 - (severity * 100)
        
        # Bubble size based on total mentions
        bubble_size = 20 + (category["count"] * 5)
        
        # Determine color based on sentiment
        if sentiment['positive'] > sentiment['negative'] + 10:
            color = "#4CAF50"  # Green for positive
        elif sentiment['negative'] > sentiment['positive'] + 10:
            color = "#F44336"  # Red for negative
        else:
            color = "#2196F3"  # Blue for neutral
        
        # Add the bubble
        html += f'''
        <div style="position: absolute; left: calc(50px + {x_percent}% * {plot_width} / 100); top: calc(20px + {y_percent}% * {plot_height} / 100); transform: translate(-50%, -50%); width: {bubble_size}px; height: {bubble_size}px; background-color: {color}80; border: 2px solid {color}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #333; font-weight: 500; font-size: 12px;" title="{category['category']} ({category['count']} mentions)">
            {i+1}
        </div>
        '''
    
    # Add legend
    html += '''
        <div style="position: absolute; top: 20px; right: 20px; background-color: white; border: 1px solid #ddd; border-radius: 4px; padding: 10px;">
            <div style="font-weight: 500; margin-bottom: 5px;">Legend</div>
    '''
    
    # Add legend items for each category
    for i, category in enumerate(categories):
        html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {"#4CAF50" if sentiment['positive'] > sentiment['negative'] + 10 else "#F44336" if sentiment['negative'] > sentiment['positive'] + 10 else "#2196F3"}; margin-right: 5px; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;">{i+1}</div>
                <div style="font-size: 12px;">{category["category"]}</div>
            </div>
        '''
    
    html += '''
        </div>
    </div>
    '''
    
    # Add a quadrant analysis section
    html += '''
    <div style="margin-top: 20px;">
        <h4 style="margin-top: 0; color: #555;">Insight:</h4>
        <p style="margin-top: 5px; color: #666;">
            The graph plots feedback categories by mention frequency (x-axis) and impact severity (y-axis). 
            Items in the upper-right quadrant represent high-priority issues that are both frequently mentioned and have high impact.
            Bubble color indicates sentiment (green = positive, blue = neutral, red = negative).
        </p>
    </div>
    '''
    
    html += '</div>'
    
    return html
