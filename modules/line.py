import requests
import streamlit as st
import os

def get_secret(key, default=""):
    """Get secret from streamlit secrets or environment variable."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.environ.get(key, default)

def send_line_message(text, user_id=None, use_broadcast=False):
    """
    Send a message via LINE Messaging API.
    """
    channel_access_token = get_secret("LINE_CHANNEL_ACCESS_TOKEN")
    
    if not channel_access_token:
        return False, "LINE_CHANNEL_ACCESS_TOKEN is missing."
    
    # Determine endpoint and payload
    if use_broadcast:
        url = "https://api.line.me/v2/bot/message/broadcast"
        payload = {
            "messages": [
                {"type": "text", "text": text}
            ]
        }
    else:
        # Push message to specific user
        target_user_id = user_id or get_secret("LINE_USER_ID")
        if not target_user_id:
            return False, "LINE_USER_ID is missing."
        
        url = "https://api.line.me/v2/bot/message/push"
        payload = {
            "to": target_user_id,
            "messages": [
                {"type": "text", "text": text}
            ]
        }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Message sent successfully."
        else:
            return False, f"Failed to send: {response.status_code} {response.text}"
    except Exception as e:
        return False, f"Error sending LINE message: {e}"
