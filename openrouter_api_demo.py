"""
OpenRouter Gemini 3.1 Flash Image Update
Fixed: NameError on 'response' and moved debug line inside the function scope.
"""

import os
import re
import requests
import json
from openai import OpenAI
from datetime import datetime

# --- HELPER FUNCTIONS ---

def download_image(url, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_gen_{timestamp}.png"
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, filename)

        print(f"Attempting to download image to: {save_path}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Image successfully saved to: {filename}")
        return save_path
        
    except Exception as e:
        print(f"✗ Error downloading image: {str(e)}")
        return None

# --- MAIN GENERATION FUNCTION ---

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

        # DEBUG LINE MOVED HERE: Now 'response' is correctly defined in this scope
        print(f"DEBUG: Raw Choice Object: {response.choices[0]}")

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            print("✗ API Response structure is unexpected.")
            return {'success': False, 'error': f'Invalid response structure: {str(e)}'}

        if not content:
            print("✗ API returned an empty text content.")
            return {'success': False, 'error': 'API returned empty content.'}

        urls = re.findall(r'(https?://[^\s]+)', content)
        
        if urls:
            image_url = urls[0].strip('()[]')
            print(f"✓ URL found: {image_url}")
            local_file = download_image(image_url)
            
            if local_file:
                return {'success': True, 'url': image_url, 'local_path': local_file}
            else:
                return {'success': False, 'error': 'Download failed.'}
        else:
            print(f"✗ No image URL found. Content was: \"{content}\"")
            return {'success': False, 'error': 'No valid URL found in text.'}
            
    except Exception as e:
        print(f"✗ Unexpected API Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    print("=" * 60)
    print("Gemini Image Gen & Auto-Save (Fixed)")
    print("=" * 60)
    
    user_prompt = "A high-tech digital forensic workstation, cinematic lighting"
    result = generate_image(user_prompt)
    
    print("\n" + "-" * 60)
    if result['success']:
        print(f"PROCESS COMPLETE: SUCCESS\nLocal File: {os.path.basename(result['local_path'])}")
    else:
        print(f"PROCESS COMPLETE: FAILED\nReason: {result['error']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
