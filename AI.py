import streamlit as st
from datetime import datetime
import requests
import json
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
from io import BytesIO



OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "google/gemma-3-27b-it:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"  # chat completions endpoint [web:209][web:211]


st.set_page_config(
    page_title="Advanced AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)



advanced_css = """
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    body, .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
    }

    .main { background-attachment: fixed; }

    .stChatMessage {
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .stChatMessage.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-left: 4px solid #00d9ff;
    }

    .stChatMessage.assistant {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-left: 4px solid #f5576c;
    }

    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }

    .header-title {
        font-size: 3em;
        font-weight: 900;
        background: linear-gradient(135deg, #00d9ff, #ff0064);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0,217,255,0.5);
        margin: 0;
    }

    .header-subtitle {
        font-size: 1.2em;
        color: #ff0064;
        margin-top: 10px;
        letter-spacing: 2px;
    }
</style>
"""
st.markdown(advanced_css, unsafe_allow_html=True)

# ============== SESSION STATE ==============

if "bot_name" not in st.session_state:
    st.session_state.bot_name = "JARVIS"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = ""

# ============== SIMPLE LANGUAGE DETECTOR ==============

def detect_language_simple(text: str) -> str:
    if not text:
        return "English"
    devanagari_count = sum('\u0900' <= ch <= '\u097F' for ch in text)
    ratio = devanagari_count / max(len(text), 1)
    return "Hindi" if ratio > 0.2 else "English"


def text_to_speech(text: str, language: str = "en"):
    """
    Generate speech audio with gTTS and show a player in Streamlit.
    language: 'en' or 'hi'.
    """
    try:
        if not text:
            st.warning("No text to speak.")
            return

        # 1) gTTS -> MP3 in memory [web:193]
        tts = gTTS(text=text, lang=language)
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)

        # 2) Streamlit audio player [web:196]
        audio_bytes = audio_io.read()
        st.audio(audio_bytes, format="audio/mpeg")
    except Exception as e:
        st.error(f"TTS error: {e}")

# ============== LLM CALL (OPENROUTER) ==============

def get_ai_response(user_message: str, context: str = "") -> dict:
    system_prompt = f"""
You are an advanced AI Assistant named {st.session_state.get('bot_name', 'JARVIS')}.
You are intelligent, helpful, and solve user problems completely.

User can speak:
- Pure Hindi.
- Pure English.
- Mixed Hinglish.

Requirements:
1. Detect the user's language from the latest message.
2. Answer in the SAME language/mix as the user (for display).
3. ALSO respond with:
   - A pure English version of the answer (simple, for TTS).
   - A pure Hindi version of the answer (simple, for TTS).

Respond in strict JSON with keys:
- "show_text": string
- "tts_text_en": string
- "tts_text_hi": string
Do not add any extra keys or text.
"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
        }

        resp = requests.post(OPENROUTER_URL, json=data, headers=headers, timeout=60)
        resp.raise_for_status()
        j = resp.json()

        raw = j["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(raw[start:end+1])
            else:
                parsed = {
                    "show_text": raw,
                    "tts_text_en": raw,
                    "tts_text_hi": raw
                }

        show_text = parsed.get("show_text") or raw
        tts_en = parsed.get("tts_text_en") or show_text
        tts_hi = parsed.get("tts_text_hi") or show_text

        return {
            "show_text": show_text,
            "tts_text_en": tts_en,
            "tts_text_hi": tts_hi
        }
    except Exception as e:
        txt = f"Error contacting AI service: {e}"
        return {
            "show_text": txt,
            "tts_text_en": txt,
            "tts_text_hi": txt
        }

# ============== HEADER ==============

st.markdown(f"""
<div class='header-container'>
    <h1 class='header-title'>⚡ {st.session_state.bot_name}</h1>
    <p class='header-subtitle'>Hindi + English Voice Assistant (OpenRouter)</p>
</div>
""", unsafe_allow_html=True)

# ============== SIDEBAR ==============

with st.sidebar:
    st.title("⚙️ Settings")

    new_name = st.text_input("Assistant Name:", value=st.session_state.bot_name)
    if new_name != st.session_state.bot_name:
        st.session_state.bot_name = new_name
        st.success(f"Assistant renamed to {new_name}")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_context = ""
        st.success("Chat cleared!")

    st.divider()
    st.markdown("### 📚 About")
    st.info(
        f"""**{st.session_state.bot_name}** - Hindi/English voice assistant using OpenRouter + gTTS.

Features:
✅ Voice Input (mic button)
✅ Auto language detection (Hindi / English / Hinglish)
✅ Each answer gets a ready audio player
✅ Context Awareness
"""
    )

# ============== CHAT DISPLAY ==============

st.markdown("### 🗣️ Conversation")
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

st.divider()

# ============== INPUT SECTION ==============

st.markdown("### 🔍 Ask Me Anything (Hindi / English / Hinglish)")

input_col, voice_col = st.columns([3, 1.5])

with input_col:
    typed_text = st.chat_input("💬 Type your question...")  # chat input widget [web:250]

with voice_col:
    st.write("🎙️ Voice Question")
    voice_text = speech_to_text(
        language='en',
        start_prompt="🎤 Speak",   # click once to start [web:203]
        stop_prompt="⏹ Stop",     # click again to stop [web:203][web:204]
        just_once=True,
        use_container_width=True,
        key="voice_input"
    )
    if voice_text:
        st.success(f"✅ You said: {voice_text}")

# prefer typed, else voice
user_input = typed_text if typed_text else (voice_text if voice_text else None)

# ============== PROCESS USER INPUT ==============

if user_input:
    user_lang = detect_language_simple(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("🤖 Thinking..."):
        ctx = st.session_state.conversation_context
        out = get_ai_response(user_input, ctx)

    show_text = out["show_text"]
    tts_en = out["tts_text_en"]
    tts_hi = out["tts_text_hi"]

    st.session_state.messages.append({"role": "assistant", "content": show_text})

    # compact context (last 10 messages)
    ctx_lines = []
    for msg in st.session_state.messages[-10:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        ctx_lines.append(f"{role}: {msg['content']}")
    st.session_state.conversation_context = "\n".join(ctx_lines)

    # choose TTS language based on user message
    if user_lang == "Hindi":
        speak_text = tts_hi
        speak_lang = "hi"
    else:
        speak_text = tts_en
        speak_lang = "en"

    # 🔊 generate audio player for the answer
    text_to_speech(speak_text, language=speak_lang)

    st.rerun()

# ============== FOOTER ==============

st.markdown(f"""
<div style='text-align:center; margin-top:40px; padding:20px; background:rgba(255,255,255,0.05); border-radius:10px;'>
    <p style='font-size:14px; color:#00d9ff;'>⚡ <b>{st.session_state.bot_name}</b> - Hindi & English Voice Assistant ⚡</p>
    <p style='font-size:12px; color:#ff0064;'>Powered by OpenRouter | gTTS + Streamlit</p>
    <p style='font-size:10px; color:#888;'>Speak or type in Hindi, English, or Hinglish. Each answer comes with an audio player ready to play.</p>
</div>
""", unsafe_allow_html=True)
