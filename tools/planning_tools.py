"""
Planning tools for Project Evolution Agents.
These tools enable the Sprint Planner Agent to create actionable sprint plans.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlanningTools:
    """Tools for the Sprint Planner Agent to create sprint plans."""
    
    @staticmethod
    def capacity_planning(team_size: int = 5, availability_percent: float = 0.8, 
                         story_points_per_developer: float = 10) -> Dict[str, Any]:
        """
        Calculate team capacity for sprint planning.
        
        Args:
            team_size: Number of developers on the team
            availability_percent: Percentage of time available for sprint work (0.0-1.0)
            story_points_per_developer: Average story points per developer per sprint
            
        Returns:
            Dictionary containing capacity planning information
        """
        logger.info(f"Calculating capacity for team of {team_size} developers")
        
        try:
            # Calculate capacity
            raw_capacity = team_size * story_points_per_developer
            adjusted_capacity = raw_capacity * availability_percent
            
            # Create capacity plan
            capacity_plan = {
                'team_size': team_size,
                'availability_percent': availability_percent,
                'story_points_per_developer': story_points_per_developer,
                'raw_capacity': raw_capacity,
                'adjusted_capacity': adjusted_capacity,
                'sprint_duration_days': 10,  # 2-week sprint = 10 working days
                'developer_days_available': team_size * 10 * availability_percent
            }
            
            logger.info(f"Calculated sprint capacity: {adjusted_capacity:.1f} story points")
            return capacity_plan
        except Exception as e:
            logger.error(f"Error in capacity planning: {str(e)}")
            raise
    
    @staticmethod
    def story_point_estimation(features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine story point estimates for features.
        
        Args:
            features: List of features with initial estimates
            
        Returns:
            List of features with refined estimates
        """
        logger.info(f"Refining story point estimates for {len(features)} features")
        
        try:
            # In a real implementation, this might involve a more sophisticated
            # estimation algorithm or team input
            
            refined_features = []
            
            for feature in features:
                # Get the initial estimate
                initial_points = feature.get('effort_estimate', {}).get('story_points', 0)
                
                # Apply refinement rules (simplified)
                # In reality, this would be based on team velocity, historical data, etc.
                
                # Round to standard Fibonacci sequence
                fibonacci = [1, 2, 3, 5, 8, 13, 21]
                closest_fibonacci = min(fibonacci, key=lambda x: abs(x - initial_points))
                
                # Create refined feature
                refined_feature = feature.copy()
                refined_feature['story_points'] = closest_fibonacci
                
                # Add tasks breakdown (simplified)
                refined_feature['tasks'] = [
                    {
                        'description': f"Design and plan {feature.get('title', 'feature')}",
                        'assignee_role': "Designer",
                        'estimate_days': max(1, closest_fibonacci * 0.2)
                    },
                    {
                        'description': f"Implement {feature.get('title', 'feature')}",
                        'assignee_role': "Developer",
                        'estimate_days': max(1, closest_fibonacci * 0.5)
                    },
                    {
                        'description': f"Test {feature.get('title', 'feature')}",
                        'assignee_role': "QA Engineer",
                        'estimate_days': max(1, closest_fibonacci * 0.3)
                    }
                ]
                
                refined_features.append(refined_feature)
            
            logger.info(f"Completed story point refinement for {len(features)} features")
            return refined_features
        except Exception as e:
            logger.error(f"Error in story point estimation: {str(e)}")
            raise
    
    @staticmethod
    def sprint_organization(capacity: Dict[str, Any], features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Organize features into a sprint plan based on capacity.
        
        Args:
            capacity: Dictionary containing capacity planning information
            features: List of features with story point estimates
            
        Returns:
            Dictionary containing the sprint plan
        """
        logger.info("Creating sprint plan")
        
        try:
            # Sort features by priority and feasibility
            sorted_features = sorted(
                features, 
                key=lambda x: (
                    # Priority order: Critical, High, Medium, Low
                    {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.get('priority', 'Low'), 4),
                    # Higher feasibility score is better
                    -x.get('feasibility_score', 0)
                )
            )
            
            # Allocate features to sprint based on capacity
            sprint_features = []
            total_story_points = 0
            available_capacity = capacity['adjusted_capacity']
            
            for feature in sorted_features:
                story_points = feature.get('story_points', 0)
                
                if total_story_points + story_points <= available_capacity:
                    sprint_features.append(feature)
                    total_story_points += story_points
            
            # Calculate capacity utilization
            capacity_utilization = (total_story_points / available_capacity) * 100 if available_capacity > 0 else 0
            
            # Create sprint dates
            start_date = datetime.now() + timedelta(days=1)  # Start tomorrow
            end_date = start_date + timedelta(days=13)  # 2 weeks (including weekends)
            
            # Create the sprint plan
            sprint_plan = {
                'sprint_name': f"Sprint {datetime.now().strftime('%Y-%m-%d')}",
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'capacity': available_capacity,
                'features': sprint_features,
                'total_story_points': total_story_points,
                'capacity_utilization': capacity_utilization
            }
            
            logger.info(f"Created sprint plan with {len(sprint_features)} features and {total_story_points} story points ({capacity_utilization:.1f}% capacity)")
            return sprint_plan
        except Exception as e:
            logger.error(f"Error in sprint organization: {str(e)}")
            raise
