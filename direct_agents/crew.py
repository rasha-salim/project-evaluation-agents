"""
Crew module for direct Anthropic integration.
This module provides the Crew class for orchestrating agents and tasks.
"""

import os
import json
import time
import logging
import threading
import queue
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .agent import Agent
from .task import Task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Crew:
    """
    Crew class for orchestrating agents and tasks.
    """
    
    def __init__(self, mode: str = 'sequential', progress_callback: Optional[Callable[[str, int, int], None]] = None):
        """
        Initialize the Crew.
        
        Args:
            mode: Execution mode ('sequential' or 'parallel')
            progress_callback: Optional callback function to report progress
                              Args: task_id, current_task_index, total_tasks
        """
        self.mode = mode
        self.agents = {}
        self.tasks = {}
        self.outputs = {}
        self.execution_log = []
        self.progress_callback = progress_callback
        self.current_task = None
        self.task_status = {}
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        logger.info(f"Crew initialized in {mode} mode")
    
    def add_agent(self, agent_id: str, agent: Agent):
        """
        Add an agent to the crew.
        
        Args:
            agent_id: The ID of the agent
            agent: The agent to add
        """
        self.agents[agent_id] = agent
        logger.info(f"Added agent: {agent_id}")
    
    def add_task(self, task_id: str, task: Task):
        """
        Add a task to the crew.
        
        Args:
            task_id: The ID of the task
            task: The task to add
        """
        self.tasks[task_id] = task
        logger.info(f"Added task: {task_id}")
    
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
        
    def _update_progress(self, task_id: str, status: str, index: int, total: int):
        """
        Update task status and call progress callback if provided.
        
        Args:
            task_id: ID of the current task
            status: Status of the task ('running', 'completed', 'error')
            index: Index of the current task
            total: Total number of tasks
        """
        self.current_task = task_id
        self.task_status[task_id] = status
        
        if self.progress_callback:
            self.progress_callback(task_id, status, index, total)
    
    def run_sequential(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the crew in sequential mode.
        
        Args:
            initial_context: Initial context for the first task
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        self._log_execution("Starting sequential workflow")
        
        # Initialize result dictionary
        result = initial_context or {}
        
        # Execute tasks sequentially
        start_time = time.time()
        task_items = list(self.tasks.items())
        total_tasks = len(task_items)
        
        for i, (task_id, task) in enumerate(task_items):
            self._log_execution(f"Executing task: {task_id}")
            self._update_progress(task_id, 'running', i, total_tasks)
            
            # Check if task dependencies are satisfied
            dependencies_satisfied = True
            for dep in task.dependencies:
                if dep not in self.outputs:
                    self._log_execution(f"Task {task_id} depends on {dep}, which has not been executed yet")
                    dependencies_satisfied = False
                    break
            
            if not dependencies_satisfied:
                self._log_execution(f"Skipping task {task_id} due to unsatisfied dependencies")
                self._update_progress(task_id, 'skipped', i, total_tasks)
                continue
            
            # Add previous outputs as context
            task_context = {}
            for dep in task.dependencies:
                if dep in self.outputs:
                    task_context[dep] = self.outputs[dep]
            
            # Execute task
            task_start_time = time.time()
            try:
                task_result = task.execute(task_context)
                task_end_time = time.time()
                
                self._log_execution(f"Task {task_id} completed in {task_end_time - task_start_time:.2f} seconds")
                self._update_progress(task_id, 'completed', i, total_tasks)
                
                # Store the result
                self.outputs[task_id] = task_result
                result[task_id] = task_result
            except Exception as e:
                self._log_execution(f"Error executing task {task_id}: {str(e)}")
                self._update_progress(task_id, 'error', i, total_tasks)
                # Continue with next task instead of failing the whole workflow
                continue
        
        end_time = time.time()
        
        self._log_execution(f"Sequential workflow completed in {end_time - start_time:.2f} seconds")
        
        # Save the result
        self._save_output('sequential_result', result)
        
        return result
    
    def run_parallel(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the crew in parallel mode.
        
        Args:
            initial_context: Initial context for the first task
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        self._log_execution("Starting parallel workflow")
        
        # Initialize result dictionary
        result = initial_context or {}
        
        # Create a queue for results
        result_queue = queue.Queue()
        
        # Create a shared dictionary for outputs (thread-safe)
        from threading import Lock
        outputs_lock = Lock()
        shared_outputs = {}
        
        # Function to execute a task in a thread
        def execute_task_thread(task_id, task, index):
            self._log_execution(f"Starting task: {task_id}")
            self._update_progress(task_id, 'running', index, total_tasks)
            
            # Wait for dependencies to complete
            for dep in task.dependencies:
                while True:
                    with outputs_lock:
                        if dep in shared_outputs:
                            break
                    time.sleep(0.5)  # Wait a bit and check again
            
            # Add previous outputs as context
            task_context = {}
            with outputs_lock:
                for dep in task.dependencies:
                    if dep in shared_outputs:
                        task_context[dep] = shared_outputs[dep]
            
            # Execute task
            task_start_time = time.time()
            try:
                task_result = task.execute(task_context)
                task_end_time = time.time()
                
                self._log_execution(f"Task {task_id} completed in {task_end_time - task_start_time:.2f} seconds")
                self._update_progress(task_id, 'completed', index, total_tasks)
                
                # Store the result
                with outputs_lock:
                    shared_outputs[task_id] = task_result
                
                # Put result in queue
                result_queue.put((task_id, task_result))
            except Exception as e:
                self._log_execution(f"Error executing task {task_id}: {str(e)}")
                self._update_progress(task_id, 'error', index, total_tasks)
                # Put error result in queue to avoid deadlock
                result_queue.put((task_id, f"Error: {str(e)}"))
        
        # Start timer
        start_time = time.time()
        
        # Create threads for each task
        threads = []
        task_items = list(self.tasks.items())
        total_tasks = len(task_items)
        
        for i, (task_id, task) in enumerate(task_items):
            thread = threading.Thread(
                target=execute_task_thread,
                args=(task_id, task, i)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all results
        for _ in range(len(self.tasks)):
            task_id, task_result = result_queue.get()
            self.outputs[task_id] = task_result
            result[task_id] = task_result
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        self._log_execution(f"Parallel workflow completed in {end_time - start_time:.2f} seconds")
        
        # Save the result
        self._save_output('parallel_result', result)
        
        return result
    
    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the crew in the specified mode.
        
        Args:
            initial_context: Initial context for the first task
            
        Returns:
            Dictionary containing all outputs from the workflow
        """
        if self.mode == 'sequential':
            return self.run_sequential(initial_context)
        elif self.mode == 'parallel':
            return self.run_parallel(initial_context)
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
            # Save to file
            output_path = os.path.join('output', f"{name}.json")
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved output to {output_path}")
        except Exception as e:
            logger.error(f"Error saving output {name}: {str(e)}")
    
    def get_execution_log(self) -> List[str]:
        """
        Get the execution log.
        
        Returns:
            List of log entries
        """
        return self.execution_log
