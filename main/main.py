# ============================================================
# PERSONAL SIRI
# Modern AI Voice + Chat Web Application
# Streamlit Cloud Ready
# ============================================================

import os
import io
import json
import hashlib
from datetime import datetime

import streamlit as st
import speech_recognition as sr
from groq import Groq


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Personal SIRI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

SESSION_DEFAULTS = {
    "messages": [],
    "chat_history": [],
    "current_chat": "New Chat",
    "listening": False,
    "audio_hash": "",
    "speaking": False,
    "last_response": "",
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL
========================================================= */

:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #8b5cf6;
    --cyan: #06b6d4;
    --green: #10b981;
    --red: #ef4444;

    --text: #172033;
    --muted: #64748b;
    --border: #e5e7eb;

    --card: rgba(255,255,255,0.88);
    --background: #f5f7fb;
}

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0 !important;
    padding: 0 !important;
}

body {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}

/* Do NOT hide Streamlit header */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 15% 5%,
            rgba(99,102,241,0.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(139,92,246,0.10),
            transparent 25%
        ),
        #f7f8fc;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1500px !important;
    padding-top: 22px !important;
    padding-left: 26px !important;
    padding-right: 26px !important;
    padding-bottom: 30px !important;
}


/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f8f9ff 100%
        ) !important;

    border-right: 1px solid #e7e9f2;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 18px 14px 20px 14px;
}


/* BRAND */

.sidebar-brand {
    position: relative;

    padding: 18px 12px 20px 12px;
    margin-bottom: 8px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.10),
            rgba(139,92,246,0.07)
        );

    border: 1px solid rgba(99,102,241,0.12);

    text-align: center;
}

.sidebar-logo {
    width: 58px;
    height: 58px;

    margin: 0 auto 10px auto;

    border-radius: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 29px;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );

    box-shadow:
        0 10px 25px rgba(99,102,241,0.28);
}

.sidebar-title {
    font-size: 21px;
    font-weight: 800;
    color: #1e1b4b;
    letter-spacing: -0.4px;
}

.sidebar-description {
    margin-top: 4px;

    font-size: 11px;
    color: #64748b;
}

.sidebar-cloud {
    display: inline-flex;

    margin-top: 11px;

    padding: 5px 10px;

    border-radius: 999px;

    background: #ecfdf5;
    border: 1px solid #bbf7d0;

    color: #047857;

    font-size: 10px;
    font-weight: 700;
}


/* SIDEBAR SECTION */

.sidebar-section-title {
    margin:
        20px
        4px
        8px
        4px;

    font-size: 10px;
    font-weight: 800;

    letter-spacing: 1.4px;

    color: #94a3b8;
}


/* NEW CHAT BUTTON */

div[data-testid="stSidebar"] div.stButton > button {
    border-radius: 12px !important;

    min-height: 43px !important;

    border: 1px solid #e0e7ff !important;

    background:
        linear-gradient(
            135deg,
            #eef2ff,
            #f5f3ff
        ) !important;

    color: #4338ca !important;

    font-weight: 700 !important;
}


/* SIDEBAR HISTORY */

div[data-testid="stSidebar"] div.stButton > button:hover {
    border-color: #a5b4fc !important;

    background:
        linear-gradient(
            135deg,
            #e0e7ff,
            #ede9fe
        ) !important;
}


/* =========================================================
   MAIN HEADER
========================================================= */

.siri-header {
    position: relative;

    width: 100%;

    min-height: 145px;

    padding: 22px;

    border-radius: 26px;

    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #4f46e5 0%,
            #6366f1 42%,
            #8b5cf6 75%,
            #7c3aed 100%
        );

    box-shadow:
        0 18px 45px rgba(79,70,229,0.20);

    color: white;

    text-align: center;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    margin-bottom: 14px;
}


/* Decorative circles */

