"""
Technical tools for Project Evolution Agents.
These tools enable the Technical Feasibility Agent to evaluate proposed features.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TechnicalTools:
    """Tools for the Technical Feasibility Agent to evaluate feature proposals."""
    
    @staticmethod
    def complexity_analysis(features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze the technical complexity of proposed features.
        
        Args:
            features: List of feature proposals
            
        Returns:
            List of features with complexity assessments
        """
        logger.info(f"Analyzing complexity for {len(features)} features")
        
        try:
            complexity_assessments = []
            
            for feature in features:
                # This is a simplified version - in a real implementation,
                # this would involve more sophisticated analysis
                
                # Determine complexity based on impact score (as a proxy)
                # In reality, this would be based on technical requirements
                impact = feature.get('impact_score', 50)
                
                if impact > 80:
                    complexity = "Complex"
                    story_points = 13
                    developer_days = 10
                elif impact > 60:
                    complexity = "Moderate"
                    story_points = 8
                    developer_days = 5
                elif impact > 40:
                    complexity = "Simple"
                    story_points = 5
                    developer_days = 3
                else:
                    complexity = "Very Simple"
                    story_points = 3
                    developer_days = 1
                
                # Create a complexity assessment
                assessment = {
                    'feature_id': feature['id'],
                    'title': feature['title'],
                    'complexity': complexity,
                    'effort_estimate': {
                        'story_points': story_points,
                        'developer_days': developer_days
                    },
                    'dependencies': [
                        "Core API integration",
                        "User authentication system"
                    ],
                    'risks': [
                        {
                            'description': "Integration with legacy systems may require additional work",
                            'severity': "Medium" if complexity in ["Complex", "Moderate"] else "Low"
                        }
                    ],
                    'technical_notes': f"Implementation will require updates to the {feature['addressing_categories'][0].split(' - ')[0]} module."
                }
                
                complexity_assessments.append(assessment)
            
            logger.info(f"Completed complexity analysis for {len(features)} features")
            return complexity_assessments
        except Exception as e:
            logger.error(f"Error in complexity analysis: {str(e)}")
            raise
    
    @staticmethod
    def dependency_mapping(complexity_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map dependencies between features and existing systems.
        
        Args:
            complexity_assessments: List of features with complexity assessments
            
        Returns:
            Dictionary containing dependency mapping
        """
        logger.info("Mapping dependencies between features")
        
        try:
            # Create a dependency graph (simplified version)
            dependency_graph = {
                'nodes': [],
                'edges': []
            }
            
            # System components that features might depend on
            system_components = [
                "User Authentication",
                "Core API",
                "Database",
                "Frontend UI",
                "Reporting Engine",
                "Integration Layer"
            ]
            
            # Add system components as nodes
            for component in system_components:
                dependency_graph['nodes'].append({
                    'id': component.replace(' ', '_').lower(),
                    'label': component,
                    'type': 'system'
                })
            
            # Add features as nodes
            for assessment in complexity_assessments:
                dependency_graph['nodes'].append({
                    'id': assessment['feature_id'],
                    'label': assessment['title'],
                    'type': 'feature',
                    'complexity': assessment['complexity']
                })
            
            # Add edges (dependencies)
            edge_id = 1
            for assessment in complexity_assessments:
                # Connect to system components based on feature area
                feature_area = assessment.get('title', '').split(' ')[1].lower()
                
                if 'user' in feature_area or 'auth' in feature_area:
                    dependency_graph['edges'].append({
                        'id': f"e{edge_id}",
                        'source': assessment['feature_id'],
                        'target': 'user_authentication',
                        'label': 'depends on'
                    })
                    edge_id += 1
                
                if 'api' in feature_area or 'data' in feature_area:
                    dependency_graph['edges'].append({
                        'id': f"e{edge_id}",
                        'source': assessment['feature_id'],
                        'target': 'core_api',
                        'label': 'depends on'
                    })
                    edge_id += 1
                
                if 'ui' in feature_area or 'interface' in feature_area:
                    dependency_graph['edges'].append({
                        'id': f"e{edge_id}",
                        'source': assessment['feature_id'],
                        'target': 'frontend_ui',
                        'label': 'depends on'
                    })
                    edge_id += 1
                
                # Add dependencies between features (simplified)
                for other in complexity_assessments:
                    if assessment['feature_id'] != other['feature_id']:
                        # If they share a dependency, they might be related
                        if any(dep in assessment.get('dependencies', []) for dep in other.get('dependencies', [])):
                            dependency_graph['edges'].append({
                                'id': f"e{edge_id}",
                                'source': assessment['feature_id'],
                                'target': other['feature_id'],
                                'label': 'related to'
                            })
                            edge_id += 1
            
            logger.info(f"Created dependency graph with {len(dependency_graph['nodes'])} nodes and {len(dependency_graph['edges'])} edges")
            return dependency_graph
        except Exception as e:
            logger.error(f"Error in dependency mapping: {str(e)}")
            raise
    
    @staticmethod
    def effort_estimation(complexity_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate effort required for implementing features.
        
        Args:
            complexity_assessments: List of features with complexity assessments
            
        Returns:
            Dictionary containing effort estimations
        """
        logger.info("Estimating implementation effort")
        
        try:
            # Calculate total effort
            total_story_points = sum(assessment['effort_estimate']['story_points'] for assessment in complexity_assessments)
            total_developer_days = sum(assessment['effort_estimate']['developer_days'] for assessment in complexity_assessments)
            
            # Estimate feasibility scores
            for assessment in complexity_assessments:
                # Calculate feasibility score (simplified)
                # Higher complexity = lower feasibility
                if assessment['complexity'] == "Very Complex":
                    feasibility_score = 40
                elif assessment['complexity'] == "Complex":
                    feasibility_score = 60
                elif assessment['complexity'] == "Moderate":
                    feasibility_score = 80
                else:  # Simple
                    feasibility_score = 95
                
                # Adjust based on risks
                risk_count = len(assessment.get('risks', []))
                high_risk_count = sum(1 for risk in assessment.get('risks', []) if risk.get('severity') == "High")
                
                feasibility_score -= (risk_count * 2 + high_risk_count * 5)
                feasibility_score = max(10, min(100, feasibility_score))  # Clamp between 10 and 100
                
                assessment['feasibility_score'] = feasibility_score
            
            # Create the effort estimation report
            estimation = {
                'timestamp': datetime.now().isoformat(),
                'total_story_points': total_story_points,
                'total_developer_days': total_developer_days,
                'average_feasibility_score': sum(assessment['feasibility_score'] for assessment in complexity_assessments) / len(complexity_assessments),
                'assessments': complexity_assessments
            }
            
            logger.info(f"Completed effort estimation with average feasibility score of {estimation['average_feasibility_score']:.1f}")
            return estimation
        except Exception as e:
            logger.error(f"Error in effort estimation: {str(e)}")
            raise
