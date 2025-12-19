import os
import requests
import json
import toml

def list_models_with_stored_key():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} not found.")
        return

    try:
        with open(secrets_path, "r") as f:
            secrets = toml.load(f)
            api_key = secrets.get("GEMINI_API_KEY")
    except Exception as e:
        print(f"Error reading secrets.toml: {e}")
        return

    if not api_key:
        print("Error: GEMINI_API_KEY not found in secrets.toml.")
        return

    # Try listing models via v1beta and v1
    for version in ["v1", "v1beta"]:
        url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
        print(f"\n--- Testing Version: {version} ---")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"Successfully retrieved {len(models)} models.")
                for m in models:
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        # Filter to interesting ones
                        if "flash" in m.get("name").lower() or "pro" in m.get("name").lower():
                            print(f"- {m.get('name')} ({m.get('displayName')})")
            else:
                print(f"Failed ({version}). Status Code: {response.status_code}")
                # print(f"Response: {response.text}") # Be careful with output
        except Exception as e:
            print(f"Error calling API ({version}): {e}")

if __name__ == "__main__":
    list_models_with_stored_key()
