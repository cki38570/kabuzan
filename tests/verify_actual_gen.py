import os
import requests
import re
import json

def verify_generation():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    api_key = None
    try:
        with open(secrets_path, "r") as f:
            for line in f:
                match = re.search(r'GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    api_key = match.group(1)
                    break
    except Exception as e:
        print(f"Error reading secrets.toml: {e}")
        return

    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        return

    # Use v1beta (common for Flash) and gemini-flash-latest confirmed in list
    model = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello, please reply with 'SUCCESS' if you can read this."
            }]
        }]
    }
    
    print(f"Testing generation with {model} via v1beta...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            print(f"Response: {text.strip()}")
            if "SUCCESS" in text.upper():
                print("\n✅ GENERATION TEST PASSED!")
            else:
                print("\n⚠️ Unexpected response content.")
        else:
            print(f"Failed. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_generation()
