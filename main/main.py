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

/* ============================================================
   RESET
   ============================================================ */

html,
body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
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


/* ============================================================
   ENTIRE APP - NO PAGE SCROLL
   ============================================================ */

[data-testid="stApp"] {
    height: 100vh !important;
    overflow: hidden !important;
}

[data-testid="stAppViewContainer"] {
    height: 100vh !important;
    overflow: hidden !important;
    background: #f4f7fb !important;
}

[data-testid="stMain"] {
    height: 100vh !important;
    overflow: hidden !important;
}


/* ============================================================
   MAIN CONTENT
   ============================================================ */

[data-testid="stMainBlockContainer"] {

    max-width: 1280px !important;

    height: 100vh !important;

    box-sizing: border-box !important;

    margin: 0 auto !important;

    padding:
        12px 20px 10px 20px !important;

    overflow: hidden !important;

    display: flex !important;

    flex-direction: column !important;
}


/* ============================================================
   REMOVE STREAMLIT EXTRA SPACING
   ============================================================ */

[data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 0.55rem !important;
}


/* ============================================================
   TOP BANNER
   ============================================================ */

.top-banner {

    flex-shrink: 0 !important;

    width: 100% !important;

    height: 135px !important;

    min-height: 135px !important;

    max-height: 135px !important;

    box-sizing: border-box !important;

    display: flex !important;

    flex-direction: column !important;

    justify-content: center !important;

    align-items: center !important;

    text-align: center !important;

    padding: 10px !important;

    margin: 0 0 8px 0 !important;

    border-radius: 18px !important;

    background:
        linear-gradient(
            135deg,
            #edf5ff 0%,
            #f5f0ff 50%,
            #ecfbff 100%
        ) !important;

    border:
        1px solid #d6e1ef !important;

    box-shadow:
        0 5px 20px
        rgba(37, 99, 216, 0.08) !important;
}


/* ============================================================
   TITLE ICON
   ============================================================ */

.title-icon {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    font-size: 34px !important;

    line-height: 34px !important;

    height: 34px !important;

    margin: 0 0 3px 0 !important;

    padding: 0 !important;
}


/* ============================================================
   MAIN TITLE
   ============================================================ */

.main-title {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    font-size: 38px !important;

    line-height: 42px !important;

    height: 42px !important;

    font-weight: 800 !important;

    letter-spacing: -0.8px !important;

    color: #2563d8 !important;

    margin: 0 !important;

    padding: 0 !important;
}


/* ============================================================
   SUBTITLE
   ============================================================ */

.main-subtitle {

    display: block !important;

    width: 100% !important;

    text-align: center !important;

    font-size: 13px !important;

    line-height: 18px !important;

    height: 18px !important;

    font-weight: 500 !important;

    color: #667085 !important;

    margin: 2px 0 0 0 !important;

    padding: 0 !important;
}


/* ============================================================
   INFORMATION ROW
   ============================================================ */

.info-row {

    flex-shrink: 0 !important;

    width: 100% !important;

    height: 40px !important;

    min-height: 40px !important;

    margin-bottom: 7px !important;
}


/* ============================================================
   STATUS
   ============================================================ */

.ready-status {

    width: 100%;

    height: 38px;

    box-sizing: border-box;

    display: flex;

    justify-content: center;

    align-items: center;

    border-radius: 9px;

    background: #dcfce7;

    color: #15803d;

    border: 1px solid #bbf7d0;

    font-weight: 700;

    font-size: 13px;
}

.listening-status {

    width: 100%;

    height: 38px;

    box-sizing: border-box;

    display: flex;

    justify-content: center;

    align-items: center;

    border-radius: 9px;

    background: #fee2e2;

    color: #dc2626;

    border: 1px solid #fecaca;

    font-weight: 700;

    font-size: 13px;
}


/* ============================================================
   CHAT AREA
   ============================================================ */

.chat-wrapper {

    flex: 1 1 auto !important;

    min-height: 0 !important;

    width: 100% !important;

    box-sizing: border-box !important;

    overflow-y: auto !important;

    overflow-x: hidden !important;

    padding: 12px !important;

    border-radius: 14px !important;

    border: 1px solid #d6dee9 !important;

    background: #ffffff !important;

    scrollbar-width: thin !important;
}


/* Scrollbar */

.chat-wrapper::-webkit-scrollbar {
    width: 7px;
}

.chat-wrapper::-webkit-scrollbar-track {
    background: transparent;
}

.chat-wrapper::-webkit-scrollbar-thumb {
    background: #c7d0dd;
    border-radius: 10px;
}


/* ============================================================
   EMPTY CHAT
   ============================================================ */

.empty-chat {

    min-height: 300px;

    height: 100%;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;

    text-align: center;

    color: #667085;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 8px;
}

