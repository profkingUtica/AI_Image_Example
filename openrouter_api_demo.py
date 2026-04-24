"""
OpenRouter 2026 Multi-Modal Update
Fixed: Nested dictionary access for Flux.2 and Gemini models.
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

def save_image_data(data, filename):
    """Handles both URL downloads and Base64 decoding."""
    save_path = os.path.join(current_dir, filename)
    try:
        if data.startswith('http'):
            response = requests.get(data, timeout=30)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
        elif 'base64,' in data or len(data) > 1000: # Assume Base64
            header_removed = data.split(",")[1] if "," in data else data
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(header_removed))
        else:
            return None
            
        logger.info(f"SUCCESS: Saved as {filename}")
        return save_path
    except Exception as e:
        logger.error(f"FAILURE: Save failed. {str(e)}")
        return None

def generate_image(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    try:
        logger.info(f"REQUEST: {prompt}")
        
        response = client.chat.completions.create(
            model="black-forest-labs/flux.2-klein-4b",
            messages=[{"role": "user", "content": prompt}],
            # CRITICAL 2026 FLAGS:
            extra_body={"modalities": ["image"]}, 
            extra_headers={"X-Title": "Cybersecurity Image Lab"}
        )

        # Deep Search for the Image URL/Data
        msg_dict = response.choices[0].message.to_dict()
        image_source = None

        # Logic to navigate the 2026 nested dictionary
        if 'images' in msg_dict and msg_dict['images']:
            first_img = msg_dict['images'][0]
            # Path A: Directly in 'url'
            if isinstance(first_img, dict):
                image_source = first_img.get('url') or \
                               first_img.get('image_url', {}).get('url') or \
                               first_img.get('data') # Base64 fallback
        
        # Path B: Fallback to Regex on content if metadata is missing
        if not image_source and msg_dict.get('content'):
            urls = re.findall(r'(https?://[^\s]+)', msg_dict['content'])
            if urls: image_source = urls[0].strip('()[]')

        if image_source:
            local_path = save_image_data(image_source, filename)
            return {'success': True, 'local_path': local_path}
            
        logger.warning(f"FAILURE: No image data. Finish Reason: {response.choices[0].finish_reason}")
        return {'success': False, 'error': 'No image data found'}
            
    except Exception as e:
        logger.error(f"EXCEPTION: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    logger.info("--- Starting Demo Run ---")
    result = generate_image("A futuristic digital rose, cinematic lighting")
    if result.get('success'):
        logger.info(f"DONE: {os.path.basename(result['local_path'])}")

if __name__ == "__main__":
    main()
