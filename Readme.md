# ============================================================
# PERSONAL SIRI - VOICE / CHAT ASSISTANT
# ============================================================

import os
import time

import streamlit as st
import pyttsx3
import speech_recognition as sr

from groq import Groq
from dotenv import load_dotenv


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Personal SIRI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY in your .env file.")
    st.stop()


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

@st.cache_resource
def get_recognizer():
    return sr.Recognizer()


recognizer = get_recognizer()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": (
                "You are Personal SIRI, a helpful personal AI "
                "voice and chat assistant. Give clear, natural "
                "and useful answers."
            )
        }
    ]


if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"


if "listening_time" not in st.session_state:
    st.session_state.listening_time = 0.0


if "is_listening" not in st.session_state:
    st.session_state.is_listening = False


if "stop_listening" not in st.session_state:
    st.session_state.stop_listening = False


# ============================================================
# VOICE DEFAULTS
# ============================================================
# These are intentionally NOT displayed in the sidebar.
# They keep the voice system working.

if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True


if "voice_gender" not in st.session_state:
    st.session_state.voice_gender = "girl"


tts_enabled = st.session_state.tts_enabled
voice_gender = st.session_state.voice_gender


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       REMOVE DEFAULT STREAMLIT ELEMENTS
       ====================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ======================================================
       FULL APP
       ====================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }


    [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }


    [data-testid="stMain"] {
        overflow: hidden !important;
    }


    .main {
        overflow: hidden !important;
    }


    .block-container {
        height: 100vh !important;
        max-height: 100vh !important;

        padding-top: 8px !important;
        padding-bottom: 0 !important;
        padding-left: 24px !important;
        padding-right: 24px !important;

        overflow: hidden !important;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }


    [data-testid="stSidebar"] > div:first-child {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow-y: auto !important;
    }


    [data-testid="stSidebar"] .block-container {
        padding: 20px 16px !important;
        height: 100vh !important;
        overflow-y: auto !important;
    }


    /* ======================================================
       SIDEBAR CHAT ITEMS
       ====================================================== */

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        padding: 5px 4px !important;
    }


    /* ======================================================
       PERSONAL SIRI TITLE
       ====================================================== */

    .siri-title {
        text-align: center;
        font-size: 38px;
        font-weight: 700;
        color: #202124;
        margin-top: 8px;
        margin-bottom: 2px;
    }


    .siri-subtitle {
        text-align: center;
        font-size: 15px;
        color: #777777;
        margin-bottom: 8px;
    }


    /* ======================================================
       BANNER
       ====================================================== */

    .st-key-banner_area {
        border-radius: 20px !important;

        border: 1px solid #e5eaf2 !important;

        background: linear-gradient(
            135deg,
            #f7faff,
            #eef5ff,
            #fbfdff
        ) !important;

        padding: 22px 25px !important;

        margin-bottom: 8px !important;

        box-shadow:
            0 4px 18px rgba(0, 0, 0, 0.04) !important;
    }


    /* ======================================================
       HOME AREA
       ====================================================== */

    .st-key-home_area {
        height: calc(100vh - 265px) !important;
        max-height: calc(100vh - 265px) !important;

        display: flex !important;

        align-items: center !important;
        justify-content: center !important;

        overflow: hidden !important;
    }


    /* ======================================================
       CHAT AREA
       ====================================================== */

    .st-key-chat_scroll {
        height: calc(100vh - 335px) !important;
        max-height: calc(100vh - 335px) !important;

        overflow-y: auto !important;
        overflow-x: hidden !important;

        padding: 8px 18px 20px 18px !important;

        border: none !important;
    }


    /* ======================================================
       CHAT MESSAGES
       ====================================================== */

    [data-testid="stChatMessage"] {
        padding-top: 8px !important;
        padding-bottom: 8px !important;
    }


    /* ======================================================
       TEXT INPUT
       ====================================================== */

    [data-testid="stTextInput"] input {
        border-radius: 25px !important;

        min-height: 48px !important;

        border: 1px solid #dcdcdc !important;

        padding-left: 18px !important;

        font-size: 15px !important;

        background: white !important;
    }


    [data-testid="stTextInput"] input:focus {
        border-color: #7aa7ff !important;
        box-shadow: 0 0 0 1px #7aa7ff !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        min-height: 42px !important;

        border-radius: 10px !important;

        font-weight: 500 !important;
    }


    .stButton > button:hover {
        transform: translateY(-1px);
    }


    /* ======================================================
       INFO BOX
       ====================================================== */

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }


    /* ======================================================
       SCROLLBAR
       ====================================================== */

    ::-webkit-scrollbar {
        width: 7px;
    }


    ::-webkit-scrollbar-track {
        background: transparent;
    }


    ::-webkit-scrollbar-thumb {
        background: #c9c9c9;
        border-radius: 10px;
    }


    ::-webkit-scrollbar-thumb:hover {
        background: #aaaaaa;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer-text {
        text-align: center;
        color: #999999;
        font-size: 10px;
        margin-top: 3px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TEXT TO SPEECH ENGINE
# ============================================================

@st.cache_resource
def get_tts_engine():
    try:
        return pyttsx3.init()

    except Exception:
        return None


# ============================================================
# SPEAK
# ============================================================

def speak(text, voice_gender):

    try:

        engine = get_tts_engine()

        if engine is None:
            return


        voices = engine.getProperty("voices")

        selected_voice = None


        # ====================================================
        # GIRL VOICE
        # ====================================================

        if voice_gender == "girl":

            for voice in voices:

                name = voice.name.lower()

                if (
                    "female" in name
                    or "zira" in name
                    or "hazel" in name
                    or "susan" in name
                ):

                    selected_voice = voice
                    break


        # ====================================================
        # BOY VOICE
        # ====================================================

        else:

            for voice in voices:

                name = voice.name.lower()

                if (
                    "male" in name
                    or "david" in name
                    or "mark" in name
                ):

                    selected_voice = voice
                    break


        if selected_voice:

            engine.setProperty(
                "voice",
                selected_voice.id
            )


        engine.setProperty(
            "rate",
            150
        )


        engine.setProperty(
            "volume",
            0.8
        )


        engine.say(text)

        engine.runAndWait()

        engine.stop()


    except Exception:
        pass


# ============================================================
# SPEECH TO TEXT
# ============================================================

def listen_to_speech():

    start_time = time.time()

    st.session_state.is_listening = True

    st.session_state.stop_listening = False


    try:

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )


            audio = recognizer.listen(
                source,
                phrase_time_limit=10
            )


        elapsed = time.time() - start_time

        st.session_state.listening_time = elapsed

        st.session_state.is_listening = False


        text = recognizer.recognize_google(
            audio
        )


        return text.lower()


    except sr.UnknownValueError:

        st.session_state.listening_time = (
            time.time() - start_time
        )

        st.session_state.is_listening = False

        st.warning(
            "Sorry, I could not understand your voice."
        )

        return None


    except sr.RequestError:

        st.session_state.listening_time = (
            time.time() - start_time
        )

        st.session_state.is_listening = False

        st.error(
            "Speech recognition service is unavailable."
        )

        return None


    except Exception as e:

        st.session_state.listening_time = (
            time.time() - start_time
        )

        st.session_state.is_listening = False

        st.error(
            f"Microphone error: {e}"
        )

        return None