.siri-header::before {
    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    border-radius: 50%;

    background: rgba(255,255,255,0.08);

    top: -90px;
    left: -50px;
}

.siri-header::after {
    content: "";

    position: absolute;

    width: 230px;
    height: 230px;

    border-radius: 50%;

    background: rgba(255,255,255,0.06);

    right: -70px;
    bottom: -130px;
}


.siri-mic {
    position: relative;
    z-index: 2;

    width: 48px;
    height: 48px;

    border-radius: 16px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 25px;

    background: rgba(255,255,255,0.18);

    border: 1px solid rgba(255,255,255,0.25);

    box-shadow:
        0 8px 20px rgba(0,0,0,0.10);

    margin-bottom: 8px;
}

.siri-main-title {
    position: relative;
    z-index: 2;

    font-size: 31px;

    font-weight: 850;

    letter-spacing: -0.8px;

    line-height: 1.1;
}

.siri-main-subtitle {
    position: relative;
    z-index: 2;

    margin-top: 7px;

    color: rgba(255,255,255,0.82);

    font-size: 13px;

    letter-spacing: 0.2px;
}


/* =========================================================
   STATUS BAR
========================================================= */

.status-grid {
    width: 100%;

    display: grid;

    grid-template-columns:
        1fr
        1fr
        1fr;

    gap: 12px;

    margin-bottom: 13px;
}

.status-card {
    min-height: 55px;

    padding: 10px 16px;

    border-radius: 15px;

    background: rgba(255,255,255,0.88);

    border: 1px solid #e4e7ef;

    box-shadow:
        0 5px 18px rgba(15,23,42,0.04);

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 9px;

    color: #334155;

    font-size: 13px;

    font-weight: 600;
}

.status-symbol {
    font-size: 17px;
}

.ready-card {
    color: #047857;

    background:
        linear-gradient(
            135deg,
            #ecfdf5,
            #f0fdf4
        );

    border-color: #bbf7d0;
}

.ready-dot {
    width: 9px;
    height: 9px;

    border-radius: 50%;

    background: #10b981;

    box-shadow:
        0 0 0 4px rgba(16,185,129,0.13);

    animation: pulseReady 2s infinite;
}

@keyframes pulseReady {

    0%, 100% {
        box-shadow:
            0 0 0 4px rgba(16,185,129,0.12);
    }

    50% {
        box-shadow:
            0 0 0 7px rgba(16,185,129,0.03);
    }

}


/* =========================================================
   CHAT HEADER
========================================================= */

.chat-top {
    display: flex;

    align-items: center;

    justify-content: space-between;

    margin:
        5px
        3px
        8px
        3px;
}

.chat-heading {
    display: flex;

    align-items: center;

    gap: 8px;

    font-size: 14px;

    font-weight: 800;

    color: #334155;
}

.chat-heading-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #6366f1;

    box-shadow:
        0 0 0 4px rgba(99,102,241,0.10);
}

.chat-count {
    color: #94a3b8;

    font-size: 11px;
}


/* =========================================================
   CHAT WINDOW
========================================================= */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px !important;

    border: 1px solid #e1e5ee !important;

    background:
        rgba(255,255,255,0.72) !important;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.8),
        0 10px 30px rgba(15,23,42,0.04) !important;
}


/* =========================================================
   EMPTY CHAT
========================================================= */

.empty-state {
    min-height: 330px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;
}

.empty-orb {
    width: 80px;
    height: 80px;

    border-radius: 25px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 37px;

    background:
        linear-gradient(
            135deg,
            #eef2ff,
            #f5f3ff
        );

    border: 1px solid #ddd6fe;

    box-shadow:
        0 15px 35px rgba(99,102,241,0.14);

    margin-bottom: 18px;
}

.empty-title {
    color: #1e293b;

    font-size: 22px;

    font-weight: 800;
}

.empty-description {
    max-width: 470px;

    margin-top: 7px;

    color: #64748b;

    font-size: 13px;

    line-height: 1.65;
}


