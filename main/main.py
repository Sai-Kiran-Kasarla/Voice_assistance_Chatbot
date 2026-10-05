# ============================================================
# PERSONAL SIRI - STREAMLIT CLOUD VERSION
# AI CHAT + BROWSER VOICE INPUT + BROWSER VOICE OUTPUT
# ============================================================

import os
import html
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
# ============================================================

defaults = {
    "messages": [],
    "history": [],
    "chat_title": "New Chat",
    "tts_enabled": True,
    "voice_gender": "Girl",
    "voice_speed": 1.0,
    "listening": False,
    "speech_text": "",
    "last_audio_id": None,
    "last_spoken_message": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
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
        height: 100% !important;
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
        padding: 8px 18px 8px 18px !important;
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
       SPACING
       ===================================================== */

    [data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {
        text-align: center;
        padding: 4px 0 2px 0;
    }

    .main-title h1 {
        color: #2563d8;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 31px;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
    }

    .main-title p {
        color: #7b8797;
        font-size: 11px;
        margin: 3px 0 0 0;
    }


    /* =====================================================
       STATUS
       ===================================================== */

    .status-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 22px;
        color: #687386;
        font-size: 11px;
        margin: 2px 0 5px 0;
    }

    .ready {
        color: #15803d;
        font-weight: 700;
    }

    .listening {
        color: #dc2626;
        font-weight: 700;
    }


    /* =====================================================
       CHAT
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
       WELCOME
       ===================================================== */

    .welcome-box {
        text-align: center;
        padding: 55px 20px 35px 20px;
    }

    .welcome-box .icon {
        font-size: 42px;
        margin-bottom: 4px;
    }

    .welcome-box h2 {
        color: #292e3b;
        font-size: 30px;
        font-weight: 800;
        margin: 4px 0;
    }

    .welcome-box p {
        color: #64748b;
        font-size: 13px;
        margin: 5px 0;
    }


    /* =====================================================
       INPUT
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
        box-shadow: 0 0 0 2px rgba(37, 99, 216, 0.10) !important;
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
       SEND
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
       VOICE
       ===================================================== */

    .st-key-start_voice button {
        background: #2563d8 !important;
        border-color: #2563d8 !important;
        color: white !important;
        font-weight: 700 !important;
    }

    .st-key-stop_voice button {
        background: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important;
        font-weight: 700 !important;
    }

    .st-key-stop_speaking button {
        background: #ef4444 !important;
        border-color: #ef4444 !important;
        color: white !important;
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

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
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
       FOOTER
       ===================================================== */

    .footer-native {
        text-align: center;
        color: #9aa3af;
        font-size: 9px;
        line-height: 15px;
        padding: 4px;
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
            padding: 6px 10px 5px 10px !important;
        }

        .main-title h1 {
            font-size: 25px;
        }

        .welcome-box {
            padding-top: 35px;
        }

        .welcome-box h2 {
            font-size: 25px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Streamlit Cloud Secrets support
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        GROQ_API_KEY = ""

client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        client = None


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
# BROWSER TEXT TO SPEECH
# ============================================================

def speak_in_browser(text, gender="Girl", speed=1.0):
    """
    Uses the user's browser speech engine.

    This does NOT require pyttsx3.
    """

    if not text:
        return

    safe_text = html.escape(str(text))

    if gender == "Girl":
        voice_hint = """
        voices.find(v =>
            /female|zira|samantha|susan|aria|hazel/i.test(v.name)
        )
        """
    else:
        voice_hint = """
        voices.find(v =>
            /male|david|mark|george/i.test(v.name)
        )
        """

    components = st.components.v1

    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    overflow: hidden;
                    height: 1px;
                }}
            </style>
        </head>

        <body>

        <script>

        const text = `{safe_text}`;

        function speakNow() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.rate = {speed};
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            const voices =
                window.speechSynthesis.getVoices();

            let selectedVoice = {voice_hint};

            if (selectedVoice) {{
                utterance.voice = selectedVoice;
            }}

            window.speechSynthesis.speak(utterance);
        }}

        if (
            window.speechSynthesis.getVoices().length
        ) {{
            speakNow();
        }}
        else {{
            window.speechSynthesis.onvoiceschanged =
                function() {{
                    speakNow();
                }};
        }}

        </script>

        </body>
        </html>
        """,
        height=1,
    )


def stop_browser_speech():
    """
    Browser speech is controlled by the browser.
    A new browser component can cancel speech.
    """

    st.components.v1.html(
        """
        <script>
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        </script>
        """,
        height=1,
    )


# ============================================================
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()


def audio_to_text(audio_file):
    """
    Convert Streamlit browser microphone audio
    to text using Google Speech Recognition.
    """

    if audio_file is None:
        return ""

    try:

        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return ""

        import io

        audio_stream = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_stream) as source:

            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(
            audio_data
        )

        return text.strip()

    except sr.UnknownValueError:

        return ""

    except sr.RequestError:

        st.error(
            "Speech recognition service is unavailable."
        )

        return ""

    except Exception as e:

        st.error(
            f"Could not process microphone audio: {e}"
        )

        return ""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:

        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please add GROQ_API_KEY to Streamlit Secrets."
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
            max_tokens=1200,
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

    st.session_state.speech_text = ""

    st.session_state.last_audio_id = None


def clear_current_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speech_text = ""

    st.session_state.last_audio_id = None


def clear_all_history():

    st.session_state.history = []

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speech_text = ""

    st.session_state.last_audio_id = None


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

    st.session_state.last_spoken_message = answer


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


    voice_speed = st.slider(
        "Speech Speed",
        min_value=0.7,
        max_value=1.4,
        value=float(
            st.session_state.voice_speed
        ),
        step=0.1
    )

    st.session_state.voice_speed = voice_speed


    st.divider()


    # --------------------------------------------------------
    # CLEAR HISTORY
    # --------------------------------------------------------

    if st.button(
        "🗑️  Clear All History",
        use_container_width=True
    ):

        clear_all_history()

        st.rerun()


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    """
    <div class="main-title">
        <h1>🎙️ Personal SIRI</h1>
        <p>Your Personal AI Voice & Chat Assistant</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATE / TIME / STATUS
