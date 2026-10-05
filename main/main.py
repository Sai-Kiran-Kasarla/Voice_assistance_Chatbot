# ============================================================
# PERSONAL SIRI - STREAMLIT VOICE & CHAT ASSISTANT
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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True

if "voice_gender" not in st.session_state:
    st.session_state.voice_gender = "Girl"

if "voice_speed" not in st.session_state:
    st.session_state.voice_speed = 1.0

if "listening" not in st.session_state:
    st.session_state.listening = False

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = ""

if "speak_text" not in st.session_state:
    st.session_state.speak_text = ""


# ============================================================
# GLOBAL CSS
# ============================================================

st.html(
    """
    <style>

    /* ========================================================
       PAGE
       ======================================================== */

    html,
    body {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stApp"] {
        height: 100vh !important;
        overflow: hidden !important;
    }

    [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
        background: #f5f7fb !important;
    }

    [data-testid="stMain"] {
        height: 100vh !important;
        overflow: hidden !important;
    }

    [data-testid="stMainBlockContainer"] {
        height: 100vh !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
        padding: 12px 18px 8px 18px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }


    /* ========================================================
       REMOVE DEFAULT STREAMLIT SPACING
       ======================================================== */

    [data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #dbe2eb !important;
    }

    section[data-testid="stSidebar"] > div {
        height: 100vh !important;
        overflow-y: auto !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 18px 12px !important;
    }


    /* ========================================================
       HEADER
       ======================================================== */

    .siri-header {
        width: 100%;
        height: 108px;

        box-sizing: border-box;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        text-align: center;

        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                #eef3ff 0%,
                #f6f1ff 50%,
                #eefaff 100%
            );

        border: 1px solid #d7e1ef;

        box-shadow:
            0 5px 18px rgba(37, 99, 235, 0.08);

        margin-bottom: 7px;
    }

    .siri-icon {
        font-size: 30px;
        line-height: 30px;
        margin-bottom: 2px;
    }

    .siri-title {
        font-size: 34px;
        line-height: 38px;
        font-weight: 800;
        letter-spacing: -0.7px;
        color: #2563d8;
        margin: 0;
    }

    .siri-subtitle {
        font-size: 12px;
        line-height: 17px;
        font-weight: 500;
        color: #667085;
        margin-top: 2px;
    }


    /* ========================================================
       EMPTY CHAT
       ======================================================== */

    .empty-box {
        height: 100%;

        display: flex;
        flex-direction: column;

        align-items: center;
        justify-content: center;

        text-align: center;

        color: #667085;
    }

    .empty-icon {
        font-size: 46px;
        margin-bottom: 8px;
    }

    .empty-heading {
        font-size: 22px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
    }

    .empty-description {
        font-size: 13px;
        color: #7b8494;
    }


    /* ========================================================
       CHAT CONTAINER
       ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1px solid #d5dce7 !important;
        background: #ffffff !important;
    }


    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    [data-testid="stChatMessage"] {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 14px !important;
        line-height: 1.55 !important;
    }


    /* ========================================================
       TEXT INPUT
       ======================================================== */

    [data-testid="stTextInput"] {
        margin: 0 !important;
    }

    [data-testid="stTextInput"] input {
        height: 43px !important;
        min-height: 43px !important;

        border-radius: 10px !important;

        border: 1px solid #cfd7e3 !important;

        background: #ffffff !important;

        font-size: 14px !important;

        padding-left: 14px !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #2563d8 !important;

        box-shadow:
            0 0 0 2px
            rgba(37, 99, 216, 0.12) !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        height: 42px !important;
        min-height: 42px !important;

        border-radius: 10px !important;

        font-weight: 650 !important;

        border: 1px solid #d0d8e4 !important;

        background: #ffffff !important;

        transition: 0.15s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow:
            0 4px 12px
            rgba(15, 23, 42, 0.10) !important;
    }


    /* SEND */

    .send-button button {
        background: #ff4b55 !important;
        color: white !important;
        border-color: #ff4b55 !important;
    }


    /* VOICE */

    .voice-button button {
        background: #2563d8 !important;
        color: white !important;
        border-color: #2563d8 !important;
    }


    /* STOP */

    .stop-button button {
        background: #dc3545 !important;
        color: white !important;
        border-color: #dc3545 !important;
    }


    /* ========================================================
       STATUS
       ======================================================== */

    .status-ready {
        height: 38px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 9px;

        background: #dcfce7;

        color: #15803d;

        border: 1px solid #bbf7d0;

        font-size: 13px;

        font-weight: 700;
    }

    .status-listening {
        height: 38px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 9px;

        background: #fee2e2;

        color: #dc2626;

        border: 1px solid #fecaca;

        font-size: 13px;

        font-weight: 700;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        [data-testid="stMainBlockContainer"] {
            padding: 7px 8px !important;
        }

        .siri-header {
            height: 100px;
            border-radius: 14px;
        }

        .siri-icon {
            font-size: 26px;
        }

        .siri-title {
            font-size: 28px;
            line-height: 32px;
        }

        .siri-subtitle {
            font-size: 10px;
        }
    }

    </style>
    """
)


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = str(
            st.secrets["GROQ_API_KEY"]
        ).strip()
    except Exception:
        GROQ_API_KEY = ""


