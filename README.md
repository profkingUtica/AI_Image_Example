# AI_Image_Example

1. API Key Security:
   - Never hardcode API keys in source code
   - Use environment variables or secure vaults
   - Rotate keys regularly
   - Implement key management best practices

2. Error Handling:
   - Always wrap API calls in try-except blocks
   - Log errors appropriately
   - Don't expose sensitive error details to users

3. Rate Limiting:
   - OpenAI has rate limits per minute/day
   - Implement retry logic with exponential backoff
   - Monitor usage to avoid service disruption

4. Input Validation:
   - Sanitize prompts to prevent prompt injection
   - Validate size and quality parameters
   - Limit user input to prevent abuse

5. Data Privacy:
   - OpenAI's API terms regarding data usage
   - Consider what prompts might contain sensitive info
   - Understand data retention policies

6. Cost Management:
   - DALL-E 3: ~$0.04-$0.08 per image, depending on quality
   - Implement usage tracking and budgets
   - Consider caching strategies

UNDERSTANDING THE API RESPONSE:
The JSON response contains:
- 'created': Unix timestamp of when the image was generated
- 'data': Array of generated images
  - 'url': Temporary URL to download the image (expires after 1 hour)
  - 'revised_prompt': OpenAI may modify your prompt for safety/quality
    (shows what prompt was actually used to generate the image)

SETUP INSTRUCTIONS:
1. python3 -m venv venv
2. source venv/bin/activate
3. Install required packages:
   pip install openai requests

4. Set your API key as an environment variable (https://platform.openai.com/):
   export OPENAI_API_KEY='your-api-key-here'  # Linux/Mac
   set OPENAI_API_KEY=your-api-key-here        # Windows

5. Run the script:
   python openai_image_demo.py
