import os
import requests
import re

def list_models_simple():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} not found.")
        return

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
        print("Error: GEMINI_API_KEY not found in secrets.toml.")
        return

    print("Gemini API Request Test (via requests)")
    for version in ["v1", "v1beta"]:
        url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
        print(f"\n--- Testing Version: {version} ---")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"Success! Found {len(models)} models.")
                for m in models:
                    name = m.get('name')
                    # Just print flash/pro to be concise
                    if "flash" in name.lower() or "pro" in name.lower():
                        print(f"- {name}")
            else:
                print(f"Failed ({version}). Status: {response.status_code}")
                # print(f"Body: {response.text}")
        except Exception as e:
            print(f"Exception ({version}): {e}")

if __name__ == "__main__":
    list_models_simple()
