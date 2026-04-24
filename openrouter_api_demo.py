"""
OpenRouter Gemini 3.1 Flash Image Update
Extracts generated URL and saves it to the local directory.
"""

import os
import re
import requests
import json
from openai import OpenAI
from datetime import datetime

def download_image(url, filename=None):
    """
    Downloads an image from a URL and saves it to the current directory.
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_gen_{timestamp}.png"
    
    try:
        # Get the current script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, filename)

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Image saved to: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"✗ Error downloading image: {str(e)}")
        return None

def generate_image(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        print(f"Generating image with prompt: '{prompt}'...")
        
        response = client.chat.completions.create(
            model="google/gemini-3.1-flash-image-preview",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://utica.edu", 
                "X-Title": "Cybersecurity Image Lab",
            }
        )

        content = response.choices[0].message.content
        
        # Regex to find a URL starting with http/https and ending in common image extensions
        # or simply look for the first URL in the markdown/text.
        urls = re.findall(r'(https?://[^\s]+)', content)
        
        if urls:
            # Take the first URL found and download it
            image_url = urls[0].strip('()[]') # Clean up markdown brackets if present
            local_file = download_image(image_url)
            return {'success': True, 'url': image_url, 'local_path': local_file}
        else:
            print("✗ No image URL found in the response content.")
            print(f"Raw content: {content}")
            return {'success': False, 'error': 'No URL found'}
            
    except Exception as e:
        print(f"✗ API Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    print("=" * 60)
    print("Gemini Image Gen & Auto-Save")
    print("=" * 60)
    
    # Example prompt for your Cybersecurity students
    user_prompt = "A high-tech digital forensic workstation with multiple monitors showing hex code and packet captures, cinematic lighting"
    
    result = generate_image(user_prompt)
    
    if result['success']:
        print("\nProcess Complete!")
        print(f"Image Link: {result['url']}")
        if result['local_path']:
            print(f"Local File: {os.path.basename(result['local_path'])}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
