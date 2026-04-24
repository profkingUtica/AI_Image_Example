"""
OpenRouter Gemini 3.1 Flash Image Update
Added: persistent logging to 'image_gen.log' to capture success/failure history.
"""

import os
import re
import requests
import logging
from openai import OpenAI
from datetime import datetime

# --- LOGGING CONFIGURATION ---
# This setup ensures logs are written to a file and also show up in your terminal.
current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, "image_gen.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Saves to file
        logging.StreamHandler()         # Also prints to terminal
    ]
)
logger = logging.getLogger(__name__)

# --- HELPER FUNCTIONS ---

def download_image(url, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_gen_{timestamp}.png"
    
    try:
        save_path = os.path.join(current_dir, filename)
        logger.info(f"Attempting download from URL: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"SUCCESS: Image saved as {filename}")
        return save_path
        
    except Exception as e:
        logger.error(f"FAILURE: Download failed for {url}. Error: {str(e)}")
        return None

# --- MAIN GENERATION FUNCTION ---

def generate_image(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        err_msg = "OPENROUTER_API_KEY environment variable not set"
        logger.critical(err_msg)
        raise ValueError(err_msg)
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        logger.info(f"REQUEST: Starting generation for prompt: '{prompt}'")
        
        response = client.chat.completions.create(
            model="black-forest-labs/flux.2-klein-4b",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://utica.edu", 
                "X-Title": "Cybersecurity Image Lab",
            }
        )

        content = response.choices[0].message.content

        if not content:
            logger.warning("FAILURE: API returned empty content field.")
            return {'success': False, 'error': 'Empty content'}

        # Find URL in response
        urls = re.findall(r'(https?://[^\s]+)', content)
        
        if urls:
            image_url = urls[0].strip('()[]')
            logger.info(f"URL FOUND: {image_url}")
            
            local_file = download_image(image_url)
            
            if local_file:
                return {'success': True, 'url': image_url, 'local_path': local_file}
            else:
                return {'success': False, 'error': 'Download failed'}
        else:
            logger.warning(f"FAILURE: No URL found in content: {content[:100]}...")
            return {'success': False, 'error': 'No URL in text'}
            
    except Exception as e:
        logger.error(f"EXCEPTION: API Call failed. Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    logger.info("--- Starting New Demo Run ---")
    
    user_prompt = "A futuristic digital rose, cinematic lighting"
    result = generate_image(user_prompt)
    
    if result['success']:
        logger.info(f"RUN COMPLETE: Image ready at {result['local_path']}")
    else:
        logger.error(f"RUN COMPLETE: Failed with reason: {result['error']}")

if __name__ == "__main__":
    main()
