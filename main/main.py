# ============================================================
# PERSONAL SIRI - VOICE & CHAT ASSISTANT
# Streamlit Web Application
# ============================================================

import os
import io
import hashlib
from datetime import datetime

import streamlit as st
import speech_recognition as sr
from groq import Groq


# ============================================================
# PAGE CONFIGURATION
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

defaults = {
    "messages": [],
    "chat_history": [],
    "current_chat": "New Chat",
    "listening": False,
    "speak_text": "",
    "audio_processed": "",
    "dark_mode": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, Arial, sans-serif;
}

/* ----------------------------------------------------------
   MAIN STREAMLIT AREA
---------------------------------------------------------- */

[data-testid="stAppViewContainer"] {
    background: #f7f9fc;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1450px !important;
    padding-top: 20px !important;
    padding-bottom: 30px !important;
}

/* ----------------------------------------------------------
   SIDEBAR
---------------------------------------------------------- */

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 20px;
}

.sidebar-brand {
    text-align: center;
    padding: 8px 10px 20px 10px;
}

.sidebar-icon {
    font-size: 38px;
    margin-bottom: 4px;
}

.sidebar-title {
    font-size: 23px;
    font-weight: 700;
    color: #172554;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #64748b;
    margin-top: 4px;
}

.sidebar-section {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1px;
    margin: 24px 4px 10px 4px;
}

/* ----------------------------------------------------------
   PERSONAL SIRI HEADER
---------------------------------------------------------- */

.siri-header {
    width: 100%;
    min-height: 105px;
    padding: 20px 20px 18px 20px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #eef2ff 0%,
        #f5f3ff 50%,
        #eff6ff 100%
    );
    border: 1px solid #dbe4f0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-bottom: 12px;
}

.siri-icon {
    font-size: 30px;
    line-height: 1;
    margin-bottom: 5px;
}

.siri-title {
    font-size: 28px;
    line-height: 1.2;
    font-weight: 800;
    color: #172554;
}

.siri-subtitle {
    margin-top: 5px;
    font-size: 14px;
    color: #64748b;
}

/* ----------------------------------------------------------
   STATUS ROW
---------------------------------------------------------- */

.status-row {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
}

.status-card {
    height: 52px;
    border-radius: 12px;
    border: 1px solid #dbe4f0;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    color: #334155;
}

.status-ready {
    background: #ecfdf5;
    border-color: #bbf7d0;
    color: #047857;
    font-weight: 700;
}

.status-icon {
    font-size: 17px;
}

/* ----------------------------------------------------------
   CHAT AREA
---------------------------------------------------------- */

.chat-heading {
    font-size: 15px;
    font-weight: 700;
    color: #475569;
    margin: 4px 0 7px 3px;
}

.chat-empty {
    min-height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 35px 20px;
}

.empty-icon {
    font-size: 42px;
    margin-bottom: 10px;
}

.empty-title {
    font-size: 22px;
    font-weight: 700;
    color: #334155;
    margin-bottom: 8px;
}

.empty-text {
    font-size: 14px;
    line-height: 1.6;
    color: #64748b;
}

/* ----------------------------------------------------------
   INPUT AREA
---------------------------------------------------------- */

.input-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    margin: 12px 0 5px 3px;
}

/* ----------------------------------------------------------
   BUTTONS
---------------------------------------------------------- */

div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    border: 1px solid #dbe4f0;
    transition: 0.15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    border-color: #94a3b8;
}

/* ----------------------------------------------------------
   VOICE CONTROLS
---------------------------------------------------------- */

.voice-area {
    margin-top: 8px;
}

/* ----------------------------------------------------------
   DARK MODE
---------------------------------------------------------- */

.dark-mode {
    background: #111827;
}

/* ----------------------------------------------------------
   MOBILE
---------------------------------------------------------- */

