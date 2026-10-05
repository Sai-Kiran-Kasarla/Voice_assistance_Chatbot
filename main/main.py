# ============================================================
# PERSONAL SIRI
# STREAMLIT CLOUD COMPATIBLE VERSION
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
# OPTIONAL .ENV
# ============================================================

try:
    from dotenv import load_dotenv

    load_dotenv()

except Exception:
    pass


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Personal SIRI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# IMPORTANT:
# DO NOT CREATE A SESSION VARIABLE WITH THE SAME
# NAME AS A WIDGET KEY.
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
# CSS
# ONLY CSS IS INSIDE st.markdown
# NO UI HTML
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    html,
    body {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #f5f7fb !important;
    }

    [data-testid="stMain"] {
        background: #f5f7fb !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1220px !important;
        margin: 0 auto !important;
        padding: 12px 18px 8px 18px !important;
    }

    #MainMenu {
        display: none !important;
    }

    footer {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }


    /* =====================================================
       STREAMLIT SPACING
       ===================================================== */

    [data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #d9e0ea !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] h1 {
        color: #2563d8 !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 30px !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.15 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]
    [data-testid="stCaptionContainer"] {
        text-align: center !important;
        color: #7b8797 !important;
        font-size: 11px !important;
        margin: 0 !important;
    }


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    [data-testid="stChatMessage"] {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
        border-radius: 10px !important;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 14px !important;
        line-height: 1.45 !important;
    }


    /* =====================================================
       TEXT INPUT
       ===================================================== */

    [data-testid="stTextInput"] {
        margin: 0 !important;
    }

    [data-testid="stTextInput"] input {
        height: 44px !important;
        min-height: 44px !important;
        border-radius: 10px !important;
        border: 1px solid #d5dce6 !important;
        background: #ffffff !important;
        color: #202633 !important;
        font-size: 14px !important;
        padding-left: 14px !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #2563d8 !important;
        box-shadow:
            0 0 0 2px
            rgba(37, 99, 216, 0.10) !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        height: 42px !important;
        min-height: 42px !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        border: 1px solid #d5dce6 !important;
        background: #ffffff !important;
        color: #26364c !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        border-color: #2563d8 !important;
    }


    /* =====================================================
       SEND BUTTON
       ===================================================== */

    .st-key-send_button button {
        background: #ff4b50 !important;
        border-color: #ff4b50 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .st-key-send_button button:hover {
        background: #e83e45 !important;
        border-color: #e83e45 !important;
    }


    /* =====================================================
       START VOICE
       ===================================================== */

    .st-key-start_voice button {
        background: #2563d8 !important;
        border-color: #2563d8 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .st-key-start_voice button:hover {
        background: #1d4fb0 !important;
        border-color: #1d4fb0 !important;
    }


    /* =====================================================
       STOP LISTENING
       ===================================================== */

    .st-key-stop_voice button {
        background: #dc3545 !important;
        border-color: #dc3545 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }


    /* =====================================================
       STOP SPEAKING
       ===================================================== */

    .st-key-stop_speaking button {
        background: #ef4444 !important;
        border-color: #ef4444 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #dce2ea !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 18px 15px 12px 15px !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: #2563d8 !important;
        text-align: center !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }

    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {
        text-align: center !important;
        color: #8993a1 !important;
        font-size: 10px !important;
    }

    section[data-testid="stSidebar"] h5 {
        color: #697386 !important;
        font-size: 10px !important;
        font-weight: 800 !important;
        letter-spacing: 0.4px !important;
        margin: 12px 0 5px 0 !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        height: 38px !important;
        min-height: 38px !important;
        font-size: 12px !important;
        border-radius: 9px !important;
    }

    section[data-testid="stSidebar"] hr {
        margin: 8px 0 !important;
    }


    /* =====================================================
       AUDIO INPUT
       ===================================================== */

    [data-testid="stAudioInput"] {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 900px) {

        [data-testid="stMainBlockContainer"] {
            padding: 8px 10px 5px 10px !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] h1 {
            font-size: 25px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)


# Streamlit Cloud Secrets
if not GROQ_API_KEY:

    try:

        GROQ_API_KEY = st.secrets[
            "GROQ_API_KEY"
        ]

    except Exception:

        GROQ_API_KEY = ""


client = None


if GROQ_API_KEY:

    try:

        client = Groq(
            api_key=GROQ_API_KEY
        )

    except Exception as e:

        print(
            "Groq initialization error:",
            e
        )

        client = None


MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Personal SIRI, a helpful and friendly AI
voice and chat assistant.

Answer clearly and naturally.

Help with:

Python, Java, SQL, AI, Generative AI,
machine learning, cloud computing, AWS,
Linux, networking, aptitude, interviews,
placements and programming projects.

Keep simple answers concise.

Explain technical questions clearly.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:

        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please add GROQ_API_KEY to "
            "Streamlit Cloud Secrets."
        )

    try:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        for item in st.session_state.messages:

            conversation.append(
                {
                    "role": item["role"],
                    "content": item["content"]
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

        return (
            response
            .choices[0]
            .message
            .content
        )

    except Exception as e:

        return (
            "⚠️ AI connection error.\n\n"
            f"{e}"
        )


# ============================================================
# CHAT MANAGEMENT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    copied_messages = [
        {
            "role": item["role"],
            "content": item["content"]
        }
        for item in st.session_state.messages
    ]

    new_chat = {
        "title": st.session_state.chat_title,
        "messages": copied_messages
    }

    found = False

    for index, chat in enumerate(
        st.session_state.history
    ):

        if (
            chat["title"]
            == st.session_state.chat_title
        ):

            st.session_state.history[index] = (
                new_chat
            )

            found = True

            break

    if not found:

        st.session_state.history.append(
            new_chat
        )


def create_new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


def clear_current_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


def clear_all_history():

    st.session_state.history = []

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


def load_chat(index):

    save_current_chat()

    selected_chat = (
        st.session_state.history[index]
    )

    st.session_state.chat_title = (
        selected_chat["title"]
    )

    st.session_state.messages = [
        {
            "role": item["role"],
            "content": item["content"]
        }
        for item in selected_chat["messages"]
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

    if (
        st.session_state.chat_title
        == "New Chat"
    ):

        title = message[:28]

        if len(message) > 28:

            title = (
                title
                + "..."
            )

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
# BROWSER TEXT-TO-SPEECH
# ============================================================

def browser_speak(
    text,
    gender,
    speed
):

    if not text:
        return

    safe_text = json.dumps(
        str(text)
    )

    if gender == "Girl":

        voice_selection = """
        let preferredVoice =
            voices.find(
                voice =>
                /female|zira|samantha|susan|aria|hazel/i
                .test(voice.name)
            );
        """

    else:

        voice_selection = """
        let preferredVoice =
            voices.find(
                voice =>
                /male|david|mark|george/i
                .test(voice.name)
            );
        """

    st.components.v1.html(
        f"""
        <!DOCTYPE html>

        <html>

        <body>

        <script>

        const text =
            {safe_text};

        function speakText() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(
                    text
                );

            utterance.rate =
                {float(speed)};

            utterance.pitch = 1.0;

            utterance.volume = 1.0;

            const voices =
                window.speechSynthesis.getVoices();

            {voice_selection}

            if (preferredVoice) {{
                utterance.voice =
                    preferredVoice;
            }}

            window.speechSynthesis.speak(
                utterance
            );
        }}

        setTimeout(
            speakText,
            200
        );

        </script>

        </body>

        </html>
        """,
        height=1
    )


# ============================================================
# STOP BROWSER SPEECH
# ============================================================

def stop_browser_speech():

    st.components.v1.html(
        """
        <!DOCTYPE html>

        <html>

        <body>

        <script>

        if (
            window.speechSynthesis
        ) {

            window.speechSynthesis.cancel();

        }

        </script>

        </body>

        </html>
        """,
        height=1
    )


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()


def convert_audio_to_text(
    audio_file
):

    if audio_file is None:

        return ""

    try:

        audio_bytes = (
            audio_file.getvalue()
        )

        if not audio_bytes:

            return ""

        audio_buffer = (
            io.BytesIO(
                audio_bytes
            )
        )

        with sr.AudioFile(
            audio_buffer
        ) as source:

            audio_data = (
                recognizer.record(
                    source
                )
            )

        text = (
            recognizer
            .recognize_google(
                audio_data
            )
        )

        return text.strip()

    except sr.UnknownValueError:

        st.warning(
            "I couldn't understand "
            "your voice. Please try again."
        )

        return ""

    except sr.RequestError:

        st.error(
            "Speech recognition service "
            "is unavailable."
        )

        return ""

    except Exception as e:

        st.error(
            f"Audio processing error: {e}"
        )

        return ""


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


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "➕  New Chat",
        use_container_width=True
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

            if len(title) > 22:

                title = (
                    title[:22]
                    + "..."
                )

            if st.button(
                f"💬  {title}",
                key=f"history_{index}",
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
        use_container_width=True
    ):

        clear_current_chat()

        st.rerun()


    # --------------------------------------------------------
    # VOICE SETTINGS
    # --------------------------------------------------------

    st.markdown(
        "##### 🎙️ VOICE SETTINGS"
    )

    voice_response = st.checkbox(
        "Voice Response",
        value=st.session_state.tts_enabled,
        key="voice_response_checkbox"
    )

    st.session_state.tts_enabled = (
        voice_response
    )


    voice_gender = st.radio(
        "Voice",
        ["Girl", "Boy"],
        index=(
            0
            if st.session_state.voice_gender
            == "Girl"
            else 1
        ),
        key="voice_gender_radio"
    )

    st.session_state.voice_gender = (
        voice_gender
    )


    voice_speed = st.slider(
        "Speech Speed",
        min_value=0.7,
        max_value=1.4,
        value=st.session_state.voice_speed,
        step=0.1,
        key="speech_speed_slider"
    )

    st.session_state.voice_speed = (
        voice_speed
    )


    st.divider()


    # --------------------------------------------------------
    # CLEAR ALL HISTORY
    # --------------------------------------------------------

    if st.button(
        "🗑️  Clear All History",
        use_container_width=True
    ):

        clear_all_history()

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

header = st.container(
    border=True
)

with header:

    st.title(
        "🎙️ Personal SIRI"
    )

    st.caption(
        "Your Personal AI Voice & Chat Assistant"
    )


# ============================================================
# DATE / TIME / STATUS
# ============================================================

date_col, time_col, status_col = st.columns(
    [2, 2, 1]
)

current_time = datetime.now()

with date_col:

    st.caption(
        "📅 "
        + current_time.strftime(
            "%d %b %Y"
        )
    )

with time_col:

    st.caption(
        "🕐 "
        + current_time.strftime(
            "%I:%M:%S %p"
        )
    )

with status_col:

    if st.session_state.listening:

        st.warning(
            "🔴 Listening"
        )

    else:

        st.success(
            "🟢 Ready"
        )


# ============================================================
# CHAT AREA
# ============================================================

chat_area = st.container(
    height=400,
    border=True
)

with chat_area:

    if not st.session_state.messages:

        st.write("")

        st.write("")

        st.write("")

        center_left, center, center_right = (
            st.columns([1, 2, 1])
        )

        with center:

            st.markdown(
                "## 🎙️ How can I help you?"
            )

            st.caption(
                "Type a message below or use 🎙️ Start Voice."
            )

            st.info(
                "Your intelligent Personal SIRI "
                "assistant is ready."
            )

    else:

        for message in (
            st.session_state.messages
        ):

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
    [6.5, 1],
    gap="small"
)

with input_col:

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

        process_message(
            user_message
        )

        st.rerun()


# ============================================================
# VOICE CONTROL
# ============================================================

voice_left, voice_center, voice_right = (
    st.columns([1, 2, 1])
)

with voice_center:

    if not st.session_state.listening:

        start_clicked = st.button(
            "🎙️ Start Voice",
            key="start_voice",
            use_container_width=True
        )

        if start_clicked:

            st.session_state.listening = True

            st.rerun()

    else:

        stop_clicked = st.button(
            "⏹️ Stop Listening",
            key="stop_voice",
            use_container_width=True
        )

        if stop_clicked:

            st.session_state.listening = False

            st.rerun()


# ============================================================
# BROWSER MICROPHONE
# ============================================================

if st.session_state.listening:

    st.info(
        "🎙️ Click the microphone button below "
        "and speak."
    )

    audio_value = st.audio_input(
        "Record your message",
        key="microphone_input"
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
# AI SPEECH
# ============================================================

if st.session_state.speak_text:

    text_to_speak = (
        st.session_state.speak_text
    )

    # Clear BEFORE rendering speech
    # so it doesn't repeatedly speak
    st.session_state.speak_text = ""

    browser_speak(
        text_to_speak,
        st.session_state.voice_gender,
        st.session_state.voice_speed
    )


# ============================================================
# STOP AI SPEAKING
# IMPORTANT:
# THERE IS NO st.session_state.stop_speaking
# ============================================================

stop_col1, stop_col2, stop_col3 = (
    st.columns([1, 2, 1])
)

with stop_col2:

    if st.button(
        "⏹️ Stop AI Speaking",
        key="stop_speaking",
        use_container_width=True
    ):

        stop_browser_speech()

        st.session_state.speak_text = ""

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "🎙️ Personal SIRI • AI Voice & Chat Assistant"
)