/* =========================================================
   CHAT BUBBLES
========================================================= */

.user-message {
    display: flex;

    justify-content: flex-end;

    margin:
        8px
        6px
        8px
        20px;
}

.user-bubble {
    max-width: 78%;

    padding:
        12px
        16px;

    border-radius:
        18px
        18px
        5px
        18px;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #7c3aed
        );

    color: white;

    font-size: 14px;

    line-height: 1.55;

    box-shadow:
        0 8px 20px rgba(99,102,241,0.16);

    word-wrap: break-word;
}


.ai-message {
    display: flex;

    justify-content: flex-start;

    margin:
        8px
        20px
        8px
        6px;
}

.ai-avatar {
    flex-shrink: 0;

    width: 35px;
    height: 35px;

    margin-right: 9px;

    border-radius: 12px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );

    color: white;

    font-size: 17px;

    box-shadow:
        0 6px 15px rgba(99,102,241,0.18);
}

.ai-bubble {
    max-width: 78%;

    padding:
        12px
        16px;

    border-radius:
        5px
        18px
        18px
        18px;

    background: #ffffff;

    border: 1px solid #e5e7eb;

    color: #334155;

    font-size: 14px;

    line-height: 1.6;

    box-shadow:
        0 5px 18px rgba(15,23,42,0.04);
}


/* =========================================================
   INPUT AREA
========================================================= */

.input-wrapper {
    margin-top: 12px;

    padding: 6px;

    border-radius: 17px;

    background: white;

    border: 1px solid #e0e5ee;

    box-shadow:
        0 8px 25px rgba(15,23,42,0.05);
}


/* Streamlit input */

div[data-testid="stTextInput"] input {
    border: none !important;

    background: transparent !important;

    box-shadow: none !important;

    font-size: 14px !important;

    color: #1e293b !important;

    padding-left: 12px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: none !important;

    box-shadow: none !important;
}


/* Send */

.send-button div.stButton > button,
div.stButton > button.send-button {
    background:
        linear-gradient(
            135deg,
            #6366f1,
            #7c3aed
        ) !important;

    color: white !important;

    border: none !important;

    box-shadow:
        0 8px 18px rgba(99,102,241,0.20);
}


/* =========================================================
   VOICE CONTROL
========================================================= */

.voice-controls {
    display: flex;

    justify-content: center;

    margin-top: 10px;

    margin-bottom: 3px;
}

.voice-status {
    margin-top: 9px;

    padding: 12px 15px;

    border-radius: 14px;

    background:
        linear-gradient(
            135deg,
            #fff7ed,
            #fef3c7
        );

    border: 1px solid #fed7aa;

    color: #9a3412;

    font-size: 13px;

    text-align: center;

    font-weight: 600;
}


/* =========================================================
   STREAMLIT BUTTONS
========================================================= */

div.stButton > button {
    border-radius: 11px !important;

    min-height: 42px !important;

    font-weight: 650 !important;

    border: 1px solid #e1e5ee !important;

    background: white !important;

    color: #334155 !important;

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        border-color 0.15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);

    border-color: #a5b4fc !important;

    box-shadow:
        0 7px 18px rgba(99,102,241,0.10);
}


/* =========================================================
   AUDIO INPUT
========================================================= */

[data-testid="stAudioInput"] {
    margin-top: 8px;
}


/* =========================================================
   AI SPEAKING
========================================================= */

.speaking-card {
    display: flex;

    align-items: center;

    justify-content: center;

    gap: 9px;

    padding: 10px;

    margin-top: 8px;

    border-radius: 12px;

    background: #eef2ff;

    border: 1px solid #c7d2fe;

    color: #4338ca;

    font-size: 12px;

    font-weight: 700;
}

.sound-bars {
    display: flex;

    align-items: center;

    gap: 3px;

    height: 17px;
}