.empty-title {
    font-size: 22px;
    font-weight: 700;
    color: #1f2937;
}

.empty-text {
    font-size: 13px;
    margin-top: 4px;
}


/* ============================================================
   CHAT MESSAGE
   ============================================================ */

[data-testid="stChatMessage"] {
    margin: 3px 0 !important;
    padding: 7px 10px !important;
}

[data-testid="stChatMessageContent"] {
    font-size: 14px !important;
    line-height: 1.5 !important;
}


/* ============================================================
   BOTTOM AREA
   ============================================================ */

.bottom-area {

    flex-shrink: 0 !important;

    width: 100% !important;

    height: 132px !important;

    min-height: 132px !important;

    box-sizing: border-box !important;

    padding-top: 7px !important;

    background: #f4f7fb !important;
}


/* ============================================================
   INPUT
   ============================================================ */

[data-testid="stTextInput"] {
    margin: 0 !important;
}

[data-testid="stTextInput"] input {

    height: 44px !important;

    min-height: 44px !important;

    border-radius: 10px !important;

    border: 1px solid #cfd7e3 !important;

    background: #ffffff !important;

    color: #111827 !important;

    font-size: 14px !important;

    padding: 0 14px !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: #8a94a6 !important;
}

[data-testid="stTextInput"] input:focus {

    border-color: #2563d8 !important;

    box-shadow:
        0 0 0 2px
        rgba(37, 99, 216, 0.12) !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {

    height: 42px !important;

    min-height: 42px !important;

    border-radius: 10px !important;

    font-size: 13px !important;

    font-weight: 700 !important;

    border: 1px solid #d1d9e6 !important;

    background: #ffffff !important;

    color: #1f2937 !important;

    transition: 0.15s ease !important;
}

.stButton > button:hover {

    transform: translateY(-1px) !important;

    box-shadow:
        0 4px 12px
        rgba(15, 23, 42, 0.10) !important;
}


/* SEND */

.st-key-send_button button {

    background: #ff4b55 !important;

    color: white !important;

    border-color: #ff4b55 !important;
}


/* START */

.st-key-start_voice button {

    background: #2563d8 !important;

    color: white !important;

    border-color: #2563d8 !important;
}


/* STOP */

.st-key-stop_voice button {

    background: #dc3545 !important;

    color: white !important;

    border-color: #dc3545 !important;
}


/* SPEAKING */

.st-key-stop_speaking button {

    background: #f97316 !important;

    color: white !important;

    border-color: #f97316 !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    position: fixed !important;

    top: 0 !important;

    left: 0 !important;

    height: 100vh !important;

    z-index: 1000 !important;

    background: #ffffff !important;

    border-right:
        1px solid #dce2ea !important;
}

section[data-testid="stSidebar"] > div {

    height: 100vh !important;

    overflow-y: auto !important;
}

section[data-testid="stSidebar"]
.block-container {

    padding:
        16px 13px !important;
}


/* ============================================================
   DARK MODE
   ============================================================ */

@media (prefers-color-scheme: dark) {

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {

        background: #0f172a !important;
    }

    .top-banner {

        background:
            linear-gradient(
                135deg,
                #172554,
                #28194f,
                #083344
            ) !important;

        border-color: #334155 !important;
    }

    .title-icon {
        color: #93c5fd !important;
    }

    .main-title {
        color: #60a5fa !important;
    }

    .main-subtitle {
        color: #cbd5e1 !important;
    }

    .chat-wrapper {

        background: #111827 !important;

        border-color: #334155 !important;
    }

    .empty-title {
        color: #f1f5f9 !important;
    }

    .empty-text {
        color: #94a3b8 !important;
    }

    .bottom-area {
        background: #0f172a !important;
    }

    [data-testid="stTextInput"] input {

        background: #111827 !important;

        color: #f8fafc !important;

        border-color: #475569 !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #94a3b8 !important;
    }

    .stButton > button {

        background: #1e293b !important;

        color: #f8fafc !important;

        border-color: #475569 !important;
    }

    section[data-testid="stSidebar"] {

        background: #111827 !important;

        border-color: #334155 !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: #60a5fa !important;
    }

    section[data-testid="stSidebar"] h5 {
        color: #94a3b8 !important;
    }

    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stSlider"] label {
        color: #e5e7eb !important;
    }

    .ready-status {

        background: #064e3b !important;

        color: #86efac !important;

        border-color: #166534 !important;
    }

    .listening-status {

        background: #7f1d1d !important;

        color: #fecaca !important;

        border-color: #991b1b !important;
    }
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 768px) {

    [data-testid="stMainBlockContainer"] {

        padding:
            7px 8px !important;
    }

    .top-banner {

        height: 112px !important;

        min-height: 112px !important;

        max-height: 112px !important;

        border-radius: 14px !important;

        margin-bottom: 7px !important;
    }

    .title-icon {

        font-size: 28px !important;

        line-height: 30px !important;

        height: 30px !important;
    }

    .main-title {

        font-size: 29px !important;

        line-height: 34px !important;

        height: 34px !important;
    }

    .main-subtitle {

        font-size: 10px !important;

        line-height: 15px !important;

        height: 15px !important;
    }

    .bottom-area {

        height: 135px !important;

        min-height: 135px !important;
    }

    .stButton > button {

        font-size: 12px !important;
    }
}


