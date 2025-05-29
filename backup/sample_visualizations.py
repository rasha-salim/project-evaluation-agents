import streamlit.components.v1 as components

def render_sample_technical_evaluation():
    """Render a sample technical evaluation visualization"""
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Technical Feasibility Assessment</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 20px;">
            <div style="flex: 1; min-width: 300px; max-width: 400px; background-color: #f9f9f9; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0; color: #333; text-align: center;">Dark Mode Implementation</h4>
                <div style="position: relative; width: 100%; height: 200px; margin: 0 auto;">
                    <svg width="100%" height="100%" viewBox="0 0 200 200">
                        <!-- Pentagon background -->
                        <polygon points="100,10 190,75 155,180 45,180 10,75" fill="#f0f0f0" stroke="#ccc" />
                        
                        <!-- Rating lines -->
                        <polygon points="100,82 136,115 124,156 76,156 64,115" fill="none" stroke="#ddd" />
                        <polygon points="100,46 172,95 140,168 60,168 28,95" fill="none" stroke="#ddd" />
                        <polygon points="100,28 181,85 147,174 53,174 19,85" fill="none" stroke="#ddd" />
                        <polygon points="100,10 190,75 155,180 45,180 10,75" fill="none" stroke="#ddd" />
                        
                        <!-- Data pentagon -->
                        <polygon points="100,46 154,95 132,150 68,150 46,95" fill="#4CAF5080" stroke="#4CAF50" stroke-width="2" />
                        
                        <!-- Labels -->
                        <text x="100" y="0" text-anchor="middle" dy="1em" font-size="10" fill="#333">Technical Complexity</text>
                        <text x="200" y="75" text-anchor="start" dy="0.3em" font-size="10" fill="#333">Feasibility</text>
                        <text x="155" y="190" text-anchor="middle" dy="-0.5em" font-size="10" fill="#333">Risk Level</text>
                        <text x="45" y="190" text-anchor="middle" dy="-0.5em" font-size="10" fill="#333">Effort Required</text>
                        <text x="0" y="75" text-anchor="end" dy="0.3em" font-size="10" fill="#333">Overall Score</text>
                        
                        <!-- Value indicators -->
                        <circle cx="100" cy="46" r="3" fill="#4CAF50" />
                        <circle cx="154" cy="95" r="3" fill="#4CAF50" />
                        <circle cx="132" cy="150" r="3" fill="#4CAF50" />
                        <circle cx="68" cy="150" r="3" fill="#4CAF50" />
                        <circle cx="46" cy="95" r="3" fill="#4CAF50" />
                    </svg>
                </div>
            </div>
            
            <div style="flex: 1; min-width: 300px; max-width: 400px; background-color: #f9f9f9; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0; color: #333; text-align: center;">Search Improvements</h4>
                <div style="position: relative; width: 100%; height: 200px; margin: 0 auto;">
                    <svg width="100%" height="100%" viewBox="0 0 200 200">
                        <!-- Pentagon background -->
                        <polygon points="100,10 190,75 155,180 45,180 10,75" fill="#f0f0f0" stroke="#ccc" />
                        
                        <!-- Rating lines -->
                        <polygon points="100,82 136,115 124,156 76,156 64,115" fill="none" stroke="#ddd" />
                        <polygon points="100,46 172,95 140,168 60,168 28,95" fill="none" stroke="#ddd" />
                        <polygon points="100,28 181,85 147,174 53,174 19,85" fill="none" stroke="#ddd" />
                        <polygon points="100,10 190,75 155,180 45,180 10,75" fill="none" stroke="#ddd" />
                        
                        <!-- Data pentagon -->
                        <polygon points="100,64 145,95 128,150 72,150 55,95" fill="#FFC10780" stroke="#FFC107" stroke-width="2" />
                        
                        <!-- Labels -->
                        <text x="100" y="0" text-anchor="middle" dy="1em" font-size="10" fill="#333">Technical Complexity</text>
                        <text x="200" y="75" text-anchor="start" dy="0.3em" font-size="10" fill="#333">Feasibility</text>
                        <text x="155" y="190" text-anchor="middle" dy="-0.5em" font-size="10" fill="#333">Risk Level</text>
                        <text x="45" y="190" text-anchor="middle" dy="-0.5em" font-size="10" fill="#333">Effort Required</text>
                        <text x="0" y="75" text-anchor="end" dy="0.3em" font-size="10" fill="#333">Overall Score</text>
                        
                        <!-- Value indicators -->
                        <circle cx="100" cy="64" r="3" fill="#FFC107" />
                        <circle cx="145" cy="95" r="3" fill="#FFC107" />
                        <circle cx="128" cy="150" r="3" fill="#FFC107" />
                        <circle cx="72" cy="150" r="3" fill="#FFC107" />
                        <circle cx="55" cy="95" r="3" fill="#FFC107" />
                    </svg>
                </div>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 30px; margin-bottom: 20px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Implementation Difficulty</h3>
        <div style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 150px; text-align: right; padding-right: 15px; font-weight: 500;">File Upload System</div>
                    <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                        <div style="width: 90%; height: 100%; background-color: #F44336; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: 500;">
                            Very Difficult
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 150px; text-align: right; padding-right: 15px; font-weight: 500;">Search Improvements</div>
                    <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                        <div style="width: 60%; height: 100%; background-color: #FFC107; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: 500;">
                            Moderate
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 150px; text-align: right; padding-right: 15px; font-weight: 500;">Dark Mode</div>
                    <div style="flex-grow: 1; background-color: #E0E0E0; height: 24px; border-radius: 12px; overflow: hidden;">
                        <div style="width: 40%; height: 100%; background-color: #4CAF50; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: 500;">
                            Easy
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    components.html(html, height=600)

