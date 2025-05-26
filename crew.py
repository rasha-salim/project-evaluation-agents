"""
Main orchestration module for Project Evolution Agents using CrewAI.
This module handles agent creation, task assignment, and workflow execution.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from crewai import Agent, Task, Crew, Process
from crewai.tasks.task_output import TaskOutput

# Import custom tools
from tools.custom_tools import FeedbackTools
from tools.technical_tools import TechnicalTools
from tools.planning_tools import PlanningTools
from tools.communication_tools import CommunicationTools

# Import configuration
from config import get_config, get_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectEvolutionCrew:
    """
    Main class for orchestrating the Project Evolution Agents system.
    Handles agent creation, task assignment, and workflow execution.
    """
    
    def __init__(self, mode: str = 'sequential'):
        """
        Initialize the ProjectEvolutionCrew.
        
        Args:
            mode: Execution mode ('sequential', 'parallel', or 'autonomous')
        """
        self.config = get_config()
        self.mode = mode
        self.agents = {}
        self.tasks = {}
        self.outputs = {}
        self.execution_log = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.config['data']['output_dir'], exist_ok=True)
        
        # Initialize agents and tasks
        self._initialize_agents()
        self._initialize_tasks()
        
        logger.info(f"ProjectEvolutionCrew initialized in {mode} mode")
    
    def _initialize_agents(self):
        """Initialize agents from configuration."""
        logger.info("Initializing agents")
        
        # Get API configuration
        api_provider = self.config['api']['provider']
        api_key = get_api_key(api_provider)
        
        if not api_key:
            logger.warning(f"No API key found for {api_provider}. Agents will not be able to make API calls.")
        
        # Create agents from YAML configuration
        agent_configs = self.config.get('agents_config', {}).get('agents', {})
        
        for agent_id, agent_config in agent_configs.items():
            # Create agent
            agent = Agent(
                role=agent_config.get('role', ''),
                goal=agent_config.get('goal', ''),
                backstory=agent_config.get('backstory', ''),
                verbose=agent_config.get('verbose', True),
                allow_delegation=True,
                # Use the configured LLM settings
                llm_config={
                    'provider': agent_config.get('llm', {}).get('provider', api_provider),
                    'model': agent_config.get('llm', {}).get('model', self.config['api']['default_model']),
                    'temperature': agent_config.get('llm', {}).get('temperature', 0.7),
                    'api_key': api_key
                }
            )
            
            # Add agent to the collection
            self.agents[agent_id] = agent
            logger.info(f"Initialized agent: {agent_id}")
    
    def _initialize_tasks(self):
        """Initialize tasks from configuration."""
        logger.info("Initializing tasks")
        
        # Get task configurations
        task_configs = self.config.get('tasks_config', {}).get('tasks', {})
        
        # First pass: Create all tasks
        for task_id, task_config in task_configs.items():
            # Get the agent for this task
            agent_id = task_config.get('agent', '')
            agent = self.agents.get(agent_id)
            
            if not agent:
                logger.warning(f"Agent {agent_id} not found for task {task_id}")
                continue
            
            # Prepare task context
            context = {}
            
            # Add input schema information if available
            if 'inputs' in task_config:
                input_descriptions = []
                for input_item in task_config['inputs']:
                    input_desc = f"{input_item['name']}: {input_item['description']}"
                    if input_item.get('required', False):
                        input_desc += " (Required)"
                    input_descriptions.append(input_desc)
                
                if input_descriptions:
                    context['input_descriptions'] = "\n".join(input_descriptions)
            
            # Add output schema information if available
            if 'outputs' in task_config:
                output_descriptions = []
                for output_item in task_config['outputs']:
                    output_descriptions.append(f"{output_item['name']}: {output_item['description']}")
                
                if output_descriptions:
                    context['output_descriptions'] = "\n".join(output_descriptions)
            
            # Enhance task description with context
            description = task_config.get('description', '')
            if context:
                description += "\n\nInputs:\n" + context.get('input_descriptions', '')
                description += "\n\nOutputs:\n" + context.get('output_descriptions', '')
            
            # Create task
            task = Task(
                description=description,
                agent=agent,
                expected_output=task_config.get('expected_output_schema', {}),
                async_execution=self.mode == 'parallel',
                context=context
            )
            
            # Add task to the collection
            self.tasks[task_id] = task
            logger.info(f"Initialized task: {task_id}")
        
        # Second pass: Set up task dependencies based on workflow configuration
        workflow_configs = self.config.get('tasks_config', {}).get('workflows', {})
        selected_workflow = workflow_configs.get(self.mode, {})
        
        if selected_workflow:
            logger.info(f"Setting up dependencies for workflow: {selected_workflow.get('name', self.mode)}")
            
            # Get workflow steps
            steps = selected_workflow.get('steps', [])
            
            # Build dependency map
            for step in steps:
                task_id = step.get('task')
                depends_on = step.get('depends_on', [])
                
                if task_id in self.tasks and depends_on:
                    task = self.tasks[task_id]
                    
                    # Add human-readable dependency information to task description
                    dependency_info = "\n\nThis task depends on the following tasks:\n"
                    for dep_id in depends_on:
                        if dep_id in self.tasks:
                            dependency_info += f"- {dep_id}\n"
                    
                    # Update task description
                    task.description += dependency_info
                    
                    logger.info(f"Set dependencies for task {task_id}: {depends_on}")
        
        logger.info(f"Initialized {len(self.tasks)} tasks for mode: {self.mode}")
    
    def _log_execution(self, message: str):
        """
        Log execution events with timestamps.
        
        Args:
            message: Log message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"{timestamp} - {message}"
        self.execution_log.append(log_entry)
        logger.info(message)
    
    def run_sequential(self, feedback_file: str) -> Dict[str, Any]:
        """
        Run the crew in sequential mode.
        
        Args:
            feedback_file: Path to the feedback CSV file
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        self._log_execution("Starting sequential workflow")
        
        # Create the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[
                self.tasks['analyze_feedback'],
                self.tasks['generate_feature_proposals'],
                self.tasks['evaluate_feasibility'],
                self.tasks['create_sprint_plan'],
                self.tasks['generate_stakeholder_update']
            ],
            verbose=2,
            process=Process.sequential
        )
        
        # Run the crew
        start_time = time.time()
        result = crew.kickoff(inputs={'feedback_data': feedback_file})
        end_time = time.time()
        
        self._log_execution(f"Sequential workflow completed in {end_time - start_time:.2f} seconds")
        
        # Save the result
        self._save_output('sequential_result', result)
        
        return result
    
    def run_parallel(self, feedback_file: str) -> Dict[str, Any]:
        """
        Run the crew in parallel mode.
        
        Args:
            feedback_file: Path to the feedback CSV file
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        self._log_execution("Starting parallel workflow")
        
        # Create the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=[
                self.tasks['analyze_feedback'],
                self.tasks['generate_feature_proposals'],
                self.tasks['evaluate_feasibility'],
                self.tasks['create_sprint_plan'],
                self.tasks['generate_stakeholder_update']
            ],
            verbose=2,
            process=Process.hierarchical
        )
        
        # Run the crew
        start_time = time.time()
        result = crew.kickoff(inputs={'feedback_data': feedback_file})
        end_time = time.time()
        
        self._log_execution(f"Parallel workflow completed in {end_time - start_time:.2f} seconds")
        
        # Save the result
        self._save_output('parallel_result', result)
        
        return result
    
    def run_autonomous(self, feedback_file: str) -> Dict[str, Any]:
        """
        Run the crew in autonomous mode with iteration capabilities.
        
        Args:
            feedback_file: Path to the feedback CSV file
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        self._log_execution("Starting autonomous workflow with intelligent iteration")
        
        # Store iteration metrics for analysis
        iteration_metrics = {
            'feature_iterations': [],
            'sprint_iterations': [],
            'total_iterations': 0,
            'iteration_triggers': []
        }
        
        # Step 1: Analyze feedback
        self._log_execution("Autonomous: Running feedback analysis")
        start_time = time.time()
        feedback_data = FeedbackTools.read_csv(feedback_file)
        feedback_analysis = FeedbackTools.analyze_feedback(feedback_data)
        self._save_output('feedback_analysis', feedback_analysis)
        self._log_execution(f"Feedback analysis completed in {time.time() - start_time:.2f} seconds")
        
        # Extract key metrics for logging
        feedback_count = feedback_analysis.get('total_feedback_count', 0)
        categories_count = len(feedback_analysis.get('categories', []))
        self._log_execution(f"Analyzed {feedback_count} feedback items across {categories_count} categories")
        
        # Step 2: Generate feature proposals
        self._log_execution("Autonomous: Generating feature proposals")
        start_time = time.time()
        features = FeatureTools.prioritize_features(feedback_analysis)
        feature_proposals = {'features': features}
        self._save_output('feature_proposals', feature_proposals)
        self._log_execution(f"Feature proposal generation completed in {time.time() - start_time:.2f} seconds")
        
        # Log feature metrics
        feature_count = len(features)
        priority_distribution = {}
        for feature in features:
            priority = feature.get('priority', 'Unknown')
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        self._log_execution(f"Generated {feature_count} feature proposals")
        self._log_execution(f"Priority distribution: {priority_distribution}")
        
        # Step 3: Evaluate feasibility with intelligent iteration
        self._log_execution("Autonomous: Evaluating technical feasibility")
        start_time = time.time()
        complexity_assessments = TechnicalTools.complexity_analysis(features)
        feasibility_assessment = TechnicalTools.effort_estimation(complexity_assessments)
        
        # Check if we need to iterate (feasibility < 50%)
        iteration_count = 0
        max_iterations = self.config['agents']['max_iterations']
        original_features = features.copy()  # Save original features for comparison
        
        # Track low feasibility features
        low_feasibility_features = []
        for assessment in feasibility_assessment.get('assessments', []):
            if assessment.get('feasibility_score', 0) < 50:
                low_feasibility_features.append(assessment.get('feature_id', 'unknown'))
        
        if low_feasibility_features:
            self._log_execution(f"Detected {len(low_feasibility_features)} features with low feasibility: {', '.join(low_feasibility_features)}")
        
        while (feasibility_assessment['average_feasibility_score'] < 50 and 
               iteration_count < max_iterations):
            self._log_execution(f"Autonomous: Feasibility score too low ({feasibility_assessment['average_feasibility_score']:.1f}%), triggering feature regeneration")
            
            # Store iteration data
            iteration_metrics['feature_iterations'].append({
                'iteration': iteration_count + 1,
                'trigger': 'low_feasibility',
                'before_score': feasibility_assessment['average_feasibility_score'],
                'low_feasibility_features': low_feasibility_features
            })
            
            # Regenerate features with higher feasibility
            # In a real implementation, we would use the LLM to regenerate features
            # with guidance to improve feasibility
            start_time = time.time()
            
            # Simulate more feasible feature generation by modifying complexity
            # This is a simplified version for demonstration
            for feature in features:
                # Find corresponding assessment
                assessment = next((a for a in feasibility_assessment.get('assessments', []) 
                                  if a.get('feature_id') == feature.get('id')), None)
                
                if assessment and assessment.get('feasibility_score', 100) < 50:
                    # Simplify the feature description to improve feasibility
                    feature['description'] = f"Simplified version of: {feature['description']}"
                    feature['title'] = f"Simplified {feature['title']}"
            
            feature_proposals = {'features': features}
            self._log_execution(f"Feature regeneration completed in {time.time() - start_time:.2f} seconds")
            
            # Re-evaluate feasibility
            start_time = time.time()
            complexity_assessments = TechnicalTools.complexity_analysis(features)
            feasibility_assessment = TechnicalTools.effort_estimation(complexity_assessments)
            self._log_execution(f"Feasibility re-assessment completed in {time.time() - start_time:.2f} seconds")
            
            # Update iteration metrics
            iteration_count += 1
            iteration_metrics['total_iterations'] += 1
            iteration_metrics['iteration_triggers'].append('low_feasibility')
            
            # Update low feasibility features for next iteration
            low_feasibility_features = []
            for assessment in feasibility_assessment.get('assessments', []):
                if assessment.get('feasibility_score', 0) < 50:
                    low_feasibility_features.append(assessment.get('feature_id', 'unknown'))
            
            self._log_execution(f"Autonomous: Iteration {iteration_count}, new feasibility score: {feasibility_assessment['average_feasibility_score']:.1f}%")
            
            # Add final iteration data
            if iteration_count > 0 and iteration_metrics['feature_iterations']:
                iteration_metrics['feature_iterations'][-1]['after_score'] = feasibility_assessment['average_feasibility_score']
                iteration_metrics['feature_iterations'][-1]['improvement'] = iteration_metrics['feature_iterations'][-1]['after_score'] - \
                                                                           iteration_metrics['feature_iterations'][-1]['before_score']
        
        self._save_output('feasibility_assessment', feasibility_assessment)
        
        # Step 4: Create sprint plan with capacity-based iteration
        self._log_execution("Autonomous: Creating sprint plan")
        start_time = time.time()
        capacity = PlanningTools.capacity_planning()
        refined_features = PlanningTools.story_point_estimation(complexity_assessments)
        sprint_plan = PlanningTools.sprint_organization(capacity, refined_features)
        self._log_execution(f"Sprint planning completed in {time.time() - start_time:.2f} seconds")
        
        # Check if we need to iterate (capacity exceeded)
        iteration_count = 0
        original_capacity = capacity['adjusted_capacity']
        
        while (sprint_plan['capacity_utilization'] > 100 and 
               iteration_count < max_iterations):
            self._log_execution(f"Autonomous: Capacity exceeded ({sprint_plan['capacity_utilization']:.1f}%), triggering re-planning")
            
            # Store iteration data
            iteration_metrics['sprint_iterations'].append({
                'iteration': iteration_count + 1,
                'trigger': 'capacity_exceeded',
                'before_utilization': sprint_plan['capacity_utilization'],
                'capacity': capacity['adjusted_capacity'],
                'feature_count': len(sprint_plan.get('features', []))
            })
            
            # Adjust capacity or reduce features
            start_time = time.time()
            
            # Strategy 1: Try increasing capacity first
            if iteration_count == 0:
                capacity['adjusted_capacity'] *= 1.1  # Increase capacity by 10%
                self._log_execution(f"Increasing capacity from {original_capacity:.1f} to {capacity['adjusted_capacity']:.1f}")
            # Strategy 2: If still exceeding after capacity increase, remove lowest priority features
            else:
                # Sort features by priority (descending) and feasibility (descending)
                sorted_features = sorted(
                    refined_features,
                    key=lambda x: (
                        {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.get('priority', 'Low'), 4),
                        -x.get('feasibility_score', 0)
                    ),
                    reverse=True  # Reverse to get lowest priority first
                )
                
                # Remove the lowest priority feature
                if sorted_features:
                    removed_feature = sorted_features.pop()
                    refined_features = [f for f in refined_features if f.get('feature_id', '') != removed_feature.get('feature_id', '')]
                    self._log_execution(f"Removed feature {removed_feature.get('feature_id', 'unknown')} from sprint plan")
            
            # Re-create sprint plan
            sprint_plan = PlanningTools.sprint_organization(capacity, refined_features)
            self._log_execution(f"Sprint re-planning completed in {time.time() - start_time:.2f} seconds")
            
            # Update iteration metrics
            iteration_count += 1
            iteration_metrics['total_iterations'] += 1
            iteration_metrics['iteration_triggers'].append('capacity_exceeded')
            
            self._log_execution(f"Autonomous: Iteration {iteration_count}, new capacity utilization: {sprint_plan['capacity_utilization']:.1f}%")
            
            # Add final iteration data
            if iteration_count > 0 and iteration_metrics['sprint_iterations']:
                iteration_metrics['sprint_iterations'][-1]['after_utilization'] = sprint_plan['capacity_utilization']
                iteration_metrics['sprint_iterations'][-1]['improvement'] = iteration_metrics['sprint_iterations'][-1]['before_utilization'] - \
                                                                            iteration_metrics['sprint_iterations'][-1]['after_utilization']
        
        self._save_output('sprint_plan', sprint_plan)
        self._save_output('iteration_metrics', iteration_metrics)
        
        # Step 5: Generate stakeholder update
        self._log_execution("Autonomous: Generating stakeholder update")
        start_time = time.time()
        aggregated_report = CommunicationTools.report_aggregation(
            feedback_analysis, feature_proposals, feasibility_assessment, sprint_plan
        )
        presentation = CommunicationTools.presentation_generation(aggregated_report)
        decision_matrix = CommunicationTools.decision_matrix_creation(aggregated_report)
        
        stakeholder_update = {
            'aggregated_report': aggregated_report,
            'presentation': presentation,
            'decision_matrix': decision_matrix,
            'iteration_summary': {
                'total_iterations': iteration_metrics['total_iterations'],
                'feature_iterations': len(iteration_metrics['feature_iterations']),
                'sprint_iterations': len(iteration_metrics['sprint_iterations']),
                'triggers': iteration_metrics['iteration_triggers']
            }
        }
        
        self._save_output('stakeholder_update', stakeholder_update)
        self._log_execution(f"Stakeholder update generation completed in {time.time() - start_time:.2f} seconds")
        
        # Combine all outputs
        result = {
            'feedback_analysis': feedback_analysis,
            'feature_proposals': feature_proposals,
            'feasibility_assessment': feasibility_assessment,
            'sprint_plan': sprint_plan,
            'stakeholder_update': stakeholder_update,
            'iteration_metrics': iteration_metrics,
            'execution_log': self.execution_log
        }
        
        self._log_execution(f"Autonomous workflow completed with {iteration_metrics['total_iterations']} total iterations")
        
        # Save the final result
        self._save_output('autonomous_result', result)
        
        return result
    
    def run(self, feedback_file: str) -> Dict[str, Any]:
        """
        Run the crew in the specified mode.
        
        Args:
            feedback_file: Path to the feedback CSV file
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        if self.mode == 'sequential':
            return self.run_sequential(feedback_file)
        elif self.mode == 'parallel':
            return self.run_parallel(feedback_file)
        elif self.mode == 'autonomous':
            return self.run_autonomous(feedback_file)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
    
    def _save_output(self, name: str, data: Any):
        """
        Save output data to file.
        
        Args:
            name: Name of the output
            data: Output data to save
        """
        try:
            # Convert to JSON-serializable format if needed
            if isinstance(data, TaskOutput):
                data = data.raw_output
            
            # Save to file
            output_path = os.path.join(self.config['data']['output_dir'], f"{name}.json")
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved output to {output_path}")
            
            # Store in outputs dictionary
            self.outputs[name] = data
        except Exception as e:
            logger.error(f"Error saving output {name}: {str(e)}")
    
    def get_execution_log(self) -> List[str]:
        """
        Get the execution log.
        
        Returns:
            List of log entries
        """
        return self.execution_log


if __name__ == "__main__":
    # Simple test to run the crew
    config = get_config()
    feedback_file = config['data']['feedback_file']
    
    crew = ProjectEvolutionCrew(mode='sequential')
    result = crew.run(feedback_file)
    
    print("Execution log:")
    for log_entry in crew.get_execution_log():
        print(log_entry)