/* ============================================================
   SMALL MOBILE
   ============================================================ */

@media (max-width: 480px) {

    .top-banner {

        height: 105px !important;

        min-height: 105px !important;

        max-height: 105px !important;
    }

    .title-icon {

        font-size: 25px !important;

        line-height: 27px !important;

        height: 27px !important;
    }

    .main-title {

        font-size: 25px !important;

        line-height: 30px !important;

        height: 30px !important;
    }

    .main-subtitle {

        font-size: 9px !important;

        line-height: 14px !important;

        height: 14px !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = ""

try:
    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY",
        ""
    ).strip()
except Exception:
    pass

if not GROQ_API_KEY:

    try:

        if "GROQ_API_KEY" in st.secrets:

            GROQ_API_KEY = str(
                st.secrets["GROQ_API_KEY"]
            ).strip()

    except Exception:
        pass


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

You can help with:
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
- Interviews
- Placements
- Programming projects

For technical questions, provide step-by-step explanations
when useful.
"""


# ============================================================
# GET AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:

        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Go to Streamlit Cloud → Manage app → "
            "Settings → Secrets and add:\n\n"
            "GROQ_API_KEY = \"gsk_...\""
        )

    try:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        for item in st.session_state.messages:

            conversation.append(
                {
                    "role": item["role"],
                    "content": item["content"],
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
            max_tokens=1200,
        )

        return response.choices[0].message.content

    except Exception as error:

        return (
            "⚠️ Groq request failed.\n\n"
            + str(error)
        )


# ============================================================
# SAVE CHAT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    messages_copy = [
        {
            "role": item["role"],
            "content": item["content"],
        }
        for item in st.session_state.messages
    ]

    chat_data = {
        "title": st.session_state.chat_title,
        "messages": messages_copy,
    }

    found = False

    for index, old_chat in enumerate(
        st.session_state.history
    ):

        if (
            old_chat["title"]
            == st.session_state.chat_title
        ):

            st.session_state.history[index] = (
                chat_data
            )

            found = True
            break

    if not found:

        st.session_state.history.append(
            chat_data
        )


# ============================================================
# NEW CHAT
# ============================================================

def create_new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


# ============================================================
# CLEAR CURRENT CHAT
# ============================================================

def clear_current_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


# ============================================================
# CLEAR ALL
# ============================================================

def clear_all_history():

    st.session_state.history = []

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.last_audio_hash = ""


# ============================================================
# LOAD CHAT
# ============================================================

def load_chat(index):

    save_current_chat()

    selected = st.session_state.history[index]

    st.session_state.chat_title = selected["title"]

    st.session_state.messages = [
        {
            "role": item["role"],
            "content": item["content"],
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
            "content": message,
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
            "content": answer,
        }
    )

    save_current_chat()

    if st.session_state.tts_enabled:
        st.session_state.speak_text = answer
    else:
        st.session_state.speak_text = ""


# ============================================================
# BROWSER SPEECH
# ============================================================

def browser_speak(
    text,
    gender,
    speed,
):

    if not text:
        return

    safe_text = json.dumps(str(text))

    if gender == "Girl":

        voice_code = """
        let preferredVoice = voices.find(
            voice =>
            /female|zira|samantha|susan|aria|hazel/i
            .test(voice.name)
        );
        """

    else:

        voice_code = """
        let preferredVoice = voices.find(
            voice =>
            /male|david|mark|george/i
            .test(voice.name)
        );
        """

    st.components.v1.html(
        f"""
        <script>

        const text = {safe_text};

        function speakText() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.rate = {float(speed)};
            utterance.pitch = 1;
            utterance.volume = 1;

            const voices =
                window.speechSynthesis.getVoices();

            {voice_code}

            if (preferredVoice) {{
                utterance.voice = preferredVoice;
            }}

            window.speechSynthesis.speak(utterance);
        }}

        setTimeout(speakText, 200);

        </script>
        """,
        height=1,
    )


# ============================================================
# STOP SPEECH
# ============================================================

def stop_browser_speech():

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


def convert_audio_to_text(audio_file):

    if audio_file is None:
        return ""

    try:

        audio_bytes = audio_file.getvalue()

        if not audio_bytes:
            return ""

        audio_buffer = io.BytesIO(
            audio_bytes
        )

        with sr.AudioFile(
            audio_buffer
        ) as source:

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
            "Audio processing error: "
            + str(error)
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
        key="new_chat_button",
        use_container_width=True,
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

            if len(title) > 23:
                title = title[:23] + "..."

            if st.button(
                "💬  " + title,
                key=f"history_{index}",
                use_container_width=True,
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
        key="clear_current_button",
        use_container_width=True,
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
        value=st.session_state.tts_enabled,
        key="voice_response_checkbox",
    )

    st.session_state.voice_gender = st.radio(
        "Voice",
        ["Girl", "Boy"],
        index=(
            0
            if st.session_state.voice_gender == "Girl"
            else 1
        ),
        key="voice_gender_radio",
    )

    st.session_state.voice_speed = st.slider(
        "Speech Speed",
        min_value=0.7,
        max_value=1.4,
        value=st.session_state.voice_speed,
        step=0.1,
        key="speech_speed_slider",
    )


    st.divider()


    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    if client is not None:

        st.success(
            "🟢 Groq Connected"
        )

    else:

        st.error(
            "🔴 Groq API Not Connected"
        )


    # --------------------------------------------------------
    # CLEAR HISTORY
    # --------------------------------------------------------

    if st.button(
        "🗑️  Clear All History",
        key="clear_all_button",
        use_container_width=True,
    ):

        clear_all_history()

        st.rerun()


# ============================================================
# FIXED HEADER
# ============================================================

st.markdown(
    """
    <div class="top-banner">

        <div class="title-icon">
            🎙️
        </div>

        <div class="main-title">
            Personal SIRI
        </div>

        <div class="main-subtitle">
            Your Personal AI Voice &amp; Chat Assistant
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATE / TIME / STATUS
# ============================================================

