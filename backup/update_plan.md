# Plan to Update Main App with DirectAnthropicExecutor

## Problem Summary
The main app is encountering issues with CrewAI defaulting to OpenAI despite being configured to use Anthropic. This is causing errors like:
- "Error running agents: 'str' object has no attribute 'get'"
- "Error running agents: litellm.RateLimitError: RateLimitError: OpenAIException - You exceeded your current quota"

## Solution Approach
We've created a `DirectAnthropicExecutor` class that bypasses CrewAI's LLM handling and uses the Anthropic API directly. We need to integrate this into the main app.

## Implementation Steps

1. **Update the run_sequential method in crew.py**
   - Replace the crew.kickoff() call with direct task execution using DirectAnthropicExecutor
   - Maintain the same workflow but execute tasks individually

2. **Update the run_parallel method in crew.py**
   - Similar to sequential, but handle task dependencies manually

3. **Update the run_autonomous method in crew.py**
   - This is more complex as it has iteration logic
   - We'll need to adapt the iteration logic to work with DirectAnthropicExecutor

4. **Ensure all agent initializations use proper Anthropic configuration**
   - Standardize the LLM configuration across all agents

5. **Test the updated app**
   - Run the app with the new implementation
   - Verify that it works with Anthropic and doesn't try to use OpenAI

## Expected Outcome
- The app will run successfully using the Anthropic API
- No more OpenAI-related errors
- Maintained functionality of the original app
