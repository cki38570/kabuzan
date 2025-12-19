import requests
import json

def test_line_push_final():
    # Updated token from user
    access_token = "k7kwyyf2ur0mSiZvmNwXRsI0lSZn2G6JVx8EBZzafQ42rQSxhfKholoWSTeiaQ0b7h/QZ263vxVhK3uRiTbWvvptSLrgC8oL38UO7rL/m3gVDGb/zi58pNHcD6+DJ6FLCKj9t2w2l5+ZHs/ww0u//AdB04t89/1O/w1cDnyilFU="
    user_id = "U168f5e427cfcc14fbf9d69959d09daf7"
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": "✅ 株山AI: 最終接続テストに成功しました！Messaging API経由での通知が完全に機能しています。"
            }
        ]
    }

    print(f"Sending test push message to {user_id} with long-lived token...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ SUCCESS: Message sent successfully!")
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_line_push_final()
