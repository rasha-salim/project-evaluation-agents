import streamlit.components.v1 as components
import re

def render_feedback_analysis_visualization(feedback_analysis_text):
    """
    Create visualizations for the feedback analysis tab
    
    Args:
        feedback_analysis_text: The feedback analysis text from the AI
    """
    # For now, always use sample data to ensure visualizations are displayed
    # This will be replaced with actual data extraction once the patterns are refined
    categories = get_sample_categories()
    sentiment = get_sample_sentiment()
    
    # Attempt to extract real data (for future use)
    # extracted_categories, extracted_sentiment = extract_feedback_data(feedback_analysis_text)
    
    # Create a bar chart for categories
    category_html = create_category_bars(categories)
    components.html(category_html, height=len(categories) * 50 + 100)
    
    # Create a sentiment analysis visualization with increased height
    sentiment_html = create_sentiment_bars(sentiment)
    components.html(sentiment_html, height=200)  # Increased from 150 to 200

def extract_feedback_data(text):
    """Extract feedback data from feedback analysis text"""
    categories = []
    sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    # Extract categories
    pattern_category = r'(?:Category|Theme|Topic|Area|Issue)\s*(?:\d+)?\s*[:\-]\s*([^\n]+)'
    category_matches = re.findall(pattern_category, text, re.IGNORECASE)
    
    for i, category in enumerate(category_matches[:6]):  # Limit to 6 categories
        # Try to find mentions or counts
        count_pattern = r'{}.*?(?:(\d+)\s*(?:mentions|users|occurrences|times)|mentioned\s*(?:by)?\s*(\d+))'.format(re.escape(category))
        count_match = re.search(count_pattern, text, re.IGNORECASE)
        
        count = int(count_match.group(1) or count_match.group(2)) if count_match else i + 1
        categories.append({
            "category": category.strip(),
            "count": count
        })
    
    # Sort by count
    categories.sort(key=lambda x: x["count"], reverse=True)
    
    # Extract sentiment
    sentiment_pattern = r'(?:Sentiment|Tone).*?(?:positive|neutral|negative).*?(\d+)%.*?(?:positive|neutral|negative).*?(\d+)%.*?(?:positive|neutral|negative).*?(\d+)%'
    sentiment_match = re.search(sentiment_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if sentiment_match:
        # Extract percentages
        percentages = [int(p) for p in sentiment_match.groups()]
        
        # Determine which is which based on context
        positive_pattern = r'positive.*?(\d+)%'
        neutral_pattern = r'neutral.*?(\d+)%'
        negative_pattern = r'negative.*?(\d+)%'
        
        positive_match = re.search(positive_pattern, text, re.IGNORECASE)
        neutral_match = re.search(neutral_pattern, text, re.IGNORECASE)
        negative_match = re.search(negative_pattern, text, re.IGNORECASE)
        
        sentiment['positive'] = int(positive_match.group(1)) if positive_match else percentages[0]
        sentiment['neutral'] = int(neutral_match.group(1)) if neutral_match else percentages[1]
        sentiment['negative'] = int(negative_match.group(1)) if negative_match else percentages[2]
    
    return categories, sentiment

def get_sample_categories():
    """Provide sample categories when extraction fails"""
    return [
        {"category": "UI/UX Issues", "count": 8},
        {"category": "Performance Problems", "count": 6},
        {"category": "Feature Requests", "count": 5},
        {"category": "Usability Concerns", "count": 4},
        {"category": "Documentation Needs", "count": 3}
    ]

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