# ============================================================
# GROQ CLIENT
# ============================================================

client = None

if GROQ_API_KEY:
    try:
        client = Groq(
            api_key=GROQ_API_KEY
        )
    except Exception:
        client = None


MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Personal SIRI, a helpful AI voice and chat assistant.

Be friendly, clear and concise.

Help with:
Python, Java, SQL, AI, Generative AI,
Machine Learning, Cloud Computing, AWS,
Linux, Networking, Aptitude, Interviews,
Placements and Programming Projects.

For technical questions, explain step by step
when necessary.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:
        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please add GROQ_API_KEY in Streamlit "
            "Cloud → Manage app → Settings → Secrets."
        )

    try:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        for message in st.session_state.messages:

            conversation.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )

        conversation.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=0.7,
            max_tokens=1200
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "⚠️ Groq request failed.\n\n"
            f"{error}"
        )


# ============================================================
# SAVE CHAT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    chat = {
        "title": st.session_state.chat_title,
        "messages": [
            {
                "role": m["role"],
                "content": m["content"]
            }
            for m in st.session_state.messages
        ]
    }

    found = False

    for i, old_chat in enumerate(
        st.session_state.history
    ):

        if (
            old_chat["title"]
            == st.session_state.chat_title
        ):

            st.session_state.history[i] = chat
            found = True
            break

    if not found:
        st.session_state.history.append(chat)


# ============================================================
# NEW CHAT
# ============================================================

def new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


# ============================================================
# CLEAR CHAT
# ============================================================

def clear_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


# ============================================================
# LOAD CHAT
# ============================================================

def load_chat(index):

    selected = st.session_state.history[index]

    st.session_state.chat_title = selected["title"]

    st.session_state.messages = [
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in selected["messages"]
    ]


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(message):

    message = message.strip()

    if not message:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    if st.session_state.chat_title == "New Chat":

        title = message[:28]

        if len(message) > 28:
            title += "..."

        st.session_state.chat_title = title

    answer = get_ai_response(message)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    save_current_chat()

    if st.session_state.tts_enabled:
        st.session_state.speak_text = answer
    else:
        st.session_state.speak_text = ""


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()


def convert_audio_to_text(audio):

    if audio is None:
        return ""

    try:

        audio_bytes = audio.getvalue()

        buffer = io.BytesIO(audio_bytes)

        with sr.AudioFile(buffer) as source:

            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(
            audio_data
        )

        return text.strip()

    except sr.UnknownValueError:

        st.warning(
            "I couldn't understand your voice."
        )

        return ""

    except sr.RequestError:

        st.error(
            "Speech recognition service is unavailable."
        )

        return ""

    except Exception as error:

        st.error(
            f"Audio error: {error}"
        )

        return ""


# ============================================================
# BROWSER TEXT TO SPEECH
# ============================================================

def speak_text(text):

    if not text:
        return

    safe_text = json.dumps(str(text))

    if st.session_state.voice_gender == "Girl":

        voice_script = """
        let preferredVoice = voices.find(
            v => /female|zira|samantha|susan|aria|hazel/i
            .test(v.name)
        );
        """

    else:

        voice_script = """
        let preferredVoice = voices.find(
            v => /male|david|mark|george/i
            .test(v.name)
        );
        """

    st.html(
        f"""
        <script>

        const text = {safe_text};

        function speakSiri() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.rate =
                {st.session_state.voice_speed};

            utterance.pitch = 1;

            utterance.volume = 1;

            const voices =
                window.speechSynthesis.getVoices();

            {voice_script}

            if (preferredVoice) {{
                utterance.voice = preferredVoice;
            }}

            window.speechSynthesis.speak(
                utterance
            );
        }}

        setTimeout(
            speakSiri,
            250
        );

        </script>
        """
    )


# ============================================================
# STOP SPEECH
# ============================================================

def stop_speech():

    st.html(
        """
        <script>
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        </script>
        """
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "### 🎙️ Personal SIRI"
    )

    st.caption(
        "AI Voice & Chat Assistant"
    )

    st.write("")

    # NEW CHAT

    if st.button(
        "➕  New Chat",
        use_container_width=True
    ):

        new_chat()
        st.rerun()


    # HISTORY

    st.markdown(
        "##### 🕘 HISTORY"
    )

    if st.session_state.history:

        for index, chat in enumerate(
            st.session_state.history
        ):

            title = chat["title"]

            if len(title) > 23:
                title = title[:23] + "..."

            if st.button(
                "💬  " + title,
                key=f"history_{index}",
                use_container_width=True
            ):

                load_chat(index)
                st.rerun()

    else:

        st.caption(
            "No previous chats"
        )


    # CURRENT CHAT

    st.markdown(
        "##### 💬 CURRENT CHAT"
    )

    if st.button(
        "🗑️  Clear Current Chat",
        use_container_width=True
    ):

        clear_chat()
        st.rerun()


    # VOICE SETTINGS

    st.markdown(
        "##### 🎙️ VOICE SETTINGS"
    )

    st.session_state.tts_enabled = st.checkbox(
        "Voice Response",
        value=st.session_state.tts_enabled
    )

    st.session_state.voice_gender = st.radio(
        "Voice",
        ["Girl", "Boy"],
        index=(
            0
            if st.session_state.voice_gender == "Girl"
            else 1
        )
    )

    st.session_state.voice_speed = st.slider(
        "Speech Speed",
        0.7,
        1.4,
        st.session_state.voice_speed,
        0.1
    )


    st.divider()


    # API STATUS

    if client:

        st.success(
            "🟢 Groq Connected"
        )

    else:

        st.error(
            "🔴 Groq API Not Connected"
        )


    # CLEAR HISTORY

    if st.button(
        "🗑️  Clear All History",
        use_container_width=True
    ):

        st.session_state.history = []

        st.session_state.messages = []

        st.session_state.chat_title = "New Chat"

        st.rerun()