date_col, time_col, status_col = st.columns(
    [1, 1, 1]
)

now = datetime.now()


with date_col:

    st.info(
        "📅  "
        + now.strftime("%d %b %Y")
    )


with time_col:

    st.info(
        "🕐  "
        + now.strftime("%I:%M:%S %p")
    )


with status_col:

    if st.session_state.listening:

        st.markdown(
            """
            <div class="listening-status">
                🔴 Listening
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="ready-status">
                🟢 Ready
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# CHAT AREA
# ============================================================

st.markdown(
    '<div class="chat-wrapper">',
    unsafe_allow_html=True,
)


if not st.session_state.messages:

    st.markdown(
        """
        <div class="empty-chat">

            <div class="empty-icon">
                🎙️
            </div>

            <div class="empty-title">
                How can I help you?
            </div>

            <div class="empty-text">
                Type a message below or use Start Voice.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message(
                "user",
                avatar="👤",
            ):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message(
                "assistant",
                avatar="🎙️",
            ):

                st.markdown(
                    message["content"]
                )


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# BOTTOM FIXED AREA
# ============================================================

st.markdown(
    '<div class="bottom-area">',
    unsafe_allow_html=True,
)


# ============================================================
# MESSAGE INPUT
# ============================================================

input_col, send_col = st.columns(
    [6.5, 1]
)


with input_col:

    user_message = st.text_input(
        "Message Personal SIRI",
        placeholder="💬 Message Personal SIRI...",
        label_visibility="collapsed",
        key="message_input",
    )


with send_col:

    send_clicked = st.button(
        "➤ Send",
        key="send_button",
        type="primary",
        use_container_width=True,
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
# VOICE BUTTON
# ============================================================

left, center, right = st.columns(
    [1, 3, 1]
)


with center:

    if not st.session_state.listening:

        if st.button(
            "🎙️  Start Voice",
            key="start_voice",
            use_container_width=True,
        ):

            st.session_state.listening = True

            st.rerun()

    else:

        if st.button(
            "⏹️  Stop Listening",
            key="stop_voice",
            use_container_width=True,
        ):

            st.session_state.listening = False

            st.rerun()


# ============================================================
# MICROPHONE
# ============================================================

if st.session_state.listening:

    audio_value = st.audio_input(
        "Record your message",
        key="microphone_input",
    )

    if audio_value is not None:

        audio_bytes = audio_value.getvalue()

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
# STOP AI SPEAKING
# ============================================================

left, center, right = st.columns(
    [1, 2, 1]
)


with center:

    if st.button(
        "⏹️  Stop AI Speaking",
        key="stop_speaking",
        use_container_width=True,
    ):

        stop_browser_speech()

        st.session_state.speak_text = ""

        st.rerun()


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# TEXT TO SPEECH
# ============================================================

if st.session_state.speak_text:

    text_to_speak = (
        st.session_state.speak_text
    )

    st.session_state.speak_text = ""

    browser_speak(
        text_to_speak,
        st.session_state.voice_gender,
        st.session_state.voice_speed,
    )
