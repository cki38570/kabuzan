import os
import requests
import re

def list_models_to_file():
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

    with open("tests/model_results.txt", "w") as out:
        for version in ["v1", "v1beta"]:
            url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
            out.write(f"\n--- VERSION: {version} ---\n")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    for m in models:
                        out.write(f"{m.get('name')}\n")
                else:
                    out.write(f"FAILED: {response.status_code}\n")
            except Exception as e:
                out.write(f"EXCEPTION: {e}\n")

if __name__ == "__main__":
    list_models_to_file()
