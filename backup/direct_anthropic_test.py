import os
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Test direct Anthropic API access"""
    print("Testing direct Anthropic API access")
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: No Anthropic API key found in environment variables")
        return
    
    print(f"API key exists: {bool(api_key)}")
    print(f"API key (first 5 chars): {api_key[:5]}...")
    
    try:
        # Create Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Make a simple API call
        print("\nSending request to Anthropic API...")
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say hello and identify yourself as an Anthropic Claude model."}
            ]
        )
        
        # Print response
        print(f"\nResponse from Anthropic API:")
        print(message.content[0].text)
        
        print("\nTest completed successfully")
    except Exception as e:
        print(f"Error accessing Anthropic API: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