# ============================================================
# GENERATE AI RESPONSE
# ============================================================

def gen_ai_response():

    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=st.session_state.chat_history,

            temperature=0.7
        )


        result = (
            response
            .choices[0]
            .message
            .content
        )


        if result:
            return result.strip()


        return "Sorry, I could not generate a response."


    except Exception as e:

        return f"Error getting AI response: {e}"


# ============================================================
# PROCESS MESSAGE
# ============================================================

def process_message(
    user_text,
    tts_enabled,
    voice_gender
):

    if not user_text:
        return


    user_text = user_text.strip()


    if not user_text:
        return


    # ========================================================
    # USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_text
        }
    )


    # ========================================================
    # CHAT TITLE
    # ========================================================

    if st.session_state.chat_title == "New Chat":

        title = user_text

        if len(title) > 40:
            title = title[:40] + "..."

        st.session_state.chat_title = title


    # ========================================================
    # AI RESPONSE
    # ========================================================

    with st.spinner(
        "Personal SIRI is thinking..."
    ):

        ai_response = gen_ai_response()


    # ========================================================
    # ASSISTANT MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )


    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )


    # ========================================================
    # TEXT TO SPEECH
    # ========================================================

    if tts_enabled:

        speak(
            ai_response,
            voice_gender
        )


