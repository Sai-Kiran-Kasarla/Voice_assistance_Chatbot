# ============================================================
# PERSONAL SIRI
# Dynamic Voice + Chat Assistant
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

defaults = {
    "messages": [],
    "history": [],
    "chat_title": "New Chat",
    "tts_enabled": True,
    "voice_gender": "Girl",
    "voice_speed": 1.0,
    "listening": False,
    "last_audio_hash": "",
    "speak_text": "",
    "show_voice_panel": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# MODERN UI CSS
# ============================================================

st.html(
    """
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

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
    background: #f7f8fc !important;
}

[data-testid="stMain"] {
    height: 100vh !important;
    overflow: hidden !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1380px !important;
    height: 100vh !important;

    margin: 0 auto !important;

    padding:
        12px 18px 10px 18px !important;

    box-sizing: border-box !important;

    overflow: hidden !important;
}


/* =========================================================
   STREAMLIT SPACING
   ========================================================= */

[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e7ef !important;
}

section[data-testid="stSidebar"] > div {
    height: 100vh !important;
    overflow-y: auto !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 18px 13px !important;
}


/* =========================================================
   SIDEBAR BUTTONS
   ========================================================= */

section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 40px !important;

    border-radius: 9px !important;

    border: 1px solid #d9e0ea !important;

    background: #ffffff !important;

    font-size: 13px !important;

    color: #273142 !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #8db4ff !important;
    background: #f5f8ff !important;
}


/* =========================================================
   HEADER
   ========================================================= */

.siri-header {
    width: 100%;

    min-height: 92px;

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
            #edf3ff 0%,
            #f5f0ff 50%,
            #ecfaff 100%
        );

    border: 1px solid #dce5f2;

    box-shadow:
        0 4px 18px
        rgba(45, 91, 160, 0.07);

    margin-bottom: 7px;
}

.siri-icon {
    font-size: 27px;
    line-height: 27px;
    margin-bottom: 2px;
}

.siri-title {
    margin: 0;

    font-size: 31px;
    line-height: 35px;

    font-weight: 800;

    letter-spacing: -0.7px;

    color: #2563d8;
}

.siri-subtitle {
    margin-top: 2px;

    font-size: 12px;

    color: #667085;
}


/* =========================================================
   STATUS BAR
   ========================================================= */

.status-card {
    width: 100%;

    min-height: 36px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 9px;

    font-size: 12px;

    font-weight: 650;

    box-sizing: border-box;
}

.status-ready {
    background: #e9f9ef;
    color: #15803d;
    border: 1px solid #c7efd4;
}

.status-listening {
    background: #fff0f0;
    color: #dc2626;
    border: 1px solid #ffd1d1;
}

.status-connected {
    background: #eef5ff;
    color: #2563d8;
    border: 1px solid #d4e3ff;
}


/* =========================================================
   INFO BOXES
   ========================================================= */

[data-testid="stAlert"] {
    min-height: 36px !important;

    padding: 7px 12px !important;

    border-radius: 9px !important;

    font-size: 12px !important;
}


/* =========================================================
   CHAT CONTAINER
   ========================================================= */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px !important;

    border:
        1px solid #dce2eb !important;

    background: #ffffff !important;

    box-shadow:
        0 2px 8px
        rgba(15, 23, 42, 0.025) !important;
}


/* =========================================================
   EMPTY STATE
   ========================================================= */

.empty-state {
    height: 100%;

    min-height: 330px;

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
    font-size: 21px;

    font-weight: 750;

    color: #202938;

    margin-bottom: 5px;
}

.empty-text {
    font-size: 13px;

    color: #7a8494;

    max-width: 400px;
}


/* =========================================================
   CHAT MESSAGES
   ========================================================= */

[data-testid="stChatMessage"] {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
}

[data-testid="stChatMessageContent"] {
    font-size: 14px !important;
    line-height: 1.55 !important;
}


/* =========================================================
   INPUT AREA
   ========================================================= */

[data-testid="stTextInput"] {
    margin: 0 !important;
}

[data-testid="stTextInput"] input {
    height: 44px !important;

    min-height: 44px !important;

    box-sizing: border-box !important;

    border-radius: 12px !important;

    border: 1px solid #cfd7e4 !important;

    background: #ffffff !important;

    padding:
        0 14px !important;

    font-size: 14px !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #4c82e8 !important;

    box-shadow:
        0 0 0 2px
        rgba(76, 130, 232, 0.10) !important;
}


/* =========================================================
   SEND BUTTON
   ========================================================= */

.st-key-send_button button {
    height: 44px !important;

    border-radius: 12px !important;

    background: #ff4b55 !important;

    color: white !important;

    border-color: #ff4b55 !important;

    font-weight: 700 !important;
}

.st-key-send_button button:hover {
    background: #ef3f49 !important;
}


/* =========================================================
   MIC BUTTON
   ========================================================= */

.st-key-mic_button button {
    height: 44px !important;

    border-radius: 12px !important;

    background: #eef4ff !important;

    color: #2563d8 !important;

    border: 1px solid #cbdcff !important;

    font-size: 18px !important;

    font-weight: 700 !important;
}

.st-key-mic_button button:hover {
    background: #e1ebff !important;
}


/* =========================================================
   VOICE PANEL
   ========================================================= */

.voice-panel {
    padding: 8px 12px;

    border-radius: 12px;

    background: #f1f6ff;

    border: 1px solid #d8e5ff;

    text-align: center;

    color: #315ca8;

    font-size: 12px;

    margin-top: 2px;
}


/* =========================================================
   STOP BUTTON
   ========================================================= */

.st-key-stop_voice button {
    height: 40px !important;

    border-radius: 10px !important;

    background: #dc3545 !important;

    color: white !important;

    border-color: #dc3545 !important;
}


/* =========================================================
   SPEAKING BUTTON
   ========================================================= */

.st-key-stop_speaking button {
    height: 38px !important;

    border-radius: 10px !important;

    background: #f97316 !important;

    color: white !important;

    border-color: #f97316 !important;
}


/* =========================================================
   AUDIO INPUT
   ========================================================= */

[data-testid="stAudioInput"] {
    width: 100% !important;
}

[data-testid="stAudioInput"] button {
    border-radius: 10px !important;
}


/* =========================================================
   DIVIDER
   ========================================================= */

hr {
    margin: 5px 0 !important;

    border-color: #e4e8ef !important;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 800px) {

    [data-testid="stMainBlockContainer"] {
        padding: 7px 8px 8px 8px !important;
    }

    .siri-header {
        min-height: 82px;
        border-radius: 14px;
    }

    .siri-icon {
        font-size: 23px;
    }

    .siri-title {
        font-size: 26px;
        line-height: 30px;
    }

    .siri-subtitle {
        font-size: 10px;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 13px !important;
    }
}


/* =========================================================
   DARK MODE
   ========================================================= */

@media (prefers-color-scheme: dark) {

    [data-testid="stAppViewContainer"] {
        background: #0f172a !important;
    }

    section[data-testid="stSidebar"] {
        background: #111827 !important;
        border-color: #273449 !important;
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

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #111827 !important;
        border-color: #334155 !important;
    }

    .empty-title {
        color: #f8fafc;
    }

    .empty-text {
        color: #94a3b8;
    }

    [data-testid="stTextInput"] input {
        background: #111827 !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
    }

    .st-key-mic_button button {
        background: #172554 !important;
        color: #93c5fd !important;
        border-color: #315aa8 !important;
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
You are Personal SIRI, a helpful personal AI assistant.

Give clear, useful and natural answers.

You can help with:
- Programming
- Python
- Java
- SQL
- AI
- Generative AI
- Machine Learning
- Cloud Computing
- AWS
- Linux
- Networking
- Aptitude
- Interview preparation
- Resume and placement preparation
- College projects

For technical questions, use examples and
step-by-step explanations when useful.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:
        return (
            "⚠️ **Groq API is not connected.**\n\n"
            "Please add your `GROQ_API_KEY` in "
            "Streamlit Cloud → Manage app → Settings → Secrets."
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
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "⚠️ **Groq error**\n\n"
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

    found = False

    for i, old_chat in enumerate(
        st.session_state.history
    ):

        if old_chat["title"] == \
                st.session_state.chat_title:

            st.session_state.history[i] = chat

            found = True

            break

    if not found:

        st.session_state.history.append(
            chat
        )


# ============================================================
# NEW CHAT
# ============================================================

def new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""

    st.session_state.listening = False

    st.session_state.show_voice_panel = False


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

    st.session_state.chat_title = \
        selected["title"]

    st.session_state.messages = [
        {
            "role": item["role"],
            "content": item["content"]
        }
        for item in selected["messages"]
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

        title = message[:30]

        if len(message) > 30:
            title += "..."

        st.session_state.chat_title = title

    answer = get_ai_response(
        message
    )

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
            "I couldn't understand the recording."
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
# TEXT TO SPEECH
# ============================================================

def speak_text(text):

    if not text:
        return

    safe_text = json.dumps(
        str(text)
    )

    if st.session_state.voice_gender == "Girl":

        voice_script = """
        let preferredVoice = voices.find(
            v =>
            /female|zira|samantha|susan|aria|hazel/i
            .test(v.name)
        );
        """

    else:

        voice_script = """
        let preferredVoice = voices.find(
            v =>
            /male|david|mark|george/i
            .test(v.name)
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

            const utterance =
                new SpeechSynthesisUtterance(
                    siriText
                );

            utterance.rate =
                {st.session_state.voice_speed};

            utterance.pitch = 1;

            utterance.volume = 1;

            const voices =
                window.speechSynthesis.getVoices();

            {voice_script}

            if (preferredVoice) {{
                utterance.voice =
                    preferredVoice;
            }}

            window.speechSynthesis.speak(
                utterance
            );
        }}

        setTimeout(
            speakSiri,
            200
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
        "Your AI Voice & Chat Assistant"
    )

    st.write("")

    # NEW CHAT

    if st.button(
        "➕  New Chat",
        use_container_width=True,
        key="new_chat_button"
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

            if len(title) > 24:
                title = title[:24] + "..."

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


    st.markdown(
        "##### 💬 CURRENT CHAT"
    )

    if st.button(
        "🗑️  Clear Current Chat",
        use_container_width=True,
        key="clear_current"
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
        min_value=0.7,
        max_value=1.4,
        value=st.session_state.voice_speed,
        step=0.1
    )

    st.divider()


    # CONNECTION STATUS

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
        use_container_width=True,
        key="clear_history"
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
# STATUS ROW
# ============================================================

date_col, status_col, connection_col = st.columns(
    [1, 1, 1]
)

now = datetime.now()


with date_col:

    st.info(
        "📅  " +
        now.strftime("%d %b %Y")
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


with connection_col:

    if client:

        st.html(
            """
            <div class="status-card status-connected">
                ⚡ Groq Online
            </div>
            """
        )

    else:

        st.html(
            """
            <div class="status-card status-listening">
                🔴 API Not Connected
            </div>
            """
        )


# ============================================================
# CHAT
#
# ONLY CHAT SCROLLS
# ============================================================

with st.container(
    height=470,
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
                    or use the microphone.
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
# INPUT ROW
#
# TEXT + MIC + SEND
# ============================================================

text_col, mic_col, send_col = st.columns(
    [7.0, 0.8, 1.2]
)


# ============================================================
# TEXT INPUT
# ============================================================

with text_col:

    user_message = st.text_input(
        "Message Personal SIRI",
        placeholder="Message Personal SIRI...",
        label_visibility="collapsed",
        key="user_message"
    )


# ============================================================
# MICROPHONE
# ============================================================

with mic_col:

    mic_clicked = st.button(
        "🎙️",
        key="mic_button",
        help="Use microphone",
        use_container_width=True
    )


# ============================================================
# SEND
# ============================================================

with send_col:

    send_clicked = st.button(
        "➤ Send",
        key="send_button",
        type="primary",
        use_container_width=True
    )


# ============================================================
# MIC CLICK
# ============================================================

if mic_clicked:

    st.session_state.show_voice_panel = True

    st.session_state.listening = True

    st.rerun()


# ============================================================
# SEND TEXT
# ============================================================

if send_clicked:

    if user_message.strip():

        process_message(
            user_message
        )

        st.rerun()


# ============================================================
# DYNAMIC VOICE PANEL
# ============================================================

if st.session_state.show_voice_panel:

    st.html(
        """
        <div class="voice-panel">
            🎙️ Microphone mode active —
            record your message below.
        </div>
        """
    )


    audio_value = st.audio_input(
        "🎤 Record your message",
        label_visibility="visible",
        key="voice_recorder"
    )


    # STOP LISTENING

    if st.button(
        "⏹️ Stop Listening",
        key="stop_voice",
        use_container_width=True
    ):

        st.session_state.listening = False

        st.session_state.show_voice_panel = False

        st.rerun()


    # PROCESS RECORDING

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

            st.session_state.show_voice_panel = False

            if recognized_text:

                process_message(
                    recognized_text
                )

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
            "⏹️ Stop AI Speaking",
            key="stop_speaking",
            use_container_width=True
        ):

            stop_speech()

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

    speak_text(
        response_text
    )
