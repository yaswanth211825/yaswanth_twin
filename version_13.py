import json
import os
import yaml
import sys
import time
import requests
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in environment variables.")
    print("Please create a .env file with your OpenAI API key.")
    sys.exit(1)
client = OpenAI(api_key=api_key)

# File paths
EMBEDDING_CACHE_PATH = "embeddings_cache.json"
CHAT_HISTORY_PATH = "yaswanth_finetune.jsonl"
YAML_PATH = "personality.yaml"
CHARACTER = "Yaswanth"

# Thread-safe cache
embedding_cache = {}
cache_lock = Lock()

# 📦 Load cache
def load_embedding_cache():
    if os.path.exists(EMBEDDING_CACHE_PATH):
        try:
            with open(EMBEDDING_CACHE_PATH, "r") as f:
                cache = json.load(f)
                print(f"📦 Loaded {len(cache)} cached embeddings.")
                return cache
        except json.JSONDecodeError:
            print("⚠️ Corrupted embeddings cache detected. Creating new.")
    return {}

# 💾 Save cache
def save_embedding_cache(cache):
    with open(EMBEDDING_CACHE_PATH, "w") as f:
        json.dump(cache, f)

# Initialize cache
embedding_cache = load_embedding_cache()

# 🔁 Get embedding with cache
def get_gpt_embedding(text, model="text-embedding-3-small"):
    key = f"{model}::{text}"
    with cache_lock:
        if key in embedding_cache:
            print(f"✅ Cache hit: {text[:30]}...")
            return embedding_cache[key]
    print(f"⏳ Cache miss: {text[:30]}...")
    try:
        response = client.embeddings.create(model=model, input=[text])
        embedding = response.data[0].embedding
        with cache_lock:
            embedding_cache[key] = embedding
        return embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        # Return a zero vector as fallback
        return [0.0] * 1536  # text-embedding-3-small dimension

# 🗂 Load chat history
def load_chat_history(file_path):
    conversations = []
    with open(file_path, "r") as f:
        for line in f:
            conversations.append(json.loads(line))
    print(f"🗂 Loaded {len(conversations)} conversations.")
    return conversations

# 😎 Load personality
def load_personality_summary(yaml_path, character="Yaswanth"):
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f).get(character, {})

# 🧠 Embed chat history
def embed_all_chat_history(history, use_threads=True):
    texts = [
        " ".join([m["content"] for m in convo["messages"]])
        for convo in history if any(m["content"].strip() for m in convo["messages"])
    ]

    def embed_and_cache(text):
        if len(text.strip()) < 5:
            print(f"⚠️ Skipping short text: {text[:10]}...")
            return
        key = f"text-embedding-3-small::{text}"
        with cache_lock:
            if key in embedding_cache:
                print(f"✅ Already cached: {text[:30]}...")
                return
        get_gpt_embedding(text)

    if use_threads:
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(embed_and_cache, texts))
    else:
        for text in texts:
            embed_and_cache(text)

    save_embedding_cache(embedding_cache)
    print("🧠 Embedding cache rebuilt.")

# 🔍 Find similar chats
def retrieve_similar_chats(history, new_message, top_k=5):
    new_emb = get_gpt_embedding(new_message)
    sims = []
    for convo in history:
        convo_text = " ".join([m["content"] for m in convo["messages"]])
        convo_emb = get_gpt_embedding(convo_text)
        score = cosine_similarity([new_emb], [convo_emb])[0][0]
        sims.append((score, convo))
    return [c[1] for c in sorted(sims, key=lambda x: x[0], reverse=True)[:top_k]]

# 🤖 Generate reply
def generate_reply(similar_convos, indu_message):
    with open(YAML_PATH, "r") as f:
        personality_yaml = f.read()

    messages = [{
        "role": "system",
        "content": f"Use this detailed personality config:\n\n{personality_yaml}"
    }]

    for convo in similar_convos:
        messages.extend(convo["messages"])

    messages.append({"role": "user", "content": indu_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generating reply: {e}")
        return "Sorry, I encountered an error while generating a response. Please try again."

# 💾 Save interaction
def save_interaction(file_path, indu_message, ai_reply):
    new_convo = {
        "messages": [
            {"role": "user", "content": indu_message},
            {"role": "assistant", "content": ai_reply}
        ]
    }
    with open(file_path, "a") as f:
        f.write(json.dumps(new_convo) + "\n")
    _ = get_gpt_embedding(" ".join([indu_message, ai_reply]))
    save_embedding_cache(embedding_cache)
    print("💾 Saved and embedded new convo.")

# 🎯 Main loop
if __name__ == "__main__":
    chat_history = load_chat_history(CHAT_HISTORY_PATH)
    personality = load_personality_summary(YAML_PATH, CHARACTER)

    if "--rebuild" in sys.argv:
        print("🔁 Rebuilding embeddings...")
        embed_all_chat_history(chat_history, use_threads=True)
        sys.exit()

    while True:
        indu_input = input("💬 Indu says: ")
        similar = retrieve_similar_chats(chat_history, indu_input)
        reply = generate_reply(similar, indu_input)

        # Send to review UI
        url_generate = "http://127.0.0.1:5000/generate"
        payload = {
            "indu_message": indu_input,
            "yaswanth_reply": reply
        }

        try:
            print("📨 Sending to review UI...")
            response = requests.post(url_generate, json=payload)
            if response.status_code == 200:
                print("⏳ Waiting for approval on UI...")

                url_status = "http://127.0.0.1:5000/status"
                while True:
                    status_resp = requests.get(url_status)
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        if status_data.get("approved", False):
                            final_reply = status_data.get("yaswanth_reply", "")
                            print(f"\n✅ Approved:\n{final_reply}\n")
                            save_interaction(CHAT_HISTORY_PATH, indu_input, final_reply)
                            break
                    else:
                        print(f"⚠️ Status check failed: {status_resp.status_code}")
                    time.sleep(2)
            else:
                print(f"❌ Review UI error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error during review UI flow: {e}")