# ============================================================
# CLEAR CHAT
# ============================================================

def clear_chat():

    st.session_state.messages = []


    st.session_state.chat_history = [
        {
            "role": "system",
            "content": (
                "You are Personal SIRI, a helpful personal AI "
                "voice and chat assistant. Give clear, natural "
                "and useful answers."
            )
        }
    ]


    st.session_state.chat_title = "New Chat"

    st.session_state.listening_time = 0.0

    st.session_state.is_listening = False

    st.session_state.stop_listening = False


# ============================================================
# DYNAMIC SIDEBAR
# ============================================================
#
# IMPORTANT:
#
# Nothing static is placed here.
#
# No:
#   Personal SIRI
#   Search
#   Recents
#   History
#   Voice
#   Girl
#   Boy
#
# Only actual conversations are displayed.
# ============================================================

with st.sidebar:

    recent_messages = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]


    if recent_messages:

        for message in reversed(
            recent_messages
        ):

            display = message.strip()


            if len(display) > 48:

                display = (
                    display[:48]
                    + "..."
                )


            st.caption(
                f"💬 {display}"
            )


        st.divider()


        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True
        ):

            clear_chat()

            st.rerun()


# ============================================================
# PERSONAL SIRI BANNER
# ============================================================

banner_area = st.container(
    key="banner_area"
)


with banner_area:

    banner_left, banner_center, banner_right = st.columns(
        [1, 5, 1]
    )


    with banner_center:

        st.markdown(
            '<div class="siri-title">'
            '🎙️ Personal SIRI'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div class="siri-subtitle">'
            'Your Personal AI Voice & Chat Assistant'
            '</div>',
            unsafe_allow_html=True
        )


    with banner_right:

        st.write("")

        st.caption(
            "🎙️ Voice + Chat"
        )


# ============================================================
# HOME PAGE
# ============================================================