.sound-bars span {
    width: 3px;

    border-radius: 4px;

    background: #6366f1;

    animation: soundWave 0.9s infinite ease-in-out;
}

.sound-bars span:nth-child(1) {
    height: 7px;
    animation-delay: 0s;
}

.sound-bars span:nth-child(2) {
    height: 15px;
    animation-delay: .15s;
}

.sound-bars span:nth-child(3) {
    height: 10px;
    animation-delay: .3s;
}

.sound-bars span:nth-child(4) {
    height: 17px;
    animation-delay: .45s;
}

@keyframes soundWave {

    0%, 100% {
        transform: scaleY(.55);
    }

    50% {
        transform: scaleY(1);
    }
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 800px) {

    [data-testid="stMainBlockContainer"] {
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-top: 12px !important;
    }

    .siri-header {
        min-height: 125px;
        border-radius: 20px;
    }

    .siri-main-title {
        font-size: 25px;
    }

    .siri-main-subtitle {
        font-size: 11px;
    }

    .status-grid {
        grid-template-columns: 1fr;
        gap: 7px;
    }

    .status-card {
        min-height: 43px;
    }

    .user-bubble,
    .ai-bubble {
        max-width: 88%;
    }

    .empty-state {
        min-height: 280px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ API
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        GROQ_API_KEY = ""

client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception:
        client = None


MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Personal SIRI, a professional personal AI assistant.

You help the user with:
- Programming
- Computer science
- Projects
- Exams
- Aptitude
- Interviews
- Career preparation
- Resume preparation
- General questions
- Technical explanations

Rules:
1. Give accurate and useful answers.
2. Be friendly and professional.
3. Explain technical topics clearly.
4. Use headings and bullets when useful.
5. Do not unnecessarily repeat the question.
6. If code is requested, provide complete working code when practical.
7. Keep responses easy to read.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if not client:
        return (
            "⚠️ **Groq API key is not configured.**\n\n"
            "Please add `GROQ_API_KEY` to your Streamlit "
            "Cloud Secrets."
        )

    try:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        for msg in st.session_state.messages:

            conversation.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

        conversation.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=0.7,
            max_tokens=2048,
        )

        return response.choices[0].message.content

    except Exception as error:

        return f"""
⚠️ **Something went wrong**

`{str(error)}`
"""


# ============================================================
# CHAT MANAGEMENT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    title = st.session_state.current_chat

    if title == "New Chat":

        first_message = next(
            (
                x["content"]
                for x in st.session_state.messages
                if x["role"] == "user"
            ),
            "New Chat",
        )

        title = first_message[:28]

        if len(first_message) > 28:
            title += "..."

        st.session_state.current_chat = title

    existing = None

    for chat in st.session_state.chat_history:

        if chat["title"] == title:
            existing = chat
            break

    if existing:

        existing["messages"] = list(
            st.session_state.messages
        )

    else:

        st.session_state.chat_history.insert(
            0,
            {
                "title": title,
                "messages": list(
                    st.session_state.messages
                ),
            },
        )


def new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.current_chat = "New Chat"

    st.session_state.last_response = ""

    st.session_state.speaking = False

    st.session_state.listening = False


def load_chat(index):

    save_current_chat()

    selected = st.session_state.chat_history[index]

    st.session_state.current_chat = selected["title"]

    st.session_state.messages = list(
        selected["messages"]
    )

    st.session_state.last_response = ""

    st.session_state.speaking = False


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(text):

    text = text.strip()

    if not text:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": text,
        }
    )

    answer = get_ai_response(text)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.session_state.last_response = answer

    save_current_chat()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def recognize_audio(audio_bytes):

    recognizer = sr.Recognizer()

    try:

        audio_stream = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_stream) as source:

            audio_data = recognizer.record(source)

        result = recognizer.recognize_google(
            audio_data
        )

        return result

    except sr.UnknownValueError:

        return "I couldn't understand your voice."

    except sr.RequestError:

        return (
            "Speech recognition service is currently "
            "unavailable."
        )

    except Exception as error:

        return f"Speech recognition error: {error}"


