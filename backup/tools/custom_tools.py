"""
Custom tools for Project Evolution Agents.
These tools enable agents to process data, generate reports, and perform specialized tasks.
"""

import os
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackTools:
    """Tools for the Feedback Analyst Agent to process and analyze user feedback."""
    
    @staticmethod
    def read_csv(file_path: str) -> pd.DataFrame:
        """
        Read and validate feedback data from CSV file.
        
        Args:
            file_path: Path to the CSV file containing feedback data
            
        Returns:
            DataFrame containing the feedback data
        """
        logger.info(f"Reading feedback data from {file_path}")
        try:
            df = pd.read_csv(file_path)
            required_columns = ['date', 'user_id', 'feedback_type', 'description', 'severity', 'feature_area']
            
            # Check if all required columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'])
            
            # Validate severity (should be 1-5)
            if not all(df['severity'].between(1, 5)):
                logger.warning("Some severity values are outside the expected range (1-5)")
                
            logger.info(f"Successfully loaded {len(df)} feedback entries")
            return df
        except Exception as e:
            logger.error(f"Error reading feedback data: {str(e)}")
            raise
    
    @staticmethod
    def analyze_feedback(feedback_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze feedback data to identify patterns and insights.
        
        Args:
            feedback_data: DataFrame containing feedback data
            
        Returns:
            Dictionary containing categorized insights and pain points
        """
        logger.info("Analyzing feedback data")
        
        try:
            # Group feedback by type and feature area
            type_counts = feedback_data['feedback_type'].value_counts().to_dict()
            area_counts = feedback_data['feature_area'].value_counts().to_dict()
            
            # Calculate average severity by feature area
            severity_by_area = feedback_data.groupby('feature_area')['severity'].mean().to_dict()
            
            # Identify high severity items
            high_severity = feedback_data[feedback_data['severity'] >= 4]
            high_severity_count = len(high_severity)
            
            # Extract common themes from descriptions
            # This is a simplified version - in a real implementation, 
            # you might use NLP techniques like topic modeling
            
            # For demonstration, we'll just group by feature_area and feedback_type
            categories = []
            for area in feedback_data['feature_area'].unique():
                area_data = feedback_data[feedback_data['feature_area'] == area]
                for feedback_type in area_data['feedback_type'].unique():
                    type_data = area_data[area_data['feedback_type'] == feedback_type]
                    
                    # Get examples (up to 3)
                    examples = type_data['description'].sample(min(3, len(type_data))).tolist()
                    
                    # Create category entry
                    categories.append({
                        'category': f"{area} - {feedback_type}",
                        'count': len(type_data),
                        'severity': type_data['severity'].mean(),
                        'insights': [
                            f"Users report issues with {area} when performing {feedback_type} actions",
                            f"Average severity is {type_data['severity'].mean():.1f}/5"
                        ],
                        'examples': examples
                    })
            
            # Create the analysis report
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_feedback_count': len(feedback_data),
                'date_range': {
                    'start': feedback_data['date'].min().isoformat(),
                    'end': feedback_data['date'].max().isoformat()
                },
                'summary': {
                    'feedback_types': type_counts,
                    'feature_areas': area_counts,
                    'high_severity_count': high_severity_count
                },
                'categories': categories
            }
            
            logger.info(f"Feedback analysis complete. Identified {len(categories)} categories.")
            return report
        except Exception as e:
            logger.error(f"Error analyzing feedback: {str(e)}")
            raise
    
    @staticmethod
    def generate_report(analysis: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Generate a structured report from feedback analysis.
        
        Args:
            analysis: Dictionary containing feedback analysis
            output_path: Optional path to save the report JSON
            
        Returns:
            Path to the saved report or the report as a JSON string
        """
        logger.info("Generating feedback analysis report")
        
        try:
            # Format the report
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'data_period': analysis['date_range']
                },
                'categories': analysis['categories']
            }
            
            # Add summary statistics
            report['summary'] = {
                'total_feedback_items': analysis['total_feedback_count'],
                'category_count': len(analysis['categories']),
                'average_severity': sum(cat['severity'] for cat in analysis['categories']) / len(analysis['categories']),
                'top_categories': sorted(
                    analysis['categories'], 
                    key=lambda x: x['severity'] * x['count'], 
                    reverse=True
                )[:3]
            }
            
            # Save to file if output path provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Report saved to {output_path}")
                return output_path
            
            # Otherwise return as JSON string
            return json.dumps(report, indent=2)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise


class FeatureTools:
    """Tools for the Feature Strategist Agent to generate and prioritize feature proposals."""
    
    @staticmethod
    def read_report(report_path: str) -> Dict[str, Any]:
        """
        Read a feedback analysis report.
        
        Args:
            report_path: Path to the feedback analysis report JSON
            
        Returns:
            Dictionary containing the report data
        """
        logger.info(f"Reading feedback analysis report from {report_path}")
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            logger.info("Successfully loaded feedback analysis report")
            return report
        except Exception as e:
            logger.error(f"Error reading report: {str(e)}")
            raise
    
    @staticmethod
    def prioritize_features(feedback_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate and prioritize feature proposals based on feedback.
        
        Args:
            feedback_report: Dictionary containing feedback analysis
            
        Returns:
            List of prioritized feature proposals
        """
        logger.info("Generating feature proposals")
        
        try:
            # Extract categories from the report
            categories = feedback_report['categories']
            
            # Generate feature proposals based on feedback categories
            features = []
            feature_id = 1
            
            for category in sorted(categories, key=lambda x: x['severity'] * x['count'], reverse=True):
                # Calculate impact score (simplified version)
                impact_score = min(100, category['severity'] * 20)
                
                # Determine priority based on impact score
                if impact_score >= 80:
                    priority = "Critical"
                elif impact_score >= 60:
                    priority = "High"
                elif impact_score >= 40:
                    priority = "Medium"
                else:
                    priority = "Low"
                
                # Create a feature proposal
                feature = {
                    'id': f"F{feature_id:03d}",
                    'title': f"Improve {category['category']}",
                    'description': f"Address user feedback regarding {category['category']} based on {category['count']} feedback items with average severity {category['severity']:.1f}/5.",
                    'addressing_categories': [category['category']],
                    'impact_score': impact_score,
                    'priority': priority,
                    'rationale': f"This feature addresses {category['count']} feedback items with an average severity of {category['severity']:.1f}/5. Example feedback: {category['examples'][0] if category['examples'] else 'N/A'}"
                }
                
                features.append(feature)
                feature_id += 1
            
            logger.info(f"Generated {len(features)} feature proposals")
            return features
        except Exception as e:
            logger.error(f"Error prioritizing features: {str(e)}")
            raise
    
    @staticmethod
    def impact_analysis(features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform impact analysis on proposed features.
        
        Args:
            features: List of feature proposals
            
        Returns:
            Dictionary containing impact analysis results
        """
        logger.info("Performing impact analysis on feature proposals")
        
        try:
            # Calculate total impact score
            total_impact = sum(feature['impact_score'] for feature in features)
            
            # Count features by priority
            priority_counts = {}
            for feature in features:
                priority = feature['priority']
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Create the impact analysis
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'total_features': len(features),
                'total_impact_score': total_impact,
                'average_impact_score': total_impact / len(features) if features else 0,
                'priority_distribution': priority_counts,
                'features': features
            }
            
            logger.info("Impact analysis complete")
            return analysis
        except Exception as e:
            logger.error(f"Error in impact analysis: {str(e)}")
            raise
