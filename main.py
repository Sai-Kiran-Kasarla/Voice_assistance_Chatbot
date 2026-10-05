# ============================================================
# PERSONAL SIRI - STATIC CHAT UI
# ============================================================

import os
import threading
from datetime import datetime

import streamlit as st
import speech_recognition as sr
import pyttsx3
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
# ============================================================

defaults = {
    "messages": [],
    "history": [],
    "chat_title": "New Chat",
    "tts_enabled": True,
    "voice_gender": "Girl",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
#
# IMPORTANT:
# This is ONLY CSS.
# There is NO visible HTML interface below.
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html,
    body {
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
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
        background: #f5f7fb !important;
    }

    [data-testid="stMainBlockContainer"] {
        box-sizing: border-box !important;
        max-width: 1220px !important;
        height: calc(100vh - 50px) !important;

        margin: 0 auto !important;

        padding:
            8px 18px 4px 18px !important;

        overflow: hidden !important;
    }

    /* Hide only Streamlit branding */
    #MainMenu {
        display: none !important;
    }

    footer {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }


    /* ======================================================
       COMPACT STREAMLIT SPACING
       ====================================================== */

    [data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
    }


    /* ======================================================
       MAIN TITLE
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #d9e0ea !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }

    .main-title-container h1 {
        color: #2563d8 !important;
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 31px !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.1 !important;
    }


    /* ======================================================
       TITLE / HEADER NATIVE CONTAINER
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"]
    h1 {
        color: #2563d8 !important;
        font-size: 30px !important;
        font-weight: 800 !important;
        text-align: center !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]
    [data-testid="stCaptionContainer"] {
        text-align: center !important;
        color: #7b8797 !important;
        font-size: 11px !important;
        margin: 0 !important;
    }


    /* ======================================================
       STATUS TEXT
       ====================================================== */

    .status-text {
        font-size: 12px !important;
        color: #687386 !important;
    }


    /* ======================================================
       CHAT CONTAINER
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        box-sizing: border-box !important;
    }


    /* ======================================================
       CHAT MESSAGES
       ====================================================== */

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


    /* ======================================================
       WELCOME SCREEN
       ====================================================== */

    .welcome-native {
        text-align: center !important;
        padding-top: 60px !important;
    }

    .welcome-native h2 {
        color: #292e3b !important;
        font-size: 34px !important;
        font-weight: 800 !important;
        margin: 8px 0 5px 0 !important;
    }

    .welcome-native p {
        color: #4d5b70 !important;
        font-size: 14px !important;
    }


    /* ======================================================
       INPUT
       ====================================================== */

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


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        height: 44px !important;
        min-height: 44px !important;

        border-radius: 10px !important;

        font-size: 13px !important;

        font-weight: 600 !important;

        border: 1px solid #d5dce6 !important;

        background: #ffffff !important;

        color: #26364c !important;

        box-shadow: none !important;

        transition: none !important;
    }

    .stButton > button:hover {
        transform: none !important;
    }


    /* ======================================================
       SEND BUTTON
       ====================================================== */

    .st-key-send_button button {
        background: #ff4b50 !important;

        border-color: #ff4b50 !important;

        color: #ffffff !important;

        font-weight: 700 !important;
    }

    .st-key-send_button button:hover {
        background: #e83e45 !important;

        border-color: #e83e45 !important;

        color: #ffffff !important;
    }


    /* ======================================================
       START VOICE
       ====================================================== */

    .st-key-start_voice button {
        background: #2563d8 !important;

        border-color: #2563d8 !important;

        color: #ffffff !important;

        font-weight: 700 !important;
    }

    .st-key-start_voice button:hover {
        background: #1d4fb0 !important;

        border-color: #1d4fb0 !important;

        color: #ffffff !important;
    }


    /* ======================================================
       STOP LISTENING
       ====================================================== */

    .st-key-stop_voice button {
        background: #dc3545 !important;

        border-color: #dc3545 !important;

        color: #ffffff !important;

        font-weight: 700 !important;
    }


    /* ======================================================
       STOP SPEAKING
       ====================================================== */

    .st-key-stop_speaking button {
        background: #ef4444 !important;

        border-color: #ef4444 !important;

        color: #ffffff !important;

        font-weight: 700 !important;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff !important;

        border-right:
            1px solid #dce2ea !important;
    }

    section[data-testid="stSidebar"]
    .block-container {
        padding:
            18px 15px 12px 15px !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: #2563d8 !important;

        text-align: center !important;

        font-size: 20px !important;

        font-weight: 800 !important;

        margin:
            0 0 0 0 !important;
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

        margin:
            12px 0 5px 0 !important;
    }

    section[data-testid="stSidebar"]
    .stButton > button {
        height: 38px !important;

        min-height: 38px !important;

        font-size: 12px !important;

        border-radius: 9px !important;
    }

    section[data-testid="stSidebar"] hr {
        margin:
            8px 0 !important;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer-native {
        text-align: center !important;

        color: #9aa3af !important;

        font-size: 9px !important;

        line-height: 15px !important;
    }


    /* ======================================================
       SMALL SCREEN
       ====================================================== */

    @media (max-width: 900px) {

        [data-testid="stMainBlockContainer"] {
            padding:
                6px 10px 3px 10px !important;
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
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)

client = None

if GROQ_API_KEY:
    try:
        client = Groq(
            api_key=GROQ_API_KEY
        )
    except Exception as e:
        print("Groq error:", e)


MODEL_NAME = "openai/gpt-oss-20b"


SYSTEM_PROMPT = """
You are Personal SIRI, a helpful and friendly AI voice
and chat assistant.

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
# TEXT TO SPEECH
# ============================================================

class TTSManager:

    def __init__(self):

        self.engine = None

        self.thread = None

        self.lock = threading.Lock()

        self.speaking = False


    def find_voice(
        self,
        engine,
        gender
    ):

        try:
            voices = engine.getProperty(
                "voices"
            )
        except Exception:
            return None

        if not voices:
            return None

        if gender == "Girl":
            keywords = [
                "female",
                "zira",
                "hazel",
                "samantha",
                "susan",
                "aria"
            ]
        else:
            keywords = [
                "male",
                "david",
                "mark",
                "george"
            ]

        for voice in voices:

            name = str(
                getattr(
                    voice,
                    "name",
                    ""
                )
            ).lower()

            voice_id = str(
                getattr(
                    voice,
                    "id",
                    ""
                )
            ).lower()

            combined = (
                name + " " + voice_id
            )

            for keyword in keywords:

                if keyword in combined:
                    return voice.id

        return voices[0].id


    def worker(
        self,
        text,
        gender
    ):

        engine = None

        try:

            engine = pyttsx3.init()

            with self.lock:
                self.engine = engine

            voice_id = self.find_voice(
                engine,
                gender
            )

            if voice_id:
                engine.setProperty(
                    "voice",
                    voice_id
                )

            engine.setProperty(
                "rate",
                170
            )

            engine.setProperty(
                "volume",
                1.0
            )

            self.speaking = True

            engine.say(text)

            engine.runAndWait()

        except Exception as e:

            print(
                "TTS Error:",
                e
            )

        finally:

            try:
                if engine:
                    engine.stop()
            except Exception:
                pass

            with self.lock:
                self.engine = None

            self.speaking = False


    def speak(
        self,
        text,
        gender
    ):

        self.stop()

        self.thread = threading.Thread(
            target=self.worker,
            args=(
                text,
                gender
            ),
            daemon=True
        )

        self.thread.start()


    def stop(self):

        with self.lock:
            engine = self.engine

        if engine:

            try:
                engine.stop()
            except Exception:
                pass

        self.speaking = False


tts_manager = TTSManager()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

class VoiceManager:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.microphone = None

        self.stop_listening = None

        self.active = False

        self.result = ""

        self.error = ""


    def callback(
        self,
        recognizer,
        audio
    ):

        try:

            text = recognizer.recognize_google(
                audio
            )

            if text:
                self.result = text

        except sr.UnknownValueError:
            pass

        except sr.RequestError:
            self.error = (
                "Speech recognition service "
                "is unavailable."
            )

        except Exception as e:
            self.error = str(e)


    def start(self):

        if self.active:
            return True

        try:

            self.result = ""

            self.error = ""

            self.microphone = sr.Microphone()

            with self.microphone as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

            self.stop_listening = (
                self.recognizer.listen_in_background(
                    self.microphone,
                    self.callback
                )
            )

            self.active = True

            return True

        except Exception as e:

            self.error = str(e)

            self.active = False

            return False


    def stop(self):

        if self.stop_listening:

            try:

                self.stop_listening(
                    wait_for_stop=False
                )

            except Exception:
                pass

        self.stop_listening = None

        self.active = False


voice_manager = VoiceManager()


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(
    user_message
):

    if client is None:

        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please check your `.env` file."
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

        return response.choices[0].message.content

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

    copied = [
        {
            "role": item["role"],
            "content": item["content"]
        }
        for item in st.session_state.messages
    ]

    new_chat = {
        "title": st.session_state.chat_title,
        "messages": copied
    }

    found = False

    for i, chat in enumerate(
        st.session_state.history
    ):

        if (
            chat["title"]
            == st.session_state.chat_title
        ):

            st.session_state.history[i] = new_chat

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


def clear_current_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"


def clear_all_history():

    st.session_state.history = []

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"


def load_chat(index):

    save_current_chat()

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


def process_message(
    message
):

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

        tts_manager.speak(
            answer,
            st.session_state.voice_gender
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

        create_new_chat()

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

            if len(title) > 22:
                title = title[:22] + "..."

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


    # CURRENT CHAT

    st.markdown(
        "##### 💬 CURRENT CHAT"
    )

    if st.button(
        "🗑️  Clear Current Chat",
        use_container_width=True
    ):

        clear_current_chat()

        st.rerun()


    # VOICE SETTINGS

    st.markdown(
        "##### 🎙️ VOICE SETTINGS"
    )

    voice_enabled = st.checkbox(
        "Voice Response",
        value=st.session_state.tts_enabled,
        key="tts_widget"
    )

    st.session_state.tts_enabled = (
        voice_enabled
    )


    selected_gender = st.radio(
        "Voice",
        ["Girl", "Boy"],
        index=(
            0
            if st.session_state.voice_gender
            == "Girl"
            else 1
        ),
        key="gender_widget"
    )

    st.session_state.voice_gender = (
        selected_gender
    )


    st.divider()


    # CLEAR HISTORY

    if st.button(
        "🗑️  Clear All History",
        use_container_width=True
    ):

        clear_all_history()

        st.rerun()


# ============================================================
# MAIN TITLE
# NATIVE STREAMLIT ONLY
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
# DATE / TIME / READY
# ============================================================

date_col, time_col, ready_col = st.columns(
    [2, 2, 1]
)

now = datetime.now()

with date_col:

    st.caption(
        f"📅 {now.strftime('%d %b %Y')}"
    )

with time_col:

    st.caption(
        f"🕐 {now.strftime('%I:%M:%S %p')}"
    )

with ready_col:

    st.success(
        "Ready",
        icon="🟢"
    )


# ============================================================
# CHAT AREA
#
# ONLY THIS CONTAINER SCROLLS.
# ============================================================

chat_area = st.container(
    height=370,
    border=True
)

with chat_area:

    if not st.session_state.messages:

        st.write("")

        st.write("")

        st.markdown(
            "## 🎙️ How can I help you?"
        )

        st.caption(
            "Type a message below or use 🎙️ Start Voice."
        )

        st.write("")

        st.info(
            "Your intelligent Personal SIRI assistant is ready."
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

left, center, right = st.columns(
    [1, 2, 1]
)

with center:

    if not voice_manager.active:

        start_clicked = st.button(
            "🎙️ Start Voice",
            key="start_voice",
            use_container_width=True
        )

        if start_clicked:

            if voice_manager.start():

                st.rerun()

            else:

                st.error(
                    "Microphone could not be accessed."
                )

    else:

        stop_clicked = st.button(
            "⏹️ Stop Listening",
            key="stop_voice",
            use_container_width=True
        )

        if stop_clicked:

            voice_manager.stop()

            st.rerun()


# ============================================================
# VOICE RESULT
# ============================================================

if voice_manager.result:

    recognized = (
        voice_manager.result.strip()
    )

    voice_manager.result = ""

    voice_manager.stop()

    if recognized:

        process_message(
            recognized
        )

        st.rerun()


# ============================================================
# VOICE ERROR
# ============================================================

if voice_manager.error:

    st.warning(
        voice_manager.error
    )

    voice_manager.error = ""


# ============================================================
# STOP AI SPEAKING
# ============================================================

if tts_manager.speaking:

    a, b, c = st.columns(
        [1, 2, 1]
    )

    with b:

        stop_speech = st.button(
            "⏹️ Stop AI Speaking",
            key="stop_speaking",
            use_container_width=True
        )

        if stop_speech:

            tts_manager.stop()

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "🎙️ Personal SIRI • AI Voice & Chat Assistant"
)