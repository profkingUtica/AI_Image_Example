"""
OpenRouter Flux.2 Klein Update
Fixed: Detects image URLs in multi-modal responses even when 'content' is empty.
"""

import os
import re
import requests
import logging
from openai import OpenAI
from datetime import datetime

# --- LOGGING CONFIG ---
current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, "image_gen.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def download_image(url, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flux_gen_{timestamp}.png"
    
    try:
        save_path = os.path.join(current_dir, filename)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"SUCCESS: Image saved as {filename}")
        return save_path
    except Exception as e:
        logger.error(f"FAILURE: Download failed. Error: {str(e)}")
        return None

def generate_image(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    
    try:
        logger.info(f"REQUEST: Generating via Flux.2 Klein: '{prompt}'")
        
        # 2026 Requirement: Explicitly request image modality
        response = client.chat.completions.create(
            model="black-forest-labs/flux.2-klein-4b",
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "modalities": ["image"] # Tells OpenRouter to expect image data
            },
            extra_headers={
                "HTTP-Referer": "https://utica.edu",
                "X-Title": "Cybersecurity Image Lab"
            }
        )

        message = response.choices[0].message
        image_url = None

        # 1. Check for the new 2026 'images' field in the message object
        if hasattr(message, 'images') and message.images:
            image_url = message.images[0].url
            logger.info("Found URL in 'images' metadata field.")

        # 2. Fallback: Search the content field if it's not empty
        if not image_url and message.content:
            urls = re.findall(r'(https?://[^\s]+)', message.content)
            if urls:
                image_url = urls[0].strip('()[]')
                logger.info("Found URL in text content field.")

        if image_url:
            local_file = download_image(image_url)
            return {'success': True, 'url': image_url, 'local_path': local_file}
        else:
            logger.warning(f"FAILURE: No URL found. Finish Reason: {response.choices[0].finish_reason}")
            return {'success': False, 'error': 'No image URL returned'}
            
    except Exception as e:
        logger.error(f"EXCEPTION: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    logger.info("--- Starting New Demo Run ---")
    user_prompt = "A futuristic digital rose, cinematic lighting"
    result = generate_image(user_prompt)
    if result['success']:
        logger.info(f"RUN COMPLETE: SUCCESS - {os.path.basename(result['local_path'])}")
    else:
        logger.error(f"RUN COMPLETE: FAILED - {result['error']}")

if __name__ == "__main__":
    main()
