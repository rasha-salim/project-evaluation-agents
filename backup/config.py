"""
Configuration settings for the Project Evolution Agents system.
"""

import os
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default configuration
DEFAULT_CONFIG = {
    # API settings
    'api': {
        'provider': 'anthropic',  # or 'openai'
        'openai_api_key': '',
        'anthropic_api_key': '',
        'default_model': 'claude-3-haiku-20240307',  # or 'gpt-4'
    },
    
    # Agent settings
    'agents': {
        'verbose': True,
        'max_iterations': 3,
        'timeout': 600,  # seconds
    },
    
    # Execution settings
    'execution': {
        'default_mode': 'sequential',  # 'sequential', 'parallel', or 'autonomous'
        'log_level': 'INFO',
    },
    
    # Data settings
    'data': {
        'feedback_file': 'data/sample_feedback.csv',
        'output_dir': 'output',
    }
}

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        file_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config from {file_path}: {str(e)}")
        return {}

def get_config() -> Dict[str, Any]:
    """
    Get the application configuration, combining default values with
    environment variables and YAML configuration.
    
    Returns:
        Dictionary containing configuration values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables
    if os.environ.get('OPENAI_API_KEY'):
        config['api']['openai_api_key'] = os.environ.get('OPENAI_API_KEY')
    
    if os.environ.get('ANTHROPIC_API_KEY'):
        config['api']['anthropic_api_key'] = os.environ.get('ANTHROPIC_API_KEY')
    
    if os.environ.get('API_PROVIDER'):
        config['api']['provider'] = os.environ.get('API_PROVIDER')
    else:
        # Default to Anthropic if not specified
        config['api']['provider'] = 'anthropic'
    
    if os.environ.get('DEFAULT_MODEL'):
        config['api']['default_model'] = os.environ.get('DEFAULT_MODEL')
    else:
        # Default to Claude model if not specified
        if config['api']['provider'] == 'anthropic':
            config['api']['default_model'] = 'claude-3-haiku-20240307'
    
    if os.environ.get('EXECUTION_MODE'):
        config['execution']['default_mode'] = os.environ.get('EXECUTION_MODE')
    
    # Load agent configuration from YAML
    agents_config = load_yaml_config('agents/agents.yaml')
    if agents_config:
        # Merge with default config
        # This is a simplified merge - in a real application you might
        # want a more sophisticated deep merge
        config['agents_config'] = agents_config
    
    # Load tasks configuration from YAML
    tasks_config = load_yaml_config('tasks/tasks.yaml')
    if tasks_config:
        config['tasks_config'] = tasks_config
    
    return config

def get_api_key(provider: Optional[str] = None) -> str:
    """
    Get the API key for the specified provider.
    
    Args:
        provider: The API provider ('openai' or 'anthropic')
        
    Returns:
        API key for the specified provider
    """
    config = get_config()
    provider = provider or config['api']['provider']
    
    if provider == 'openai':
        return config['api']['openai_api_key']
    elif provider == 'anthropic':
        return config['api']['anthropic_api_key']
    else:
        raise ValueError(f"Unsupported API provider: {provider}")
