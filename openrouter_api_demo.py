"""
OpenRouter Image Generation Demo - Gemini 3.1 Flash Update
Demonstrates the correct Chat Completions approach for Gemini Image Generation
"""

import os
from openai import OpenAI
import requests
import json
from datetime import datetime

def generate_image(prompt):
    """
    Generate an image using OpenRouter's Chat Completion endpoint.
    Note: Gemini 3.1 Flash Image Preview via OpenRouter uses the chat interface 
    to return image data/URLs.
    """
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    # Initialize the client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        print(f"Generating image with prompt: '{prompt}'")
        
        # Gemini 3.1 Flash Image generation on OpenRouter is typically 
        # handled via the completions endpoint.
        response = client.chat.completions.create(
            model="google/gemini-3.1-flash-image-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://utica.edu", 
                "X-Title": "Cybersecurity Educator Tools",
            }
        )

        # Log the response for debugging
        print("=" * 60)
        print("API RESPONSE RECEIVED")
        print("=" * 60)

        # Extract the image information from the message content
        # OpenRouter returns the image URL within the choice content for this model
        content = response.choices[0].message.content
        
        # In many implementations, the image is provided as a URL or a markdown link
        # We will return the result to be processed
        print(f"✓ Response content received.")
        
        return {
            'success': True,
            'content': content,
            'raw': response
        }
        
    except Exception as e:
        print(f"✗ Error generating image: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("=" * 60)
    print("OpenRouter Gemini 3.1 Flash Image Demo")
    print("=" * 60 + "\n")
    
    # Example prompt relevant to your cybersecurity curriculum
    prompt = "A high-resolution technical diagram of a secure network architecture with a hardware firewall and DMZ, 3d isometric style"
    
    result = generate_image(prompt)
    
    if result['success']:
        print("\nGeneration Result:")
        print("-" * 60)
        print(result['content'])
    else:
        print(f"Failed to generate: {result['error']}")

if __name__ == "__main__":
    main()
