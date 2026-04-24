"""
OpenRouter Gemini 3.1 Flash Image Update
Adds safety checks to prevent 'expected string or bytes-like object' error.
Extracts generated URL and saves it to the local directory.
"""

import os
import re
import requests
import json
from openai import OpenAI
from datetime import datetime

# --- HELPER FUNCTIONS ---

def download_image(url, filename=None):
    """
    Downloads an image from a URL and saves it to the current directory.
    """
    if not filename:
        # Create a safe, timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_gen_{timestamp}.png"
    
    try:
        # Get the current script's directory for the save path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(current_dir, filename)

        print(f"Attempting to download image to: {save_path}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Image successfully saved to: {filename}")
        return save_path
        
    except requests.exceptions.RequestException as re:
        print(f"✗ Error during download request: {str(re)}")
        return None
    except IOError as ioe:
        print(f"✗ Error writing file: {str(ioe)}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error downloading image: {str(e)}")
        return None

# --- MAIN GENERATION FUNCTION ---

def generate_image(prompt):
    """
    Generates an image via OpenRouter and Gemini 3.1 Flash.
    Includes robustness checks to handle unexpected API responses.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        print(f"Generating image with prompt: '{prompt}'...")
        
        # Make the API call
        response = client.chat.completions.create(
            model="openai/gpt-5.4-image-2",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://utica.edu", 
                "X-Title": "Cybersecurity Image Lab",
            }
        )

        # 1. Safely extract the message content
        # We need to handle cases where the API returns an unusual or empty response.
        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            # If the response object doesn't have the expected structure
            print("✗ API Response structure is unexpected.")
            # For debugging: print(f"Raw API Response Object: {response}")
            return {'success': False, 'error': f'Invalid response structure: {str(e)}'}

        # =========================================================================
        # 2. THE FIX: Validate content before calling re.findall
        # =========================================================================
        if not content:
            # content is None or an empty string, which is the root of the original crash.
            print("✗ API returned an empty text content. This sometimes happens with 'preview' models.")
            # This is a successful API call, but we have no data to act on.
            return {'success': False, 'error': 'API returned empty content. No image generated.'}

        # content is validated as a non-empty string, so re.findall is now safe to use.
        print("✓ API content received. Searching for image URL...")

        # Regex to find a URL starting with http/https
        urls = re.findall(r'(https?://[^\s]+)', content)
        
        if urls:
            # Take the first URL found and download it
            image_url = urls[0].strip('()[]') # Clean up potential markdown brackets
            print(f"✓ URL found: {image_url}")
            
            # Pass to the download helper
            local_file = download_image(image_url)
            
            if local_file:
                # Full success path
                return {'success': True, 'url': image_url, 'local_path': local_file}
            else:
                # The image generation worked, but the download part failed
                return {'success': False, 'error': 'Image generated, but file download failed.'}

        else:
            print("✗ No image URL found within the API response content.")
            print(f"Raw content was: \"{content}\"")
            return {'success': False, 'error': 'No valid URL found in text.'}
            
    except requests.exceptions.RequestException as re_err:
        # Handle connection issues to the OpenRouter API itself
        print(f"✗ OpenRouter API connection error: {str(re_err)}")
        return {'success': False, 'error': f'API Connection error: {str(re_err)}'}
    except Exception as e:
        # Catch any other unexpected errors
        print(f"✗ Unexpected API Error: {str(e)}")
        return {'success': False, 'error': str(e)}

# --- MAIN EXECUTION BLOCK ---

def main():
    print("=" * 60)
    print("Gemini Image Gen & Auto-Save (Fixed)")
    print("=" * 60)
    
    # Define your prompt (reused your previous one as a good example)
    user_prompt = "Generate and provide a direct URL for an image of: A high-tech digital forensic workstation with multiple monitors showing hex code and packet captures, cinematic lighting"
    
    # Run the robust generation process
    result = generate_image(user_prompt)
    
    # Process the final result dictionary
    print("\n" + "-" * 60)
    if result['success']:
        print("PROCESS COMPLETE: SUCCESS")
        print(f"  Remote URL: {result['url']}")
        if result['local_path']:
            # os.path.basename prints only 'filename.png', not 'C:\\path\\to\\filename.png'
            print(f"  Local File: {os.path.basename(result['local_path'])}")
    else:
        print("PROCESS COMPLETE: FAILED")
        print(f"  Reason: {result['error']}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