# ============================================================
# BROWSER SPEECH
# ============================================================

def browser_speak(text):

    if not text:
        return

    safe_text = json.dumps(text)

    st.html(
        f"""
        <script>

        const siriText = {safe_text};

        if ("speechSynthesis" in window) {{

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(
                    siriText
                );

            speech.rate = 1.0;
            speech.pitch = 1.0;
            speech.volume = 1.0;

            window.speechSynthesis.speak(
                speech
            );
        }}

        </script>
        """
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                🎙️
            </div>

            <div class="sidebar-title">
                Personal SIRI
            </div>

            <div class="sidebar-description">
                Your intelligent AI voice assistant
            </div>

            <div class="sidebar-cloud">
                ● AI ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # NEW CHAT

    if st.button(
        "＋  New Conversation",
        use_container_width=True,
    ):

        new_chat()
        st.rerun()


    # HISTORY

    st.markdown(
        """
        <div class="sidebar-section-title">
            CONVERSATIONS
        </div>
        """,
        unsafe_allow_html=True,
    )


    if st.session_state.chat_history:

        for index, chat in enumerate(
            st.session_state.chat_history
        ):

            if st.button(
                f"💬  {chat['title']}",
                key=f"chat_history_{index}",
                use_container_width=True,
            ):

                load_chat(index)
                st.rerun()

    else:

        st.markdown(
            """
            <div style="
                padding:12px 5px;
                color:#94a3b8;
                font-size:12px;
                text-align:center;
            ">
                Your conversations<br>
                will appear here.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # SETTINGS

    st.markdown(
        """
        <div class="sidebar-section-title">
            ASSISTANT
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            padding:11px 12px;
            border:1px solid #e5e7eb;
            border-radius:12px;
            background:white;
            margin-bottom:7px;
            font-size:12px;
            color:#475569;
        ">
            🤖 &nbsp; Groq AI
        </div>

        <div style="
            padding:11px 12px;
            border:1px solid #e5e7eb;
            border-radius:12px;
            background:white;
            margin-bottom:7px;
            font-size:12px;
            color:#475569;
        ">
            🎙️ &nbsp; Voice Input
        </div>

        <div style="
            padding:11px 12px;
            border:1px solid #e5e7eb;
            border-radius:12px;
            background:white;
            font-size:12px;
            color:#475569;
        ">
            🔊 &nbsp; Voice Output
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.html(
    """
    <div class="siri-header">

        <div class="siri-mic">
            🎙️
        </div>

        <div class="siri-main-title">
            Personal SIRI
        </div>

        <div class="siri-main-subtitle">
            Your Personal AI Voice & Chat Assistant
        </div>

    </div>
    """
)


# ============================================================
# STATUS
# ============================================================

now = datetime.now()

date_text = now.strftime("%d %b %Y")
time_text = now.strftime("%I:%M %p")

message_count = len(st.session_state.messages)


st.html(
    f"""
    <div class="status-grid">

        <div class="status-card">
            <span class="status-symbol">📅</span>
            <span>{date_text}</span>
        </div>

        <div class="status-card">
            <span class="status-symbol">🕐</span>
            <span>{time_text}</span>
        </div>

        <div class="status-card ready-card">
            <span class="ready-dot"></span>
            <span>AI Ready</span>
        </div>

    </div>
    """
)


# ============================================================
# CHAT HEADER
# ============================================================

st.html(
    f"""
    <div class="chat-top">

        <div class="chat-heading">
            <span class="chat-heading-dot"></span>
            <span>{st.session_state.current_chat}</span>
        </div>

        <div class="chat-count">
            {message_count} messages
        </div>

    </div>
    """
)


# ============================================================
# CHAT WINDOW
# ONLY THIS SECTION SCROLLS
# ============================================================

with st.container(
    height=430,
    border=True,
):

    if not st.session_state.messages:

        st.html(
            """
            <div class="empty-state">

                <div class="empty-orb">
                    🎙️
                </div>

                <div class="empty-title">
                    How can I help you?
                </div>

                <div class="empty-description">
                    Welcome to Personal SIRI.
                    Ask a question, work on your project,
                    prepare for an interview, or simply
                    talk to your AI assistant.
                </div>

            </div>
            """
        )

    else:

        for message in st.session_state.messages:

            if message["role"] == "user":

                st.markdown(
                    f"""
                    <div class="user-message">

                        <div class="user-bubble">
                            {message["content"]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                # Markdown is converted to HTML by Streamlit
                # inside the AI bubble using a normal container.

                st.markdown(
                    f"""
                    <div class="ai-message">

                        <div class="ai-avatar">
                            🎙️
                        </div>

                        <div class="ai-bubble">
                            {message["content"]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# MESSAGE COMPOSER
# ============================================================

with st.form(
    "message_form",
    clear_on_submit=True,
):

    input_col, send_col = st.columns(
        [8.5, 1],
        gap="small",
    )

    with input_col:

        user_input = st.text_input(
            "Message",
            placeholder="Message Personal SIRI...",
            label_visibility="collapsed",
        )

    with send_col:

        send_clicked = st.form_submit_button(
            "➤",
            use_container_width=True,
        )


if send_clicked and user_input.strip():

    send_message(user_input)

    st.rerun()


# ============================================================
# VOICE CONTROLS
# ============================================================

voice_col, stop_col = st.columns(
    [1, 1],
    gap="small",
)


with voice_col:

    if st.button(
        "🎙️  Start Voice",
        use_container_width=True,
    ):

        st.session_state.listening = True
        st.rerun()


with stop_col:

    if st.session_state.listening:

        if st.button(
            "⏹️  Stop Listening",
            use_container_width=True,
        ):

            st.session_state.listening = False
            st.rerun()

    else:

        if st.session_state.last_response:

            if st.button(
                "🔊  Play AI Response",
                use_container_width=True,
            ):

                st.session_state.speaking = True
                st.rerun()


# ============================================================
# VOICE INPUT
# ============================================================

if st.session_state.listening:

    st.markdown(
        """
        <div class="voice-status">
            🎙️ &nbsp; Listening mode is active.
            Record your message below.
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio_value = st.audio_input(
        "Voice recording",
        label_visibility="visible",
    )

    if audio_value is not None:

        audio_bytes = audio_value.getvalue()

        current_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            current_hash
            != st.session_state.audio_hash
        ):

            st.session_state.audio_hash = current_hash

            recognized_text = recognize_audio(
                audio_bytes
            )

            st.session_state.listening = False

            if (
                recognized_text
                and not recognized_text.startswith(
                    (
                        "I couldn't",
                        "Speech recognition",
                    )
                )
            ):

                send_message(recognized_text)

            st.rerun()


# ============================================================
# AI SPEAKING
# ============================================================

if (
    st.session_state.speaking
    and st.session_state.last_response
):

    st.html(
        """
        <div class="speaking-card">

            <div class="sound-bars">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>

            🔊 Personal SIRI is speaking...

        </div>
        """
    )

    browser_speak(
        st.session_state.last_response
    )

    if st.button(
        "⏹️  Stop AI Speaking",
        use_container_width=True,
    ):

        st.session_state.speaking = False

        st.html(
            """
            <script>
                if ("speechSynthesis" in window) {
                    window.speechSynthesis.cancel();
                }
            </script>
            """
        )

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:13px;
        color:#94a3b8;
        font-size:10px;
        letter-spacing:.2px;
    ">
        Personal SIRI &nbsp;•&nbsp;
        AI Voice & Chat Assistant
    </div>
    """,
    unsafe_allow_html=True,
)
