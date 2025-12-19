import requests
import json

def test_line_push():
    # Provided by user
    access_token = "9a1e75eed41d100627ba3db6ef42a911"
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
                "text": "🔔 株山AI: 自動検証システムからのテスト通知です。受信できていれば実装は正常です。"
            }
        ]
    }

    print(f"Sending test push message to {user_id}...")
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
    test_line_push()