# ============================================================
# MAIN TITLE
# ============================================================

st.html(
    """
    <div class="siri-header">

        <div class="siri-icon">
            🎙️
        </div>

        <div class="siri-title">
            Personal SIRI
        </div>

        <div class="siri-subtitle">
            Your Personal AI Voice &amp; Chat Assistant
        </div>

    </div>
    """
)


# ============================================================
# STATUS ROW
# ============================================================

date_col, time_col, status_col = st.columns(
    [1, 1, 1]
)


now = datetime.now()


with date_col:

    st.info(
        "📅 " + now.strftime("%d %b %Y")
    )


with time_col:

    st.info(
        "🕐 " + now.strftime("%I:%M:%S %p")
    )


with status_col:

    if st.session_state.listening:

        st.html(
            """
            <div class="status-listening">
                🔴 Listening
            </div>
            """
        )

    else:

        st.html(
            """
            <div class="status-ready">
                🟢 Ready
            </div>
            """
        )


# ============================================================
# CHAT AREA
#
# IMPORTANT:
# We are NOT wrapping Streamlit widgets inside HTML.
# st.container() is the scrollable chat area.
# ============================================================

with st.container(
    height=455,
    border=True
):

    if not st.session_state.messages:

        st.html(
            """
            <div class="empty-box">

                <div class="empty-icon">
                    🎙️
                </div>

                <div class="empty-heading">
                    How can I help you?
                </div>

                <div class="empty-description">
                    Type a message below or use Start Voice.
                </div>

            </div>
            """
        )

    else:

        for message in st.session_state.messages:

            if message["role"] == "user":

                with st.chat_message(
                    "user",
                    avatar="👤"
                ):

                    st.markdown(
                        message["content"]
                    )

            else:

                with st.chat_message(
                    "assistant",
                    avatar="🎙️"
                ):

                    st.markdown(
                        message["content"]
                    )


# ============================================================
# MESSAGE INPUT
# ============================================================

input_col, send_col = st.columns(
    [6.7, 1]
)


with input_col:

    user_message = st.text_input(
        "Message",
        placeholder="💬 Message Personal SIRI...",
        label_visibility="collapsed"
    )


with send_col:

    st.markdown(
        '<div class="send-button">',
        unsafe_allow_html=True
    )

    send_clicked = st.button(
        "➤ Send",
        use_container_width=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SEND
# ============================================================

if send_clicked:

    if user_message.strip():

        process_message(
            user_message
        )

        st.rerun()


# ============================================================
# VOICE BUTTON
# ============================================================

voice_col_left, voice_col, voice_col_right = st.columns(
    [1, 4, 1]
)


with voice_col:

    if not st.session_state.listening:

        st.markdown(
            '<div class="voice-button">',
            unsafe_allow_html=True
        )

        start_voice = st.button(
            "🎙️  Start Voice",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if start_voice:

            st.session_state.listening = True

            st.rerun()

    else:

        st.markdown(
            '<div class="stop-button">',
            unsafe_allow_html=True
        )

        stop_voice = st.button(
            "⏹️  Stop Listening",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if stop_voice:

            st.session_state.listening = False

            st.rerun()


# ============================================================
# AUDIO INPUT
# ============================================================

if st.session_state.listening:

    audio_value = st.audio_input(
        "🎤 Record your message"
    )

    if audio_value is not None:

        audio_bytes = audio_value.getvalue()

        current_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            current_hash
            != st.session_state.last_audio_hash
        ):

            st.session_state.last_audio_hash = (
                current_hash
            )

            recognized_text = (
                convert_audio_to_text(
                    audio_value
                )
            )

            st.session_state.listening = False

            if recognized_text:

                process_message(
                    recognized_text
                )

                st.rerun()


# ============================================================
# STOP AI SPEAKING
# ============================================================

left, center, right = st.columns(
    [1, 2, 1]
)


with center:

    if st.button(
        "⏹️ Stop AI Speaking",
        use_container_width=True
    ):

        stop_speech()

        st.session_state.speak_text = ""

        st.rerun()


# ============================================================
# TEXT TO SPEECH
# ============================================================

if st.session_state.speak_text:

    text = st.session_state.speak_text

    st.session_state.speak_text = ""

    speak_text(text)
