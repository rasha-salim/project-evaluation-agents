import streamlit as st
import os
import time
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Direct Anthropic Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "output" not in st.session_state:
    st.session_state.output = ""

def get_api_key():
    """Get Anthropic API key from environment variables"""
    return os.getenv("ANTHROPIC_API_KEY")

def run_anthropic_query(query):
    """Run a query using the Anthropic API directly"""
    try:
        # Get API key
        api_key = get_api_key()
        
        if not api_key:
            return "Error: No Anthropic API key found. Please check your .env file."
        
        # Create Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Make API call
        start_time = time.time()
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user", 
                    "content": f"""You are a research assistant AI. Please respond to the following query:
                    
                    {query}
                    
                    Provide a detailed, well-structured response."""
                }
            ]
        )
        
        end_time = time.time()
        
        # Format result
        result = {
            "response": message.content[0].text,
            "model": "claude-3-haiku-20240307",
            "execution_time": f"{end_time - start_time:.2f} seconds"
        }
        
        return result
    except Exception as e:
        return f"Error using Anthropic API: {str(e)}"

# Streamlit UI
st.title("Direct Anthropic API Demo")
st.write("This app uses the Anthropic API directly without CrewAI.")

# Input area
query = st.text_area(
    "Enter your research query:",
    height=150,
    placeholder="e.g., Explain the latest advancements in artificial intelligence in 2024."
)

# Start button
if st.button("Run Query", disabled=st.session_state.running):
    if not query:
        st.error("Please enter a query.")
    else:
        st.session_state.running = True
        with st.spinner("Processing your query..."):
            result = run_anthropic_query(query)
            st.session_state.output = result
            st.session_state.running = False

# Display results
if st.session_state.output:
    st.subheader("Response")
    
    if isinstance(st.session_state.output, dict):
        st.write(f"**Model:** {st.session_state.output['model']}")
        st.write(f"**Execution Time:** {st.session_state.output['execution_time']}")
        st.markdown("**Response:**")
        st.markdown(st.session_state.output['response'])
    else:
        st.error(st.session_state.output)
