import os
import httpx
import asyncio
from flask import current_app # For logging and accessing app config

async def generate_text(prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 256) -> str:
    """
    Asynchronously generates text using the DeepSeek API.
    """
    api_key = os.getenv('DEEPSEEK_API_KEY') # Fetches directly from env; could also use current_app.config
    
    if not api_key:
        # This check is somewhat redundant if check_deepseek_auth is used before calling this,
        # but good for direct calls or as a safeguard.
        if current_app:
            current_app.logger.error("DeepSeek API key not found in environment for generate_text call.")
        raise RuntimeError('DeepSeek API key not configured for integration utility.')

    # Use model from argument, or app config default, or hardcoded default
    if model is None:
        model = current_app.config.get('DEFAULT_DEEPSEEK_MODEL', 'deepseek-r1-distill-qwen-7b')

    # Consider making the base URL configurable if it might change or for testing
    base_url = "https://api.deepseek.ai/v1"
    request_url = f"{base_url}/chat/completions" # Corrected endpoint for chat models usually

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    # Payload for chat completion models typically requires a 'messages' array
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': temperature,
        'max_tokens': max_tokens
    }

    # Using a timeout for the HTTP request is good practice
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if current_app:
                 current_app.logger.info(f"Sending request to DeepSeek API: {request_url} with model {model}")
            resp = await client.post(request_url, json=payload, headers=headers)
            resp.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            
            response_data = resp.json()
            # Extract text from the typical chat completion response structure
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message_content = response_data["choices"][0].get("message", {}).get("content")
                if message_content:
                    return message_content
                else:
                    if current_app:
                        current_app.logger.error(f"DeepSeek API response missing message content: {response_data}")
                    raise ValueError("DeepSeek API response did not contain expected message content.")
            else:
                if current_app:
                    current_app.logger.error(f"DeepSeek API response missing choices: {response_data}")
                raise ValueError("DeepSeek API response did not contain expected choices array.")

        except httpx.HTTPStatusError as e:
            error_message = f"DeepSeek API request failed with status {e.response.status_code}: {e.response.text}"
            if current_app:
                current_app.logger.error(error_message)
            raise RuntimeError(error_message) # Re-raise as a generic runtime error for the route to handle
        except httpx.RequestError as e:
            error_message = f"DeepSeek API request failed due to a network or connection error: {e}"
            if current_app:
                current_app.logger.error(error_message)
            raise RuntimeError(error_message)
        except ValueError as e: # Catch specific ValueError from parsing response
             error_message = f"Error parsing DeepSeek API response: {e}"
             if current_app:
                current_app.logger.error(error_message)
             raise RuntimeError(error_message)
