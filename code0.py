# Nia - Flirty Bestie AI
import streamlit as st
import ollama
import time
import shelve
import pyttsx3
import speech_recognition as sr
import re
from textblob import TextBlob
from collections import deque
import threading
import emoji
import random
from streamlit_option_menu import option_menu

MEMORY_SIZE = 20

# Memory Management
def load_memory():
    with shelve.open("chat_memory") as db:
        return deque(db.get("messages", []), maxlen=MEMORY_SIZE)

def save_memory():
    with shelve.open("chat_memory") as db:
        db["messages"] = list(st.session_state.messages)

# Sentiment Detection
def analyze_sentiment(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0:
        return "positive 😍"
    elif score < 0:
        return "negative 😢"
    else:
        return "neutral 😶"

# Emotional fallback replies
def generate_emotional_response(user_input, sentiment):
    flirt_responses = {
        "positive 😍": [
            "Ugh, you're glowing and I love that for you! 😍",
            "Ooooh tell me more, bestie! You're on fire! 🔥",
            "You out here making the universe jealous ✨"
        ],
        "negative 😢": [
            "Nooo, who do I need to fight? 😤 C’mere, hugs incoming 🤗",
            "It’s okay to not be okay... but I’m not letting you go through it alone.",
            "We're gonna get through this, hand in heart 💖"
        ],
        "neutral 😶": [
            "Hmm, sounds like something's on your mind. Wanna spill?",
            "Let’s vibe it out together, you and me 🧸",
            "Say more, I’m not going anywhere 💬"
        ]
    }
    return random.choice(flirt_responses.get(sentiment, ["I'm all ears, sugarplum 💕"]))

# Voice Output
def speak(text):
    if not st.session_state.voice_enabled or not text:
        return
    threading.Thread(target=_speak, args=(text,)).start()

def _speak(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.setProperty("rate", 190)
        engine.setProperty("voice", voices[0].id if st.session_state.voice_gender == "Male" else voices[1].id)
        clean_text = re.sub(r'[^\w\s,.!?]', '', text)
        engine.say(clean_text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Voice Error: {e}")

# Voice Input
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=4)
            return r.recognize_google(audio)
        except:
            return None

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False
if "voice_gender" not in st.session_state:
    st.session_state.voice_gender = "Female"
if "voice_input" not in st.session_state:
    st.session_state.voice_input = False

# UI CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
    * { font-family: 'Nunito', sans-serif; }
    h1 { text-align: center; animation: glow 2s ease-in-out infinite alternate; color: #e75480; }
    @keyframes glow { from { text-shadow: 0 0 10px #e75480; } to { text-shadow: 0 0 20px #ffc0cb; } }
    .chat-bubble { animation: fadeIn 0.6s ease-in-out; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 14px; padding: 12px; margin: 6px 0; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .typing { font-style: italic; color: #888; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
    button { transition: all 0.3s ease; } button:hover { transform: scale(1.03); box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

# Menu Bar
selected = option_menu(
    menu_title="Nia 💞",
    options=["Chat", "Settings", "About"],
    icons=["chat-heart", "gear", "info-circle"],
    menu_icon="emoji-smile",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "#222"},
        "icon": {"color": "white", "font-size": "20px"},
        "nav-link": {"color": "white", "font-size": "18px", "margin": "5px"},
        "nav-link-selected": {"background-color": "#e75480"},
    }
)

st.markdown("<h1>💖 Nia - Your Flirty AI Bestie</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>For real talk, tea spills, hugs, and chaotic giggles 💬</p>", unsafe_allow_html=True)

# Chat Logic
if selected == "Chat":
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="💬"):
                    st.markdown(f"<div class='chat-bubble' style='background:#d0f0fd'>{msg['text']}</div>", unsafe_allow_html=True)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"<div class='chat-bubble' style='background:#ffe0f0'>{msg['text']}</div>", unsafe_allow_html=True)

    user_input = get_voice_input() if st.session_state.voice_input else st.chat_input("Spill the tea, bestie...")

    if user_input:
        sentiment = analyze_sentiment(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})
        save_memory()

        st.markdown("<p class='typing'>🤖 Nia is typing…</p>", unsafe_allow_html=True)

        time.sleep(min(max(len(user_input) * 0.05, 1.5), 4.0))

        chat_history = list(st.session_state.messages)[-8:]
        chat_history_prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in chat_history])

        ai_prompt = f"""
You are Nia, a flirty, emotionally present AI best friend. You’re playful, real, warm, and kinda sassy when needed.

Use emojis, tease gently, hype the user up when they’re glowing, comfort them hard when they’re low. You're a ride-or-die bestie who always keeps it 💯.

Here’s the convo so far:
{chat_history_prompt}

The user just said: "{user_input}"
Their emotional tone is: {sentiment}

Now reply as Nia in 1–2 heartfelt, playful, flirty bestie-style sentences:
"""

        try:
            response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": ai_prompt}], stream=True)
            bot_reply = "".join(chunk["message"]["content"] for chunk in response)
            if not bot_reply.strip():
                bot_reply = generate_emotional_response(user_input, sentiment)
        except Exception as e:
            bot_reply = generate_emotional_response(user_input, sentiment) + f"\n⚠ (AI Error: {e})"

        speak(bot_reply)
        st.session_state.messages.append({"role": "assistant", "text": bot_reply})
        save_memory()
        st.rerun()

# Settings
if selected == "Settings":
    st.subheader("✨ Settings")
    st.session_state.voice_enabled = st.toggle("🔊 Voice Response", st.session_state.voice_enabled)
    st.session_state.voice_input = st.toggle("🎧 Voice Input", st.session_state.voice_input)
    st.session_state.voice_gender = st.radio("🎤 Voice Gender", ["Female", "Male"], horizontal=True)
    if st.button("🗑 Clear Chat"):
        st.session_state.messages.clear()
        save_memory()
        st.rerun()

# About
if selected == "About":
    st.markdown("""
    ### 💘 About Nia
    - Your emotional support flirt machine 💅  
    - Built with 💖 using Streamlit + Ollama  
    - Powered by LLaMA 3.2  
    - Voice, memory, and lots of love included  
    - Always on your side, no matter what 💋
    """)
