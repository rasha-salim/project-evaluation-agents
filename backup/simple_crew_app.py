import streamlit as st
from simple_crew import SimpleCrewManager
import time

# Set page configuration
st.set_page_config(
    page_title="Simple Crew Manager Demo",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "output" not in st.session_state:
    st.session_state.output = ""
if "mode" not in st.session_state:
    st.session_state.mode = "sequential"

def run_crew():
    """Run the simple crew manager"""
    try:
        # Create and run the crew manager
        crew_manager = SimpleCrewManager(mode=st.session_state.mode)
        start_time = time.time()
        result = crew_manager.run()
        end_time = time.time()
        
        # Format the result
        formatted_result = {
            "result": result,
            "execution_time": f"{end_time - start_time:.2f} seconds",
            "mode": st.session_state.mode
        }
        
        return formatted_result
    except Exception as e:
        return f"Error running crew: {str(e)}"

# Streamlit UI
st.title("Simple Crew Manager Demo")
st.write("This app demonstrates a simplified version of the Project Evolution Crew system.")

# Mode selection
st.radio(
    "Select execution mode:",
    ["sequential", "parallel"],
    key="mode"
)

# Start button
if st.button("Run Crew", disabled=st.session_state.running):
    st.session_state.running = True
    with st.spinner(f"Running crew in {st.session_state.mode} mode..."):
        result = run_crew()
        st.session_state.output = result
        st.session_state.running = False

# Display results
if st.session_state.output:
    st.subheader("Crew Output")
    
    if isinstance(st.session_state.output, dict):
        st.write(f"**Mode:** {st.session_state.output['mode']}")
        st.write(f"**Execution Time:** {st.session_state.output['execution_time']}")
        st.write("**Result:**")
        st.write(st.session_state.output['result'])
    else:
        st.error(st.session_state.output)
