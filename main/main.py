# ============================================================
# PERSONAL SIRI
# AI VOICE & CHAT ASSISTANT
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
# OPTIONAL DOTENV
# ============================================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Personal SIRI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
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

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
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

[data-testid="stAppViewContainer"] {
    background: #f4f7fb !important;
}

[data-testid="stMain"] {
    background: #f4f7fb !important;
}

[data-testid="stMainBlockContainer"] {

    max-width: 1280px !important;

    margin: 0 auto !important;

    padding:
        12px
        20px
        20px
        20px !important;
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
   REDUCE DEFAULT STREAMLIT SPACING
   ============================================================ */

[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 0.65rem !important;
}


/* ============================================================
   TOP PERSONAL SIRI BANNER
   ============================================================ */

.top-banner {

    width: 100%;

    min-height: 155px;

    box-sizing: border-box;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;

    text-align: center;

    padding: 22px 15px;

    margin:
        0
        0
        12px
        0;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #eef5ff 0%,
            #f5f1ff 50%,
            #eefcff 100%
        );

    border:
        1px solid
        #d7e2f2;

    box-shadow:
        0 5px 20px
        rgba(
            37,
            99,
            216,
            0.08
        );
}


/* ============================================================
   TITLE MICROPHONE
   ============================================================ */

.title-icon {

    font-size: 42px;

    line-height: 1;

    margin-bottom: 6px;
}


/* ============================================================
   MAIN TITLE
   ============================================================ */

.main-title {

    width: 100%;

    text-align: center;

    font-size: 42px;

    line-height: 1.15;

    font-weight: 800;

    letter-spacing: -1px;

    color: #2563d8;

    margin: 0;

    padding: 0;
}


/* ============================================================
   SUBTITLE
   ============================================================ */

.main-subtitle {

    width: 100%;

    text-align: center;

    font-size: 14px;

    font-weight: 500;

    color: #667085;

    margin-top: 8px;
}


/* ============================================================
   DATE / TIME
   ============================================================ */

[data-testid="stAlert"] {

    border-radius: 10px !important;
}


/* ============================================================
   STATUS
   ============================================================ */

.ready-status {

    width: 100%;

    box-sizing: border-box;

    text-align: center;

    padding: 10px;

    border-radius: 10px;

    background: #dcfce7;

    color: #15803d;

    border:
        1px solid
        #bbf7d0;

    font-weight: 700;
}


.listening-status {

    width: 100%;

    box-sizing: border-box;

    text-align: center;

    padding: 10px;

    border-radius: 10px;

    background: #fee2e2;

    color: #dc2626;

    border:
        1px solid
        #fecaca;

    font-weight: 700;
}


/* ============================================================
   CHAT CONTAINER
   ============================================================ */

[data-testid="stVerticalBlockBorderWrapper"] {

    border-radius: 14px !important;

    border:
        1px solid
        #d7dee9 !important;

    background: #ffffff;
}


/* ============================================================
   CHAT MESSAGES
   ============================================================ */

[data-testid="stChatMessage"] {

    margin:
        3px
        0 !important;

    padding:
        7px
        10px !important;

    border-radius: 10px !important;
}


[data-testid="stChatMessageContent"] {

    font-size: 14px !important;

    line-height: 1.5 !important;

    color: #1f2937 !important;
}


/* ============================================================
   MESSAGE INPUT
   ============================================================ */

[data-testid="stTextInput"] {

    margin: 0 !important;
}


[data-testid="stTextInput"] input {

    height: 46px !important;

    min-height: 46px !important;

    border-radius: 10px !important;

    border:
        1px solid
        #cfd7e3 !important;

    background:
        #ffffff !important;

    color:
        #111827 !important;

    font-size:
        14px !important;

    padding:
        0 14px !important;
}


[data-testid="stTextInput"] input::placeholder {

    color:
        #8a94a6 !important;
}


