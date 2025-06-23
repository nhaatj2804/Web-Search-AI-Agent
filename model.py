import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MODEL = os.getenv("MODEL", "llama3.2:3b")
PORT = os.getenv("PORT", 11434)
API_URL = f"http://14.9.0.125:{PORT}/api/generate"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def process(context, user_request):
    try:
        response = requests.post(
            API_URL,
            json={
                'model': MODEL,
                'prompt': (
                    f"Context:\n{context}\n\n"
                    "Using only the information from the above context, "
                    "answer the following request. Do not include any information "
                    "not present in the context, and keep your answer relevant:\n"
                    f"User's request:{user_request}"
                ),
                'stream': False
            }
        )
        
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()
    except Exception as e:
        print(f"Error in process: {e}")
        return ""

def process_deepseek(context, user_request):
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",  # Replace with your actual API key
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": (
                        f"Context:\n{context}\n\n"
                        "Using only the information from the above context, "
                        "answer the following request. Do not include any information "
                        "not present in the context, and keep your answer relevant, your answer should not mention the context:\n"
                        f"User's request: {user_request}"
                    )}
                ],
                "stream": False
            }
        )
        
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"Error in process_deepseek: {e}")
        return ""