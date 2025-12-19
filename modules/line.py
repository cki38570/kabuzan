import requests
import streamlit as st

def send_line_notification(message, token):
    """
    Send a message via LINE Notify.
    """
    if not token:
        return False, "LINE Notify Token is missing."
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            return True, "Notification sent successfully."
        else:
            return False, f"Failed to send: {response.status_code} {response.text}"
    except Exception as e:
        return False, f"Error sending LINE notification: {e}"
