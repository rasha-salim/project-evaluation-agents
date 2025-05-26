# Project Leadership with Agentic AI

This repository contains a demonstration of an agentic AI system for continuous product improvement, built for a blog post series on "Project Leadership with Agentic AI". This is Part 2 of the series, focusing on how multiple AI agents can work together to drive product evolution using Anthropic's Claude model.

## Project Overview

The system demonstrates how agentic AI can transform product management from reactive to proactive by handling complex workflows that would typically require multiple team members. It uses the CrewAI framework to orchestrate a team of specialized agents that work together to analyze feedback, generate feature proposals, assess technical feasibility, create sprint plans, and communicate with stakeholders.

### The 5 Agents System

1. **Feedback Analyst Agent**
   - Analyzes user feedback, support tickets, and usage patterns
   - Inputs: CSV files with feedback data
   - Outputs: Categorized insights and pain points report

2. **Feature Strategist Agent**
   - Generates feature proposals based on feedback patterns
   - Inputs: Feedback analysis report
   - Outputs: Prioritized feature proposals with user impact scores

3. **Technical Feasibility Agent**
   - Evaluates technical complexity and dependencies
   - Inputs: Feature proposals
   - Outputs: Feasibility scores and implementation estimates

4. **Sprint Planner Agent**
   - Creates actionable sprint plans
   - Inputs: Feasible features with scores
   - Outputs: 2-week sprint plans with story points

5. **Stakeholder Communicator Agent**
   - Generates executive summaries and updates
   - Inputs: All previous agents' outputs
   - Outputs: Stakeholder presentation and decision matrix

### Key Features

- **Parallel Processing Mode**: Feedback, Technical, and Market agents can run simultaneously
- **Sequential Orchestration Mode**: Workflow follows a specific order with dependencies
- **Autonomous Iteration Feature**: Automatically triggers regeneration based on specific conditions
- **Interactive Visualizations**: Real-time visualization of agent interactions and iteration metrics
- **Anthropic Claude Integration**: Powered by Claude-3-Haiku for advanced reasoning capabilities

## Project Structure

```
project-evolution-agents/
├── agents/
│   └── agents.yaml         # Agent configuration
├── tasks/
│   └── tasks.yaml          # Task definitions and workflows
├── tools/
│   ├── custom_tools.py     # Tools for Feedback Analyst
│   ├── technical_tools.py  # Tools for Technical Feasibility Agent
│   ├── planning_tools.py   # Tools for Sprint Planner
│   └── communication_tools.py # Tools for Stakeholder Communicator
├── data/
│   └── sample_feedback.csv # Sample feedback data
├── app.py                  # Streamlit UI
├── crew.py                 # Main CrewAI orchestration
├── config.py               # Configuration settings
├── .env                    # Environment variables and API configuration
├── install_deps.py         # Helper script for dependency installation
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Setup and Installation

1. Clone this repository
2. Create a conda environment (recommended):
   ```
   conda create -n crewai-env python=3.10
   conda activate crewai-env
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   or use the helper script:
   ```
   python install_deps.py
   ```
4. Set up your Anthropic API key in the `.env` file or through the UI

## Running the Application

Start the Streamlit application:

```
conda activate crewai-env  # If using conda environment
streamlit run app.py
```

This will launch a web interface where you can:
- Select the execution mode (Sequential, Parallel, or Autonomous)
- Upload feedback data or use the sample data
- Enter your Anthropic API key
- Choose between different Claude models
- Start and monitor the agent execution
- View the outputs from each agent
- Explore interactive visualizations of agent interactions

## Use Cases

This demonstration can be used to showcase:
- How agentic AI can automate complex product management workflows
- The benefits of using multiple specialized agents versus a single agent
- Different orchestration patterns for agent collaboration
- How to implement autonomous decision-making with iteration capabilities
- Visualizing agent interactions and collaboration metrics
- Leveraging Anthropic's Claude model for complex reasoning tasks

## Sample Data

The repository includes sample feedback data (`data/sample_feedback.csv`) that simulates user feedback for the fictional SmartAssist product. This data includes:
- Date of feedback
- User ID
- Feedback type (bug, feature request, performance, usability)
- Description
- Severity (1-5)
- Feature area

## Extending the System

You can extend this system by:
- Adding more specialized agents
- Creating additional tools for existing agents
- Implementing more complex workflows
- Integrating with real data sources or APIs

## License

This project is provided as an educational demonstration. Feel free to use and modify it for your own purposes.

## Acknowledgments

This project uses the following technologies:
- [CrewAI](https://github.com/joaomdmoura/crewAI) framework for agent orchestration
- [Anthropic Claude](https://www.anthropic.com/claude) for advanced language capabilities
- [Streamlit](https://streamlit.io/) for the interactive web interface
- [Matplotlib](https://matplotlib.org/) for data visualization
