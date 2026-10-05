# ============================================================
# PERSONAL SIRI
# Voice + Chat AI Assistant
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

DEFAULTS = {
    "messages": [],
    "history": [],
    "chat_title": "New Chat",

    "tts_enabled": True,
    "voice_gender": "Girl",
    "voice_speed": 1.0,

    "listening": False,
    "last_audio_hash": "",
    "speak_text": "",

    "audio_key": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.html(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

html,
body {
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stApp"] {
    background: #f5f7fb !important;
}

[data-testid="stAppViewContainer"] {
    background: #f5f7fb !important;
}

[data-testid="stMain"] {
    overflow: hidden !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 10px 18px 8px 18px !important;
    box-sizing: border-box !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0.3rem !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #dce3ec !important;
}

section[data-testid="stSidebar"] > div {
    height: 100vh !important;
    overflow-y: auto !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 18px 12px !important;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.sidebar-brand {
    font-size: 21px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 2px;
}

.sidebar-description {
    font-size: 12px;
    color: #7b8494;
    margin-bottom: 16px;
}


/* ============================================================
   SIDEBAR BUTTONS
   ============================================================ */

section[data-testid="stSidebar"] .stButton > button {
    min-height: 40px !important;
    border-radius: 9px !important;
    border: 1px solid #d7dfeb !important;
    background: #ffffff !important;
    color: #273142 !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f4f7ff !important;
    border-color: #9ebcf0 !important;
}


/* ============================================================
   MAIN HEADER
   ============================================================ */

.siri-header {
    width: 100%;
    height: 96px;

    box-sizing: border-box;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    text-align: center;

    border-radius: 17px;

    background:
        linear-gradient(
            135deg,
            #edf4ff 0%,
            #f5f1ff 50%,
            #edfbff 100%
        );

    border: 1px solid #d7e2f0;

    box-shadow:
        0 3px 14px rgba(37, 99, 235, 0.06);

    margin-bottom: 7px;
}

.siri-icon {
    font-size: 27px;
    line-height: 27px;
    height: 27px;
    margin-bottom: 1px;
}

.siri-title {
    font-size: 31px;
    line-height: 35px;
    height: 35px;
    font-weight: 800;
    letter-spacing: -0.7px;
    color: #2563d8;
}

.siri-subtitle {
    font-size: 12px;
    line-height: 17px;
    color: #667085;
    margin-top: 1px;
}


/* ============================================================
   STATUS
   ============================================================ */

.status-card {
    height: 36px;
    min-height: 36px;
    width: 100%;

    display: flex;
    align-items: center;
    justify-content: center;

    box-sizing: border-box;

    border-radius: 9px;

    font-size: 12px;
    font-weight: 650;
}

.status-ready {
    background: #e9f9ef;
    color: #15803d;
    border: 1px solid #c5ecd2;
}

.status-connected {
    background: #edf5ff;
    color: #2563d8;
    border: 1px solid #d3e2ff;
}

.status-listening {
    background: #fff0f0;
    color: #dc2626;
    border: 1px solid #ffd1d1;
}


/* ============================================================
   CHAT CONTAINER
   ============================================================ */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border: 1px solid #d7dee8 !important;
    background: #ffffff !important;

    box-shadow:
        0 2px 10px rgba(15, 23, 42, 0.03) !important;
}


/* ============================================================
   EMPTY CHAT
   ============================================================ */

.empty-state {
    min-height: 300px;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;

    text-align: center;
}

.empty-icon {
    width: 70px;
    height: 70px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #eef4ff;

    font-size: 32px;

    margin-bottom: 13px;
}

.empty-title {
    font-size: 22px;
    font-weight: 750;
    color: #1f2937;
    margin-bottom: 5px;
}

.empty-text {
    font-size: 13px;
    color: #7a8494;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {
    padding-top: 5px !important;
    padding-bottom: 5px !important;
}

[data-testid="stChatMessageContent"] {
    font-size: 14px !important;
    line-height: 1.55 !important;
}


/* ============================================================
   TEXT INPUT
   ============================================================ */

[data-testid="stTextInput"] {
    margin: 0 !important;
}

[data-testid="stTextInput"] input {
    height: 44px !important;
    min-height: 44px !important;

    border-radius: 11px !important;

    border: 1px solid #ccd5e2 !important;

    background: #ffffff !important;

    color: #1f2937 !important;

    font-size: 14px !important;

    padding: 0 14px !important;

    box-sizing: border-box !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #4d82e8 !important;

    box-shadow:
        0 0 0 2px rgba(77, 130, 232, 0.10) !important;
}


/* ============================================================
   SEND BUTTON
   ============================================================ */

.st-key-send_button button {
    height: 44px !important;
    min-height: 44px !important;

    border-radius: 11px !important;

    background: #ff4b55 !important;

    color: #ffffff !important;

    border: 1px solid #ff4b55 !important;

    font-weight: 700 !important;
}

.st-key-send_button button:hover {
    background: #ed3e49 !important;
}


/* ============================================================
   START VOICE
   ============================================================ */

.st-key-start_voice button {
    height: 40px !important;
    min-height: 40px !important;

    border-radius: 10px !important;

    background: #2563d8 !important;

    color: #ffffff !important;

    border: 1px solid #2563d8 !important;

    font-weight: 700 !important;
}

.st-key-start_voice button:hover {
    background: #1d55bd !important;
}


/* ============================================================
   STOP VOICE
   ============================================================ */

.st-key-stop_voice button {
    height: 40px !important;
    min-height: 40px !important;

    border-radius: 10px !important;

    background: #dc3545 !important;

    color: #ffffff !important;

    border: 1px solid #dc3545 !important;
}


/* ============================================================
   STOP AI SPEAKING
   ============================================================ */

.st-key-stop_speaking button {
    height: 38px !important;
    min-height: 38px !important;

    border-radius: 9px !important;

    background: #f97316 !important;

    color: #ffffff !important;

    border: 1px solid #f97316 !important;

    font-weight: 650 !important;
}


/* ============================================================
   AUDIO INPUT
   ============================================================ */

[data-testid="stAudioInput"] {
    width: 100% !important;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 800px) {

    [data-testid="stMainBlockContainer"] {
        padding: 7px 8px !important;
    }

    .siri-header {
        height: 82px;
    }

    .siri-icon {
        font-size: 23px;
    }

    .siri-title {
        font-size: 26px;
        line-height: 29px;
        height: 29px;
    }

    .siri-subtitle {
        font-size: 10px;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 13px !important;
    }
}


/* ============================================================
   DARK MODE
   ============================================================ */

@media (prefers-color-scheme: dark) {

    [data-testid="stAppViewContainer"] {
        background: #0f172a !important;
    }

    section[data-testid="stSidebar"] {
        background: #111827 !important;
        border-color: #2b374b !important;
    }

    .sidebar-brand {
        color: #f1f5f9;
    }

    .siri-header {
        background:
            linear-gradient(
                135deg,
                #172554,
                #241b43,
                #083344
            );

        border-color: #334155;
    }

    .siri-title {
        color: #60a5fa;
    }

    .siri-subtitle {
        color: #cbd5e1;
    }

    .empty-title {
        color: #f8fafc;
    }

    .empty-text {
        color: #94a3b8;
    }

    [data-testid="stTextInput"] input {
        background: #111827 !important;
        color: #ffffff !important;
        border-color: #475569 !important;
    }
}

</style>
"""
)


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
).strip()

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
You are Personal SIRI, a helpful AI assistant.

Be clear, friendly and practical.

You can help with:
Python, Java, SQL, AI, Generative AI,
Machine Learning, Cloud Computing, AWS,
Linux, Networking, Aptitude, Interviews,
Placements, Resume preparation and Projects.

For technical questions, provide step-by-step
explanations when useful.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response():

    if client is None:

        return (
            "⚠️ **Groq API is not connected.**\n\n"
            "Please add `GROQ_API_KEY` in "
            "Streamlit Cloud → Manage app → "
            "Settings → Secrets."
        )

    try:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        conversation.extend(
            st.session_state.messages
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=0.7,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "⚠️ **Groq Error**\n\n"
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
                "role": item["role"],
                "content": item["content"]
            }

            for item in st.session_state.messages
        ]
    }

    for index, old_chat in enumerate(
        st.session_state.history
    ):

        if (
            old_chat["title"]
            ==
            st.session_state.chat_title
        ):

            st.session_state.history[index] = chat

            return

    st.session_state.history.append(chat)


# ============================================================
# NEW CHAT
# ============================================================

def create_new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""

    st.session_state.listening = False


# ============================================================
# CLEAR CURRENT CHAT
# ============================================================

def clear_current_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""

    st.session_state.listening = False


# ============================================================
# LOAD CHAT
# ============================================================

def load_chat(index):

    selected = st.session_state.history[index]

    st.session_state.chat_title = (
        selected["title"]
    )

    st.session_state.messages = [
        {
            "role": item["role"],
            "content": item["content"]
        }

        for item in selected["messages"]
    ]


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
            "content": message
        }
    )

    if (
        st.session_state.chat_title
        ==
        "New Chat"
    ):

        title = message[:30]

        if len(message) > 30:
            title += "..."

        st.session_state.chat_title = title

    answer = get_ai_response()

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


def recognize_audio(audio):

    if audio is None:
        return ""

    try:

        audio_bytes = audio.getvalue()

        if not audio_bytes:
            return ""

        buffer = io.BytesIO(
            audio_bytes
        )

        with sr.AudioFile(buffer) as source:

            audio_data = recognizer.record(
                source
            )

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
            f"Microphone error: {error}"
        )

        return ""


# ============================================================
# BROWSER TEXT TO SPEECH
# ============================================================

def browser_speak(text):

    if not text:
        return

    safe_text = json.dumps(
        str(text)
    )

    if (
        st.session_state.voice_gender
        ==
        "Girl"
    ):

        voice_code = """
        let selectedVoice = voices.find(
            voice =>
            /female|zira|samantha|susan|aria|hazel/i
            .test(voice.name)
        );
        """

    else:

        voice_code = """
        let selectedVoice = voices.find(
            voice =>
            /male|david|mark|george/i
            .test(voice.name)
        );
        """

    st.html(
        f"""
        <script>

        const siriText = {safe_text};

        function speakSiri() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(
                    siriText
                );

            speech.rate =
                {st.session_state.voice_speed};

            speech.pitch = 1;

            speech.volume = 1;

            const voices =
                window.speechSynthesis.getVoices();

            {voice_code}

            if (selectedVoice) {{
                speech.voice = selectedVoice;
            }}

            window.speechSynthesis.speak(
                speech
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
# STOP SPEAKING
# ============================================================

def stop_browser_speech():

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

    st.html(
        """
        <div class="sidebar-brand">
            🎙️ Personal SIRI
        </div>

        <div class="sidebar-description">
            Your Personal AI Voice & Chat Assistant
        </div>
        """
    )


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "➕  New Chat",
        use_container_width=True,
        key="new_chat_button"
    ):

        create_new_chat()

        st.rerun()


    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    st.markdown(
        "##### 🕘 HISTORY"
    )

    if st.session_state.history:

        for index, chat in enumerate(
            st.session_state.history
        ):

            title = chat["title"]

            if len(title) > 25:
                title = title[:25] + "..."

            if st.button(
                "💬  " + title,
                key=f"history_button_{index}",
                use_container_width=True
            ):

                load_chat(index)

                st.rerun()

    else:

        st.caption(
            "No previous chats"
        )


    # --------------------------------------------------------
    # CURRENT CHAT
    # --------------------------------------------------------

    st.markdown(
        "##### 💬 CURRENT CHAT"
    )

    if st.button(
        "🗑️  Clear Current Chat",
        use_container_width=True,
        key="clear_current_button"
    ):

        clear_current_chat()

        st.rerun()


    # --------------------------------------------------------
    # VOICE SETTINGS
    # --------------------------------------------------------

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
        min_value=0.7,
        max_value=1.4,
        value=st.session_state.voice_speed,
        step=0.1
    )


    st.divider()


    # --------------------------------------------------------
    # GROQ STATUS
    # --------------------------------------------------------

    if client:

        st.success(
            "🟢 Groq Connected"
        )

    else:

        st.error(
            "🔴 Groq API Not Connected"
        )


    # --------------------------------------------------------
    # CLEAR ALL HISTORY
    # --------------------------------------------------------

    if st.button(
        "🗑️  Clear All History",
        use_container_width=True,
        key="clear_history_button"
    ):

        st.session_state.history = []

        st.session_state.messages = []

        st.session_state.chat_title = "New Chat"

        st.rerun()


# ============================================================
# MAIN HEADER
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
            Your Personal AI Voice & Chat Assistant
        </div>

    </div>
    """
)


# ============================================================
# DATE / TIME / STATUS
# ============================================================

date_col, time_col, status_col = st.columns(
    [1, 1, 1]
)

current_time = datetime.now()


with date_col:

    st.info(
        "📅  "
        + current_time.strftime(
            "%d %b %Y"
        )
    )


with time_col:

    st.info(
        "🕐  "
        + current_time.strftime(
            "%I:%M:%S %p"
        )
    )


with status_col:

    if st.session_state.listening:

        st.html(
            """
            <div class="status-card status-listening">
                🔴 Listening...
            </div>
            """
        )

    else:

        st.html(
            """
            <div class="status-card status-ready">
                🟢 Ready
            </div>
            """
        )


# ============================================================
# CHAT AREA
#
# ONLY THIS CONTAINER SCROLLS
# ============================================================

with st.container(
    height=410,
    border=True
):

    if not st.session_state.messages:

        st.html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    🎙️
                </div>

                <div class="empty-title">
                    How can I help you?
                </div>

                <div class="empty-text">
                    Ask me anything by typing below
                    or use Start Voice.
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
# MESSAGE + SEND
# ============================================================

message_col, send_col = st.columns(
    [8.2, 1.3]
)


with message_col:

    user_message = st.text_input(
        "Message Personal SIRI",
        placeholder="💬 Message Personal SIRI...",
        label_visibility="collapsed",
        key="message_input"
    )


with send_col:

    send_clicked = st.button(
        "➤ Send",
        key="send_button",
        type="primary",
        use_container_width=True
    )


# ============================================================
# SEND MESSAGE
# ============================================================

if send_clicked:

    if user_message.strip():

        send_message(
            user_message
        )

        st.rerun()


# ============================================================
# START VOICE
# ============================================================

voice_left, voice_center, voice_right = st.columns(
    [1, 4, 1]
)


with voice_center:

    if not st.session_state.listening:

        start_voice_clicked = st.button(
            "🎙️  Start Voice",
            key="start_voice",
            use_container_width=True
        )

        if start_voice_clicked:

            st.session_state.listening = True

            st.rerun()

    else:

        stop_voice_clicked = st.button(
            "⏹️  Stop Listening",
            key="stop_voice",
            use_container_width=True
        )

        if stop_voice_clicked:

            st.session_state.listening = False

            st.rerun()


# ============================================================
# VOICE RECORDING
# ============================================================

if st.session_state.listening:

    audio_value = st.audio_input(
        "🎤 Record your message",
        key=f"audio_input_{st.session_state.audio_key}"
    )

    if audio_value is not None:

        audio_bytes = (
            audio_value.getvalue()
        )

        audio_hash = hashlib.md5(
            audio_bytes
        ).hexdigest()

        if (
            audio_hash
            != st.session_state.last_audio_hash
        ):

            st.session_state.last_audio_hash = (
                audio_hash
            )

            recognized_text = (
                recognize_audio(
                    audio_value
                )
            )

            st.session_state.listening = False

            if recognized_text:

                send_message(
                    recognized_text
                )

                st.session_state.audio_key += 1

                st.rerun()


# ============================================================
# STOP AI SPEAKING
# ============================================================

if st.session_state.speak_text:

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        if st.button(
            "⏹️  Stop AI Speaking",
            key="stop_speaking",
            use_container_width=True
        ):

            stop_browser_speech()

            st.session_state.speak_text = ""

            st.rerun()


# ============================================================
# TEXT TO SPEECH
# ============================================================

if st.session_state.speak_text:

    response_text = (
        st.session_state.speak_text
    )

    st.session_state.speak_text = ""

    browser_speak(
        response_text
    )