[data-testid="stTextInput"] input:focus {

    border-color:
        #2563d8 !important;

    box-shadow:
        0 0 0 2px
        rgba(
            37,
            99,
            216,
            0.12
        ) !important;
}


/* ============================================================
   GENERAL BUTTON
   ============================================================ */

.stButton > button {

    min-height:
        42px !important;

    height:
        42px !important;

    border-radius:
        10px !important;

    font-size:
        13px !important;

    font-weight:
        700 !important;

    background:
        #ffffff !important;

    color:
        #1f2937 !important;

    border:
        1px solid
        #d1d9e6 !important;

    box-shadow:
        none !important;

    transition:
        all 0.15s ease;
}


.stButton > button:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 4px 12px
        rgba(
            15,
            23,
            42,
            0.10
        ) !important;
}


/* ============================================================
   SEND BUTTON
   ============================================================ */

.st-key-send_button button {

    background:
        #ff4b55 !important;

    color:
        #ffffff !important;

    border-color:
        #ff4b55 !important;
}


.st-key-send_button button:hover {

    background:
        #e83c47 !important;
}


/* ============================================================
   START VOICE
   ============================================================ */

.st-key-start_voice button {

    background:
        #2563d8 !important;

    color:
        #ffffff !important;

    border-color:
        #2563d8 !important;
}


.st-key-start_voice button:hover {

    background:
        #1d4fb0 !important;
}


/* ============================================================
   STOP LISTENING
   ============================================================ */

.st-key-stop_voice button {

    background:
        #dc3545 !important;

    color:
        #ffffff !important;

    border-color:
        #dc3545 !important;
}


/* ============================================================
   STOP AI SPEAKING
   ============================================================ */

.st-key-stop_speaking button {

    background:
        #f97316 !important;

    color:
        #ffffff !important;

    border-color:
        #f97316 !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background:
        #ffffff !important;

    border-right:
        1px solid
        #dce2ea !important;
}


section[data-testid="stSidebar"]
.block-container {

    padding:
        18px
        14px !important;
}


section[data-testid="stSidebar"] h3 {

    color:
        #2563d8 !important;

    text-align:
        center !important;

    font-size:
        21px !important;

    font-weight:
        800 !important;
}


section[data-testid="stSidebar"] h5 {

    color:
        #667085 !important;

    font-size:
        10px !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.5px !important;
}


section[data-testid="stSidebar"]
.stButton > button {

    height:
        38px !important;

    min-height:
        38px !important;

    font-size:
        12px !important;
}


/* ============================================================
   DARK MODE
   ============================================================ */

@media (prefers-color-scheme: dark) {

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {

        background:
            #0f172a !important;
    }


    [data-testid="stMainBlockContainer"] {

        color:
            #e5e7eb !important;
    }


    /* Banner */

    .top-banner {

        background:
            linear-gradient(
                135deg,
                #172554 0%,
                #28194f 50%,
                #083344 100%
            );

        border-color:
            #334155;

        box-shadow:
            0 5px 20px
            rgba(
                0,
                0,
                0,
                0.25
            );
    }


    .title-icon {

        color:
            #93c5fd;
    }


    .main-title {

        color:
            #60a5fa;
    }


    .main-subtitle {

        color:
            #cbd5e1;
    }


    /* Chat */

    [data-testid="stVerticalBlockBorderWrapper"] {

        background:
            #111827 !important;

        border-color:
            #334155 !important;
    }


    [data-testid="stChatMessageContent"] {

        color:
            #f1f5f9 !important;
    }


    [data-testid="stCaptionContainer"] {

        color:
            #aab4c3 !important;
    }


    /* Input */

    [data-testid="stTextInput"] input {

        background:
            #111827 !important;

        color:
            #f8fafc !important;

        border-color:
            #475569 !important;
    }


    [data-testid="stTextInput"]
    input::placeholder {

        color:
            #94a3b8 !important;
    }


    /* Buttons */

    .stButton > button {

        background:
            #1e293b !important;

        color:
            #f8fafc !important;

        border-color:
            #475569 !important;
    }


    /* Sidebar */

    section[data-testid="stSidebar"] {

        background:
            #111827 !important;

        border-color:
            #334155 !important;
    }


    section[data-testid="stSidebar"] h3 {

        color:
            #60a5fa !important;
    }


    section[data-testid="stSidebar"] h5 {

        color:
            #94a3b8 !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {

        color:
            #94a3b8 !important;
    }


    [data-testid="stRadio"] label,
    [data-testid="stCheckbox"] label,
    [data-testid="stSlider"] label {

        color:
            #e5e7eb !important;
    }


    /* Ready */

    .ready-status {

        background:
            #064e3b !important;

        color:
            #86efac !important;

        border-color:
            #166534 !important;
    }


    /* Listening */

    .listening-status {

        background:
            #7f1d1d !important;

        color:
            #fecaca !important;

        border-color:
            #991b1b !important;
    }
}