if not st.session_state.messages:

    home_area = st.container(
        key="home_area"
    )


    with home_area:

        st.write("")


        empty1, center, empty2 = st.columns(
            [1, 3, 1]
        )


        with center:

            st.markdown(
                "### What's on the agenda today?"
            )


            st.caption(
                "Ask Personal SIRI anything or start a voice conversation."
            )


            st.write("")


            # =================================================
            # MESSAGE INPUT
            # =================================================

            home_text = st.text_input(

                "Message Personal SIRI",

                placeholder=(
                    "💬 Message Personal SIRI..."
                ),

                label_visibility="collapsed",

                key="home_message"
            )


            # =================================================
            # SEND BUTTON
            # =================================================

            send_col1, send_col2, send_col3 = st.columns(
                [1, 2, 1]
            )


            with send_col2:

                if st.button(

                    "➤ SEND",

                    type="primary",

                    use_container_width=True
                ):

                    if home_text.strip():

                        process_message(

                            home_text,

                            tts_enabled,

                            voice_gender
                        )

                        st.rerun()


            st.write("")


            # =================================================
            # VOICE BUTTON
            # =================================================

            mic_col1, mic_col2, mic_col3 = st.columns(
                [1, 2, 1]
            )


            with mic_col2:

                if st.button(
                    "🎙️ START VOICE",
                    use_container_width=True
                ):

                    st.session_state.is_listening = True

                    st.session_state.stop_listening = False

                    st.rerun()


                # =============================================
                # LISTENING MODE
                # =============================================

                if st.session_state.is_listening:

                    st.info(
                        "🎙️ Listening... Speak now"
                    )


                    if st.button(
                        "⛔ STOP",
                        use_container_width=True
                    ):

                        st.session_state.is_listening = False

                        st.session_state.stop_listening = True

                        st.rerun()


                    if not st.session_state.stop_listening:

                        voice_text = listen_to_speech()


                        if voice_text:

                            process_message(

                                voice_text,

                                tts_enabled,

                                voice_gender
                            )


                            st.session_state.is_listening = False

                            st.rerun()


            # =================================================
            # LISTENING TIME
            # =================================================

            if st.session_state.listening_time > 0:

                st.caption(
                    "🎧 Last listening time: "
                    f"{st.session_state.listening_time:.1f} seconds"
                )


# ============================================================
# CHAT PAGE
# ============================================================

else:

    st.subheader(
        st.session_state.chat_title
    )


    # ========================================================
    # CHAT SCROLL AREA
    # ========================================================

    chat_scroll = st.container(
        key="chat_scroll"
    )


    with chat_scroll:

        for message in st.session_state.messages:

            if message["role"] == "user":

                with st.chat_message(
                    "user",
                    avatar="👤"
                ):

                    st.caption(
                        "You"
                    )

                    st.write(
                        message["content"]
                    )


            else:

                with st.chat_message(
                    "assistant",
                    avatar="🎙️"
                ):

                    st.caption(
                        "Personal SIRI"
                    )

                    st.write(
                        message["content"]
                    )


    # ========================================================
    # BOTTOM INPUT
    # ========================================================

    st.divider()


    input_col, send_col = st.columns(
        [5, 1]
    )


    with input_col:

        chat_text = st.text_input(

            "Message Personal SIRI",

            placeholder=(
                "💬 Message Personal SIRI..."
            ),

            label_visibility="collapsed",

            key="chat_message"
        )


    with send_col:

        send_clicked = st.button(

            "➤ SEND",

            type="primary",

            use_container_width=True
        )


    if send_clicked:

        if chat_text.strip():

            process_message(

                chat_text,

                tts_enabled,

                voice_gender
            )

            st.rerun()


    # ========================================================
    # MICROPHONE
    # ========================================================

    mic1, mic2, mic3 = st.columns(
        [1, 2, 1]
    )


    with mic2:

        if st.button(
            "🎙️ MIC • START VOICE",
            use_container_width=True
        ):

            st.session_state.is_listening = True

            st.session_state.stop_listening = False

            st.rerun()


        if st.session_state.is_listening:

            st.info(
                "🎙️ Listening... Speak now"
            )


            if st.button(
                "⛔ STOP LISTENING",
                use_container_width=True
            ):

                st.session_state.is_listening = False

                st.session_state.stop_listening = True

                st.rerun()


            if not st.session_state.stop_listening:

                voice_text = listen_to_speech()


                if voice_text:

                    process_message(

                        voice_text,

                        tts_enabled,

                        voice_gender
                    )


                    st.session_state.is_listening = False

                    st.rerun()


    # ========================================================
    # LISTENING TIME
    # ========================================================

    if st.session_state.listening_time > 0:

        st.caption(
            "🎧 Last listening time: "
            f"{st.session_state.listening_time:.1f} seconds"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-text">'
    '🎙️ Personal SIRI • Voice & Chat Assistant • '
    'Copyright © Sai Kiran'
    '</div>',
    unsafe_allow_html=True
)