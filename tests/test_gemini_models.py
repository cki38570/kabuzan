import sys
import os
import streamlit as st

# Add current directory to path
sys.path.append(os.getcwd())

print("--- Gemini Connection & Model Discovery Test ---")

try:
    from modules.llm import get_gemini_client, API_KEY, GENAI_V1_AVAILABLE, GENAI_LEGACY_AVAILABLE
    import google.generativeai as old_genai

    # 1. New SDK Discovery
    print(f"\n[V1 SDK Test]")
    client = get_gemini_client()
    if client:
        print("V1 Client initialized. Trying to list models (if possible via SDK)...")
        # Direct generation test instead of listing for simplicity
        test_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-2.0-flash-exp']
        for m in test_models:
            try:
                print(f"Testing {m}...", end=" ")
                resp = client.models.generate_content(model=m, contents="Hi")
                print("SUCCESS!")
            except Exception as e:
                print(f"FAILED: {e}")
    else:
        print("V1 Client NOT available.")

    # 2. Legacy SDK Discovery
    print(f"\n[Legacy SDK Test]")
    if GENAI_LEGACY_AVAILABLE and API_KEY:
        try:
            old_genai.configure(api_key=API_KEY)
            print("Listing models available in Legacy SDK...")
            # This is key to find the exact string it expects
            for m in old_genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"- {m.name}")
            
            # Test direct generation
            test_models = ['gemini-1.5-flash', 'gemini-1.5-flash-latest']
            for m in test_models:
                try:
                    print(f"Testing {m}...", end=" ")
                    model = old_genai.GenerativeModel(m)
                    resp = model.generate_content("Hi")
                    print("SUCCESS!")
                except Exception as e:
                    print(f"FAILED: {e}")
        except Exception as e:
            print(f"Legacy SDK check failed: {e}")
    else:
        print("Legacy SDK NOT available.")

except ImportError as e:
    print(f"Import Error: {e}")

print("\nDiscovery Complete.")
