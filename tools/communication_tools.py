"""
Communication tools for Project Evolution Agents.
These tools enable the Stakeholder Communicator Agent to generate executive summaries and updates.
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

class CommunicationTools:
    """Tools for the Stakeholder Communicator Agent to generate reports and presentations."""
    
    @staticmethod
    def report_aggregation(feedback_report: Dict[str, Any], 
                          feature_proposals: Dict[str, Any],
                          feasibility_assessment: Dict[str, Any],
                          sprint_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate reports from all previous agents into a consolidated view.
        
        Args:
            feedback_report: Report from Feedback Analyst
            feature_proposals: Report from Feature Strategist
            feasibility_assessment: Report from Technical Feasibility Agent
            sprint_plan: Report from Sprint Planner
            
        Returns:
            Dictionary containing aggregated information
        """
        logger.info("Aggregating reports from all agents")
        
        try:
            # Extract key metrics
            feedback_count = feedback_report.get('total_feedback_count', 0)
            feature_count = len(feature_proposals.get('features', []))
            avg_feasibility = feasibility_assessment.get('average_feasibility_score', 0)
            sprint_capacity = sprint_plan.get('capacity_utilization', 0)
            
            # Create aggregated report
            aggregated_report = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'feedback_items_analyzed': feedback_count,
                    'feature_proposals_generated': feature_count,
                    'average_feasibility_score': avg_feasibility,
                    'sprint_capacity_utilization': sprint_capacity
                },
                'key_insights': [
                    f"Analyzed {feedback_count} feedback items across multiple categories",
                    f"Generated {feature_count} feature proposals to address user pain points",
                    f"Technical feasibility assessment shows {avg_feasibility:.1f}% average feasibility",
                    f"Sprint plan utilizes {sprint_capacity:.1f}% of available capacity"
                ],
                'feature_summary': []
            }
            
            # Add feature summary
            for feature in sprint_plan.get('features', []):
                # Find corresponding feasibility assessment
                feasibility_info = next(
                    (a for a in feasibility_assessment.get('assessments', []) if a.get('feature_id') == feature.get('feature_id')),
                    {}
                )
                
                # Add to summary
                aggregated_report['feature_summary'].append({
                    'id': feature.get('feature_id', 'unknown'),
                    'title': feature.get('title', 'Unknown Feature'),
                    'priority': feature.get('priority', 'Unknown'),
                    'feasibility': feasibility_info.get('feasibility_score', 0),
                    'story_points': feature.get('story_points', 0),
                    'included_in_sprint': True
                })
            
            # Add features not in sprint
            for assessment in feasibility_assessment.get('assessments', []):
                feature_id = assessment.get('feature_id')
                if not any(f.get('feature_id') == feature_id for f in sprint_plan.get('features', [])):
                    aggregated_report['feature_summary'].append({
                        'id': feature_id,
                        'title': assessment.get('title', 'Unknown Feature'),
                        'priority': 'Unknown',  # We don't have this info here
                        'feasibility': assessment.get('feasibility_score', 0),
                        'story_points': 0,  # We don't have this info here
                        'included_in_sprint': False
                    })
            
            logger.info("Report aggregation complete")
            return aggregated_report
        except Exception as e:
            logger.error(f"Error in report aggregation: {str(e)}")
            raise
    
    @staticmethod
    def presentation_generation(aggregated_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a stakeholder presentation from the aggregated report.
        
        Args:
            aggregated_report: Aggregated report from all agents
            
        Returns:
            Dictionary containing presentation content
        """
        logger.info("Generating stakeholder presentation")
        
        try:
            # Create presentation structure
            presentation = {
                'title': "SmartAssist Continuous Improvement Update",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slides': [
                    {
                        'title': "Executive Summary",
                        'content': [
                            "SmartAssist Continuous Improvement Cycle",
                            "Powered by Agentic AI System",
                            "",
                            *aggregated_report.get('key_insights', [])
                        ]
                    },
                    {
                        'title': "Feedback Analysis",
                        'content': [
                            f"Analyzed {aggregated_report.get('metrics', {}).get('feedback_items_analyzed', 0)} feedback items",
                            "Identified key pain points and improvement opportunities",
                            "Categorized feedback by feature area and severity"
                        ]
                    },
                    {
                        'title': "Feature Proposals",
                        'content': [
                            f"Generated {aggregated_report.get('metrics', {}).get('feature_proposals_generated', 0)} feature proposals",
                            "Prioritized based on user impact and business value",
                            "Aligned with product roadmap and strategic goals"
                        ]
                    },
                    {
                        'title': "Technical Assessment",
                        'content': [
                            f"Average feasibility score: {aggregated_report.get('metrics', {}).get('average_feasibility_score', 0):.1f}%",
                            "Evaluated implementation complexity and dependencies",
                            "Identified technical risks and mitigation strategies"
                        ]
                    },
                    {
                        'title': "Sprint Plan",
                        'content': [
                            f"Capacity utilization: {aggregated_report.get('metrics', {}).get('sprint_capacity_utilization', 0):.1f}%",
                            f"Features included in sprint: {len([f for f in aggregated_report.get('feature_summary', []) if f.get('included_in_sprint', False)])}",
                            "Balanced technical feasibility with business priority"
                        ]
                    },
                    {
                        'title': "Next Steps",
                        'content': [
                            "Review and approve sprint plan",
                            "Begin implementation of selected features",
                            "Continue monitoring user feedback",
                            "Next improvement cycle scheduled in 2 weeks"
                        ]
                    }
                ]
            }
            
            logger.info(f"Generated presentation with {len(presentation['slides'])} slides")
            return presentation
        except Exception as e:
            logger.error(f"Error in presentation generation: {str(e)}")
            raise
    
    @staticmethod
    def decision_matrix_creation(aggregated_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a decision matrix for stakeholders.
        
        Args:
            aggregated_report: Aggregated report from all agents
            
        Returns:
            Dictionary containing decision matrix
        """
        logger.info("Creating decision matrix for stakeholders")
        
        try:
            # Create decision matrix
            decision_matrix = {
                'timestamp': datetime.now().isoformat(),
                'matrix': []
            }
            
            # Add features to decision matrix
            for feature in aggregated_report.get('feature_summary', []):
                # Determine business impact based on priority
                priority = feature.get('priority', 'Low')
                if priority == 'Critical':
                    business_impact = 'Critical'
                elif priority == 'High':
                    business_impact = 'High'
                elif priority == 'Medium':
                    business_impact = 'Medium'
                else:
                    business_impact = 'Low'
                
                # Determine technical feasibility
                feasibility_score = feature.get('feasibility', 0)
                if feasibility_score >= 80:
                    technical_feasibility = 'High'
                elif feasibility_score >= 50:
                    technical_feasibility = 'Medium'
                else:
                    technical_feasibility = 'Low'
                
                # Determine resource requirement
                story_points = feature.get('story_points', 0)
                if story_points >= 13:
                    resource_requirement = 'High'
                elif story_points >= 8:
                    resource_requirement = 'Medium'
                else:
                    resource_requirement = 'Low'
                
                # Determine recommendation
                if business_impact == 'Critical' and technical_feasibility != 'Low':
                    recommendation = 'Approve'
                elif business_impact == 'High' and technical_feasibility == 'High':
                    recommendation = 'Approve'
                elif business_impact == 'High' and technical_feasibility == 'Medium':
                    recommendation = 'Consider'
                elif business_impact == 'Medium' and technical_feasibility == 'High':
                    recommendation = 'Consider'
                else:
                    recommendation = 'Defer'
                
                # Override recommendation if feature is already in sprint
                if feature.get('included_in_sprint', False):
                    recommendation = 'Approve'
                
                # Add to matrix
                decision_matrix['matrix'].append({
                    'feature_id': feature.get('id', 'unknown'),
                    'title': feature.get('title', 'Unknown Feature'),
                    'business_impact': business_impact,
                    'technical_feasibility': technical_feasibility,
                    'resource_requirement': resource_requirement,
                    'recommendation': recommendation,
                    'rationale': f"This feature has {business_impact.lower()} business impact and {technical_feasibility.lower()} technical feasibility, requiring {resource_requirement.lower()} resources."
                })
            
            logger.info(f"Created decision matrix with {len(decision_matrix['matrix'])} features")
            return decision_matrix
        except Exception as e:
            logger.error(f"Error in decision matrix creation: {str(e)}")
            raise
