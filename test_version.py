import json
import os
import time
import requests
import sys

# Test version without OpenAI dependency
def generate_test_reply(indu_message):
    """Generate a test reply without using OpenAI API"""
    test_replies = [
        f"Hello! I received your message: '{indu_message}'. This is a test reply from Yaswanth.",
        f"Thanks for saying '{indu_message}'. I'm responding as Yaswanth in test mode.",
        f"Your message '{indu_message}' was heard. Yaswanth here, replying in test mode!",
    ]
    # Simple hash-based selection for consistent responses
    import hashlib
    hash_val = int(hashlib.md5(indu_message.encode()).hexdigest(), 16)
    return test_replies[hash_val % len(test_replies)]

def test_flask_communication():
    """Test the Flask app communication without OpenAI"""
    print("🧪 Testing Flask Communication (No OpenAI Required)")
    print("=" * 50)
    
    while True:
        indu_input = input("💬 Indu says: ")
        if indu_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
            
        # Generate test reply
        reply = generate_test_reply(indu_input)
        print(f"🤖 Generated reply: {reply}")

        # Send to review UI
        url_generate = "http://127.0.0.1:5000/generate"
        payload = {
            "indu_message": indu_input,
            "yaswanth_reply": reply
        }

        try:
            print("📨 Sending to review UI...")
            response = requests.post(url_generate, json=payload)
            print(f"🔍 Response status: {response.status_code}")
            print(f"🔍 Response text: {response.text}")
            
            if response.status_code == 200:
                print("✅ Successfully sent to review UI!")
                print("⏳ Waiting for approval on UI...")
                print("🌐 Open http://127.0.0.1:5000 in your browser to approve the message")

                url_status = "http://127.0.0.1:5000/status"
                while True:
                    status_resp = requests.get(url_status)
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        if status_data.get("approved", False):
                            final_reply = status_data.get("yaswanth_reply", "")
                            print(f"\n✅ Approved Final Reply:\n{final_reply}\n")
                            print("=" * 50)
                            break
                    else:
                        print(f"⚠️ Status check failed: {status_resp.status_code}")
                    time.sleep(2)
            else:
                print(f"❌ Review UI error: {response.status_code}")
                print(f"❌ Response body: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure Flask app is running on http://127.0.0.1:5000")
            print("   Run: python app.py")
        except Exception as e:
            print(f"❌ Error during review UI flow: {e}")

if __name__ == "__main__":
    test_flask_communication()