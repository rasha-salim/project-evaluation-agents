# Project Evolution Agents

A Streamlit application that demonstrates how multiple AI agents can work together to drive product evolution using Anthropic's Claude model. This project showcases direct integration with the Anthropic API to orchestrate a team of specialized agents that analyze feedback, generate feature proposals, assess technical feasibility, create sprint plans, and communicate with stakeholders.

## Project Overview

The system demonstrates how agentic AI can transform product management from reactive to proactive by handling complex workflows that would typically require multiple team members. It uses direct integration with Anthropic's Claude API to create specialized agents that work together to analyze feedback, generate feature proposals, assess technical feasibility, create sprint plans, and communicate with stakeholders.

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

- **Sequential and Parallel Processing Modes**: Choose between sequential or parallel agent execution
- **CSV File Upload**: Upload feedback data via CSV files or use text input
- **Interactive Visualizations**: Visual representations of agent outputs for better understanding
- **Real-time Progress Tracking**: Monitor the status of each agent task as it executes
- **Direct Anthropic Claude Integration**: Powered by Claude models for advanced reasoning capabilities

### Visualizations

- **Feedback Analysis**: Category bar charts and sentiment analysis visualizations
- **Feature Proposals**: Feature priority vs. complexity matrix and detailed feature tables
- **Technical Evaluation**: Radar charts for technical feasibility and implementation difficulty bars
- **Sprint Planning**: Sprint timeline visualization with task breakdowns
- **Stakeholder Updates**: Project progress overview with key metrics and achievements

## Project Structure

```
project-evolution-agents/
├── direct_agents/
│   ├── __init__.py
│   ├── agent.py           # Agent class with direct Anthropic API integration
│   ├── task.py            # Task class for defining and executing tasks
│   └── crew.py            # Crew class for orchestrating agents and tasks
├── data/
│   └── sample_feedback.csv # Sample feedback data
├── direct_app.py          # Streamlit UI with direct Anthropic integration
├── feedback_visualizations.py # Feedback analysis visualizations
├── feature_visualizations.py  # Feature proposal visualizations
├── technical_visualizations.py # Technical evaluation visualizations
├── sprint_visualizations.py    # Sprint plan visualizations
├── stakeholder_visualizations.py # Stakeholder update visualizations
├── sample_visualizations.py   # Sample visualization functions
├── .env                    # Environment variables and API configuration
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Setup and Installation

1. Clone this repository
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your Anthropic API key in the `.env` file or through the UI

## Running the Application

Start the Streamlit application:

```
# Activate your virtual environment first
streamlit run direct_app.py
```

This will launch a web interface where you can:
- Select the execution mode (Sequential or Parallel)
- Upload feedback data via CSV or use text input/sample data
- Enter your Anthropic API key
- Start and monitor the agent execution with real-time progress tracking
- View the outputs from each agent with interactive visualizations
- See visual representations of feedback analysis, feature proposals, technical evaluations, sprint plans, and stakeholder updates

## Visualizations

The application includes visualizations for each section:

1. **Feedback Analysis**
   - Category bar charts showing the frequency of different feedback categories
   - Sentiment analysis with progress bars for positive, neutral, and negative feedback

2. **Feature Proposals**
   - Feature priority vs. complexity matrix to visualize the relationship between these attributes
   - Detailed feature tables with color-coding based on priority and complexity

3. **Technical Evaluation**
   - Radar charts showing technical feasibility assessment for each feature
   - Implementation difficulty bars to visualize the complexity of each feature

4. **Sprint Plan**
   - Sprint timeline visualization showing tasks organized by sprint
   - Sprint summary table with task counts and descriptions

5. **Stakeholder Update**
   - Project progress overview with circular progress indicators
   - Feature status breakdown with progress bars
   - Key achievements, challenges, and next steps visualization
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