def render_sample_stakeholder_update():
    """Render a sample stakeholder update visualization"""
    html = '''
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; color: #333; border-bottom: 2px solid #673AB7; padding-bottom: 8px;">Project Progress Overview</h3>
        
        <!-- Progress Circle -->
        <div style="display: flex; flex-wrap: wrap; align-items: center; margin-top: 20px;">
            <div style="flex: 0 0 200px; position: relative; margin: 0 auto;">
                <svg width="200" height="200" viewBox="0 0 200 200">
                    <!-- Background circle -->
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="15"/>
                    
                    <!-- Progress circle -->
                    <circle cx="100" cy="100" r="90" fill="none" stroke="#4CAF50" stroke-width="15"
                            stroke-dasharray="565.48" stroke-dashoffset="339.29"
                            transform="rotate(-90 100 100)"/>
                            
                    <!-- Percentage text -->
                    <text x="100" y="100" text-anchor="middle" dominant-baseline="middle" font-size="36" font-weight="bold" fill="#333">
                        40%
                    </text>
                    <text x="100" y="130" text-anchor="middle" dominant-baseline="middle" font-size="14" fill="#666">
                        Complete
                    </text>
                </svg>
            </div>
            
            <!-- Feature Status Breakdown -->
            <div style="flex: 1; min-width: 300px; margin-left: 20px;">
                <div style="margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #333; margin-bottom: 15px;">Feature Status</h4>
                    
                    <!-- Completed Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">Completed</div>
                            <div>4 of 10</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: 40%; height: 100%; background-color: #4CAF50;"></div>
                        </div>
                    </div>
                    
                    <!-- In Progress Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">In Progress</div>
                            <div>3 of 10</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: 30%; height: 100%; background-color: #2196F3;"></div>
                        </div>
                    </div>
                    
                    <!-- Planned Features -->
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: 500;">Planned</div>
                            <div>3 of 10</div>
                        </div>
                        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="width: 30%; height: 100%; background-color: #FF9800;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 20px; margin-bottom: 30px;">
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
            <div style="flex: 1; min-width: 300px; background-color: #E8F5E9; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 8px;">Key Achievements</h3>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    <li style="margin-bottom: 10px;">Completed Dark Mode implementation</li>
                    <li style="margin-bottom: 10px;">Improved search functionality with partial matching</li>
                    <li style="margin-bottom: 10px;">Fixed critical performance issues on large files</li>
                    <li style="margin-bottom: 10px;">Added user preference storage</li>
                </ul>
            </div>
            
            <div style="flex: 1; min-width: 300px; background-color: #FFF3E0; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #E65100; border-bottom: 2px solid #E65100; padding-bottom: 8px;">Challenges</h3>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    <li style="margin-bottom: 10px;">File upload system complexity is higher than anticipated</li>
                    <li style="margin-bottom: 10px;">Battery optimization requires additional testing</li>
                    <li style="margin-bottom: 10px;">Integration with legacy systems taking longer than expected</li>
                </ul>
            </div>
            
            <div style="flex: 1; min-width: 300px; background-color: #E3F2FD; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #1565C0; border-bottom: 2px solid #1565C0; padding-bottom: 8px;">Next Steps</h3>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    <li style="margin-bottom: 10px;">Complete file upload system implementation</li>
                    <li style="margin-bottom: 10px;">Begin work on analytics dashboard</li>
                    <li style="margin-bottom: 10px;">Implement notification system improvements</li>
                    <li style="margin-bottom: 10px;">Start planning for custom themes feature</li>
                </ul>
            </div>
        </div>
    </div>
    '''
    
    components.html(html, height=700)