/* ============================================================
   TABLET / MOBILE
   ============================================================ */

@media (max-width: 768px) {

    [data-testid="stMainBlockContainer"] {

        padding:
            8px !important;
    }


    .top-banner {

        min-height:
            130px;

        padding:
            18px
            10px;

        border-radius:
            14px;
    }


    .title-icon {

        font-size:
            34px;
    }


    .main-title {

        font-size:
            30px;

        letter-spacing:
            -0.5px;
    }


    .main-subtitle {

        font-size:
            11px;
    }


    [data-testid="stTextInput"]
    input {

        font-size:
            13px !important;
    }


    .stButton > button {

        font-size:
            12px !important;
    }
}


/* ============================================================
   SMALL MOBILE
   ============================================================ */

@media (max-width: 480px) {

    .top-banner {

        min-height:
            112px;

        padding:
            14px
            7px;
    }


    .title-icon {

        font-size:
            30px;
    }


    .main-title {

        font-size:
            25px;
    }


    .main-subtitle {

        font-size:
            10px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# GROQ API KEY
# ============================================================

GROQ_API_KEY = ""


# ------------------------------------------------------------
# Check environment variable
# ------------------------------------------------------------

try:

    GROQ_API_KEY = os.environ.get(
        "GROQ_API_KEY",
        ""
    ).strip()

except Exception:

    GROQ_API_KEY = ""


# ------------------------------------------------------------
# Check Streamlit Secrets
# ------------------------------------------------------------

if not GROQ_API_KEY:

    try:

        if "GROQ_API_KEY" in st.secrets:

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


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Personal SIRI, a helpful and friendly AI
voice and chat assistant.

You can help with:

Python
Java
SQL
AI
Generative AI
Machine Learning
Cloud Computing
AWS
Linux
Networking
Aptitude
Interviews
Placements
Programming Projects

Answer clearly and naturally.

Keep simple questions concise.

For technical questions, explain step-by-step
when useful.
"""


# ============================================================
# AI RESPONSE
# ============================================================

def get_ai_response(user_message):

    if client is None:

        return (
            "⚠️ Groq API key is not configured.\n\n"
            "Please open Streamlit Cloud → "
            "Manage app → Settings → Secrets "
            "and add your GROQ_API_KEY."
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

    except Exception as error:

        return (
            "⚠️ Groq request failed.\n\n"
            + str(error)
        )


# ============================================================
# SAVE CURRENT CHAT
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    messages_copy = [
        {
            "role": item["role"],
            "content": item["content"]
        }
        for item in st.session_state.messages
    ]

    chat_data = {

        "title":
            st.session_state.chat_title,

        "messages":
            messages_copy
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
# CLEAR ALL HISTORY
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

    # Generate chat title
    if (
        st.session_state.chat_title
        == "New Chat"
    ):

        title = message[:28]

        if len(message) > 28:

            title += "..."

        st.session_state.chat_title = title

    # AI response
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
# BROWSER TEXT TO SPEECH
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
        <script>

        const text = {safe_text};

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

            utterance.pitch = 1;

            utterance.volume = 1;

            const voices =
                window.speechSynthesis
                .getVoices();

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
        """,
        height=1
    )


# ============================================================
# STOP BROWSER SPEECH
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

        audio_buffer = io.BytesIO(
            audio_bytes
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
            "I couldn't understand your voice."
        )

        return ""

    except sr.RequestError:

        st.error(
            "Speech recognition service "
            "is unavailable."
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


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "➕  New Chat",
        key="new_chat_button",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()


    # ========================================================
    # HISTORY
    # ========================================================

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


    # ========================================================
    # CURRENT CHAT
    # ========================================================

    st.markdown(
        "##### 💬 CURRENT CHAT"
    )

    if st.button(
        "🗑️  Clear Current Chat",
        key="clear_current_button",
        use_container_width=True
    ):

        clear_current_chat()

        st.rerun()


    # ========================================================
    # VOICE SETTINGS
    # ========================================================

    st.markdown(
        "##### 🎙️ VOICE SETTINGS"
    )


    voice_response = st.checkbox(
        "Voice Response",
        value=st.session_state.tts_enabled,
        key="voice_response"
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
        key="voice_gender"
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
        key="voice_speed"
    )

    st.session_state.voice_speed = (
        voice_speed
    )


    st.divider()


    # ========================================================
    # API STATUS
    # ========================================================

    if client is not None:

        st.success(
            "🟢 Groq Connected"
        )

    else:

        st.error(
            "🔴 Groq API Not Connected"
        )


    # ========================================================
    # CLEAR ALL
    # ========================================================

    if st.button(
        "🗑️  Clear All History",
        key="clear_all_button",
        use_container_width=True
    ):

        clear_all_history()

        st.rerun()


# ============================================================
# MAIN TITLE BANNER
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
    unsafe_allow_html=True
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
        + now.strftime(
            "%d %b %Y"
        )
    )


with time_col:

    st.info(
        "🕐  "
        + now.strftime(
            "%I:%M:%S %p"
        )
    )


with status_col:

    if st.session_state.listening:

        st.markdown(
            """
            <div class="listening-status">
                🔴 Listening
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="ready-status">
                🟢 Ready
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# CHAT AREA
# ============================================================

chat_area = st.container(
    height=420,
    border=True
)


with chat_area:

    if not st.session_state.messages:

        left, center, right = st.columns(
            [1, 3, 1]
        )

        with center:

            st.write("")

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

        placeholder=
            "💬 Message Personal SIRI...",

        label_visibility=
            "collapsed",

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
# START / STOP VOICE
# ============================================================

left, center, right = st.columns(
    [1, 3, 1]
)


with center:

    if not st.session_state.listening:

        if st.button(
            "🎙️  Start Voice",
            key="start_voice",
            use_container_width=True
        ):

            st.session_state.listening = True

            st.rerun()

    else:

        if st.button(
            "⏹️  Stop Listening",
            key="stop_voice",
            use_container_width=True
        ):

            st.session_state.listening = False

            st.rerun()


# ============================================================
# MICROPHONE INPUT
# ============================================================

if st.session_state.listening:

    st.info(
        "🎙️ Record your message using the microphone."
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
# AI VOICE RESPONSE
# ============================================================

if st.session_state.speak_text:

    text_to_speak = (
        st.session_state.speak_text
    )

    st.session_state.speak_text = ""

    browser_speak(
        text_to_speak,

        st.session_state.voice_gender,

        st.session_state.voice_speed
    )


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

        use_container_width=True
    ):

        stop_browser_speech()

        st.session_state.speak_text = ""

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

left, center, right = st.columns(
    [1, 2, 1]
)


with center:

    st.caption(
        "🎙️ Personal SIRI • AI Voice & Chat Assistant"
    )
