"""
OpenAI DALL-E Image Generation Demo
Demonstrates API authentication, request handling, and error management
"""

import os
from openai import OpenAI
import requests
import json
from datetime import datetime

def generate_image(prompt, size="1024x1024", quality="standard", n=1):
    """
    Generate an image using OpenAI's DALL-E API
    
    Args:
        prompt (str): Description of the image to generate
        size (str): Image size - "1024x1024", "1792x1024", or "1024x1792"
        quality (str): "standard" or "hd"
        n (int): Number of images to generate (1-10)
    
    Returns:
        dict: Response containing image URL(s) and metadata
    """
    
    # Initialize the OpenAI client
    # API key should be stored in environment variable for security
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = OpenAI(api_key=api_key)
    
    try:
        print(f"Generating image with prompt: '{prompt}'")
        print(f"Parameters: size={size}, quality={quality}, n={n}\n")
        
        # Make the API call
        response = client.images.generate(
            model="dall-e-3",  # or "dall-e-2" for the older model
            prompt=prompt,
            size=size,
            quality=quality,
            n=n
        )
        
        # Display raw JSON response for educational purposes
        print("=" * 60)
        print("RAW API RESPONSE (JSON):")
        print("=" * 60)
        
        # Convert response object to dictionary for JSON display
        response_dict = {
            'created': response.created,
            'data': [
                {
                    'url': img.url,
                    'revised_prompt': getattr(img, 'revised_prompt', None)
                }
                for img in response.data
            ]
        }
        
        print(json.dumps(response_dict, indent=2))
        print("=" * 60 + "\n")
        
        # Extract image URLs from response
        images = []
        for img in response.data:
            images.append({
                'url': img.url,
                'revised_prompt': getattr(img, 'revised_prompt', None)
            })
        
        print(f"✓ Successfully generated {len(images)} image(s)")
        return {
            'success': True,
            'images': images,
            'created': response.created
        }
        
    except Exception as e:
        print(f"✗ Error generating image: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def download_image(url, filename=None):
    """
    Download image from URL to local file
    
    Args:
        url (str): Image URL
        filename (str): Optional custom filename
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Image saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"✗ Error downloading image: {str(e)}")
        return None


def main():
    """
    Main demonstration function
    """
    print("=" * 60)
    print("OpenAI DALL-E Image Generation Demo")
    print("=" * 60 + "\n")
    
    # Example 1: Basic image generation
    prompt = "A cybersecurity professional analyzing data on holographic screens in a futuristic command center"
    
    result = generate_image(
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    
    if result['success']:
        print("\nGenerated Image Details:")
        print("-" * 60)
        for i, img in enumerate(result['images'], 1):
            print(f"\nImage {i}:")
            print(f"URL: {img['url']}")
            if img['revised_prompt']:
                print(f"Revised Prompt: {img['revised_prompt']}")
            
            # Download the image
            download_image(img['url'], f"cybersecurity_demo_{i}.png")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