# ============================================================

now = datetime.now()

status_class = (
    "listening"
    if st.session_state.listening
    else "ready"
)

status_text = (
    "🔴 Listening"
    if st.session_state.listening
    else "🟢 Ready"
)

st.markdown(
    f"""
    <div class="status-row">

        <span>
            📅 {now.strftime('%d %b %Y')}
        </span>

        <span>
            🕐 {now.strftime('%I:%M:%S %p')}
        </span>

        <span class="{status_class}">
            {status_text}
        </span>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHAT AREA
# ============================================================

chat_area = st.container(
    height=390,
    border=True
)

with chat_area:

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="welcome-box">

                <div class="icon">🎙️</div>

                <h2>
                    How can I help you?
                </h2>

                <p>
                    Type a message below or use
                    the microphone.
                </p>

                <p>
                    Your intelligent Personal SIRI
                    assistant is ready.
                </p>

            </div>
            """,
            unsafe_allow_html=True
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
# TEXT INPUT
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
# SEND TEXT MESSAGE
# ============================================================

if send_clicked:

    if user_message.strip():

        process_message(
            user_message
        )

        st.rerun()


# ============================================================
# VOICE SECTION
# ============================================================

st.markdown("")


voice_left, voice_center, voice_right = st.columns(
    [1, 2, 1]
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
        "🎙️ Click the microphone below and speak. "
        "When recording is finished, the audio will be "
        "converted to text."
    )

    audio_value = st.audio_input(
        "Record your message",
        key="browser_microphone"
    )

    if audio_value is not None:

        # Create a simple identifier for this recording
        audio_id = str(
            hash(
                audio_value.getvalue()
            )
        )

        if (
            audio_id
            != st.session_state.last_audio_id
        ):

            st.session_state.last_audio_id = audio_id

            recognized = audio_to_text(
                audio_value
            )

            st.session_state.listening = False

            if recognized:

                st.session_state.speech_text = (
                    recognized
                )

                process_message(
                    recognized
                )

                st.rerun()

            else:

                st.warning(
                    "I couldn't understand the audio. "
                    "Please try again."
                )

                st.rerun()


# ============================================================
# RECOGNIZED TEXT
# ============================================================

if st.session_state.speech_text:

    st.caption(
        f"🎤 Recognized: "
        f"{st.session_state.speech_text}"
    )


# ============================================================
# AI SPEAKING
# ============================================================

if (
    st.session_state.tts_enabled
    and st.session_state.last_spoken_message
):

    answer_to_speak = (
        st.session_state.last_spoken_message
    )

    st.session_state.last_spoken_message = ""

    speak_in_browser(
        answer_to_speak,
        st.session_state.voice_gender,
        st.session_state.voice_speed
    )


# ============================================================
# STOP SPEAKING
# ============================================================

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

        stop_browser_speech()

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer-native">
        🎙️ Personal SIRI • AI Voice & Chat Assistant
    </div>
    """,
    unsafe_allow_html=True
)