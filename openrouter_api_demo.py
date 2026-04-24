"""
OpenRouter Flux.2 Klein Update - Dict Access Fix
Fixed: Dictionary key access for 'images' field and Base64 support.
"""

import os
import re
import requests
import logging
import base64
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

def save_base64_image(b64_string, filename):
    """Decodes and saves base64 image data."""
    try:
        save_path = os.path.join(current_dir, filename)
        # Remove header if present (e.g., data:image/png;base64,)
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(b64_string))
        logger.info(f"SUCCESS: Base64 image saved as {filename}")
        return save_path
    except Exception as e:
        logger.error(f"FAILURE: Base64 save failed. {str(e)}")
        return None

def download_image(url, filename):
    """Downloads image from a remote URL."""
    try:
        save_path = os.path.join(current_dir, filename)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"SUCCESS: Remote image saved as {filename}")
        return save_path
    except Exception as e:
        logger.error(f"FAILURE: Download failed. {str(e)}")
        return None

def generate_image(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    
    # Standardized filename for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"flux_gen_{timestamp}.png"

    try:
        logger.info(f"REQUEST: Generating via Flux.2 Klein: '{prompt}'")
        
        response = client.chat.completions.create(
            model="black-forest-labs/flux.2-klein-4b",
            messages=[{"role": "user", "content": prompt}],
            extra_body={"modalities": ["image"]},
            extra_headers={"X-Title": "Cybersecurity Image Lab"}
        )

        message = response.choices[0].message
        image_data = None

        # 1. 2026 DICTIONARY ACCESS: Look for 'images' list
        if hasattr(message, 'images') and message.images:
            img_obj = message.images[0]
            
            # Use .get() for safe dictionary access
            if isinstance(img_obj, dict):
                if img_obj.get('url'):
                    url = img_obj['url']
                    if url.startswith('data:image'):
                        return {'success': True, 'local_path': save_base64_image(url, filename)}
                    return {'success': True, 'local_path': download_image(url, filename)}
            
            # Fallback for older SDK object versions
            elif hasattr(img_obj, 'url'):
                return {'success': True, 'local_path': download_image(img_obj.url, filename)}

        # 2. Fallback: Search the content field
        if message.content:
            urls = re.findall(r'(https?://[^\s]+)', message.content)
            if urls:
                url = urls[0].strip('()[]')
                return {'success': True, 'local_path': download_image(url, filename)}

        logger.warning("FAILURE: Response received but no image URL/data found.")
        return {'success': False, 'error': 'No image data in response'}
            
    except Exception as e:
        logger.error(f"EXCEPTION: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    logger.info("--- Starting New Demo Run ---")
    result = generate_image("A futuristic digital rose, cinematic lighting")
    
    if result.get('success') and result.get('local_path'):
        logger.info(f"RUN COMPLETE: Saved to {os.path.basename(result['local_path'])}")
    else:
        logger.error(f"RUN COMPLETE: FAILED - {result.get('error')}")

if __name__ == "__main__":
    main()
