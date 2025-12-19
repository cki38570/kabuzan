import os
import requests
import json

def list_models_via_api():
    # Try to get API KEY from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print(f"Calling: https://generativelanguage.googleapis.com/v1beta/models?key=***")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Successfully retrieved models list:")
            models = data.get("models", [])
            for m in models:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(f"- Name: {m.get('name')}, Version: {m.get('version')}, DisplayName: {m.get('displayName')}")
        else:
            print(f"Failed to retrieve models. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_models_via_api()