@media (max-width: 800px) {

    [data-testid="stMainBlockContainer"] {
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    .siri-header {
        min-height: 95px;
        padding: 16px 10px;
    }

    .siri-title {
        font-size: 23px;
    }

    .siri-subtitle {
        font-size: 12px;
    }

    .status-row {
        grid-template-columns: 1fr;
        gap: 7px;
    }

    .status-card {
        height: 45px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ CONFIGURATION
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
You are Personal SIRI, a helpful personal AI voice and chat assistant.

Your responsibilities:
- Answer questions clearly and accurately.
- Help with programming and technical problems.
- Help with study and placement preparation.
- Explain difficult concepts simply.
- Help with projects, resumes and interviews.
- Be friendly and professional.
- Do not unnecessarily repeat information.
- Keep answers well structured.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if not client:
        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please add GROQ_API_KEY to your Streamlit Cloud Secrets."
        )

    try:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        for message in st.session_state.messages:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"⚠️ AI Error: {str(e)}"


# ============================================================
# SAVE CHAT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    existing = None

    for chat in st.session_state.chat_history:
        if chat["title"] == st.session_state.current_chat:
            existing = chat
            break

    if existing:
        existing["messages"] = list(st.session_state.messages)
    else:

        title = st.session_state.current_chat

        if title == "New Chat":

            first_user_message = next(
                (
                    m["content"]
                    for m in st.session_state.messages
                    if m["role"] == "user"
                ),
                "New Chat",
            )

            title = first_user_message[:30]

            if len(first_user_message) > 30:
                title += "..."

            st.session_state.current_chat = title

        st.session_state.chat_history.insert(
            0,
            {
                "title": st.session_state.current_chat,
                "messages": list(st.session_state.messages),
            },
        )


# ============================================================
# NEW CHAT
# ============================================================

def new_chat():

    save_current_chat()

    st.session_state.messages = []
    st.session_state.current_chat = "New Chat"
    st.session_state.speak_text = ""
    st.session_state.listening = False


# ============================================================
# LOAD CHAT
# ============================================================

def load_chat(index):

    save_current_chat()

    chat = st.session_state.chat_history[index]

    st.session_state.current_chat = chat["title"]
    st.session_state.messages = list(chat["messages"])
    st.session_state.speak_text = ""


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(message):

    message = message.strip()

    if not message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    answer = get_ai_response(message)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.session_state.speak_text = answer

    save_current_chat()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def recognize_audio(audio_bytes):

    recognizer = sr.Recognizer()

    try:

        audio_file = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        return text

    except sr.UnknownValueError:
        return "I couldn't understand the audio."

    except sr.RequestError:
        return "Speech recognition service is unavailable."

    except Exception as e:
        return f"Speech recognition error: {str(e)}"


# ============================================================
# BROWSER TEXT TO SPEECH
# ============================================================

def browser_speak(text):

    if not text:
        return

    safe_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    html = f"""
    <script>

    const textToSpeak = `{safe_text}`;

    if ("speechSynthesis" in window) {{

        window.speechSynthesis.cancel();

        const utterance =
            new SpeechSynthesisUtterance(textToSpeak);

        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        window.speechSynthesis.speak(utterance);
    }}

    </script>
    """

    st.html(html)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-icon">🎙️</div>
            <div class="sidebar-title">Personal SIRI</div>
            <div class="sidebar-subtitle">
                AI Voice & Chat Assistant
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "➕  New Chat",
        use_container_width=True,
    ):
        new_chat()
        st.rerun()

    st.markdown(
        '<div class="sidebar-section">HISTORY</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:

        for i, chat in enumerate(
            st.session_state.chat_history
        ):

            if st.button(
                f"💬  {chat['title']}",
                key=f"history_{i}",
                use_container_width=True,
            ):

                load_chat(i)
                st.rerun()

    else:

        st.caption("No previous chats yet.")

    st.markdown(
        '<div class="sidebar-section">SETTINGS</div>',
        unsafe_allow_html=True,
    )

    st.caption("🎙️ Voice Input")
    st.caption("🔊 Browser Voice Output")
    st.caption("🤖 Groq AI")


# ============================================================
# MAIN HEADER
# IMPORTANT: USE st.html() HERE
# ============================================================

st.html(
    """
    <div class="siri-header">
        <div class="siri-icon">🎙️</div>

        <div class="siri-title">
            Personal SIRI
        </div>

        <div class="siri-subtitle">
            Your Personal AI Voice & Chat Assistant
        </div>
    </div>
    """
)


# ============================================================
# STATUS INFORMATION
# ============================================================

now = datetime.now()

date_text = now.strftime("%d %b %Y")
time_text = now.strftime("%I:%M:%S %p")


st.html(
    f"""
    <div class="status-row">

        <div class="status-card">
            <span class="status-icon">📅</span>
            <span>{date_text}</span>
        </div>

        <div class="status-card">
            <span class="status-icon">🕐</span>
            <span>{time_text}</span>
        </div>

        <div class="status-card status-ready">
            <span>🟢</span>
            <span>Ready</span>
        </div>

    </div>
    """
)


# ============================================================
# CHAT HEADING
# ============================================================

st.markdown(
    '<div class="chat-heading">💬 Conversation</div>',
    unsafe_allow_html=True,
)


# ============================================================
# ONLY CHAT AREA SCROLLS
# ============================================================

with st.container(
    height=390,
    border=True,
):

    if not st.session_state.messages:

        st.html(
            """
            <div class="chat-empty">

                <div class="empty-icon">
                    🎙️
                </div>

                <div class="empty-title">
                    How can I help you?
                </div>

                <div class="empty-text">
                    Ask me anything by typing below<br>
                    or use <b>Start Voice</b>.
                </div>

            </div>
            """
        )

    else:

        for message in st.session_state.messages:

            if message["role"] == "user":

                with st.chat_message(
                    "user",
                    avatar="👤",
                ):
                    st.markdown(message["content"])

            else:

                with st.chat_message(
                    "assistant",
                    avatar="🎙️",
                ):
                    st.markdown(message["content"])


# ============================================================
# MESSAGE INPUT
# ============================================================

st.markdown(
    '<div class="input-label">💬 Message</div>',
    unsafe_allow_html=True,
)


col_input, col_send = st.columns(
    [8, 1],
    gap="small",
)


with col_input:

    user_input = st.text_input(
        "Message",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        key="message_input",
    )


with col_send:

    send_clicked = st.button(
        "➤",
        use_container_width=True,
        key="send_button",
    )


if send_clicked and user_input.strip():

    send_message(user_input)

    st.rerun()


# ============================================================
# VOICE BUTTONS
# ============================================================

st.markdown(
    '<div class="voice-area"></div>',
    unsafe_allow_html=True,
)

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


# ============================================================
# VOICE INPUT AREA
# ============================================================

if st.session_state.listening:

    st.info(
        "🎙️ Listening area opened. "
        "Record your voice and then stop recording."
    )

    audio_value = st.audio_input(
        "Record your voice",
        key="voice_recorder",
    )

    if audio_value is not None:

        audio_bytes = audio_value.getvalue()

        audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            audio_hash
            != st.session_state.audio_processed
        ):

            st.session_state.audio_processed = audio_hash

            recognized_text = recognize_audio(
                audio_bytes
            )

            if recognized_text:

                st.session_state.listening = False

                if not recognized_text.startswith(
                    (
                        "I couldn't",
                        "Speech recognition",
                    )
                ):

                    send_message(
                        recognized_text
                    )

                st.rerun()


# ============================================================
# STOP AI SPEAKING
# ============================================================

if st.session_state.speak_text:

    if st.button(
        "⏹️  Stop AI Speaking",
        use_container_width=True,
    ):

        st.session_state.speak_text = ""

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
# SPEAK LATEST AI RESPONSE
# ============================================================

if st.session_state.speak_text:

    text_to_speak = st.session_state.speak_text

    st.session_state.speak_text = ""

    browser_speak(text_to_speak)
