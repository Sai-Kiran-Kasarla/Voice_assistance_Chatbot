import os
import io
import json
import hashlib
from datetime import datetime

import streamlit as st
import speech_recognition as sr
from groq import Groq


# ============================================================
# PAGE
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
    "audio_key": 0,
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

/* ==========================================================
   DO NOT HIDE STREAMLIT MAIN HEADER
   ========================================================== */

html,
body {
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stAppViewContainer"] {
    background: #f5f7fb !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1400px !important;
    padding: 12px 18px 15px 18px !important;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #dce3ec !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 18px 13px !important;
}

.sidebar-title {
    font-size: 21px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 3px;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #7b8494;
    margin-bottom: 18px;
}

section[data-testid="stSidebar"] .stButton > button {
    min-height: 40px !important;
    border-radius: 9px !important;
    border: 1px solid #d8e0eb !important;
    background: #ffffff !important;
    color: #273142 !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f3f7ff !important;
    border-color: #9ebcf0 !important;
}


/* ==========================================================
   PERSONAL SIRI HEADER
   ========================================================== */

.siri-header {
    width: 100%;
    height: 100px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    text-align: center;

    box-sizing: border-box;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #edf4ff 0%,
            #f6f1ff 50%,
            #edfbff 100%
        );

    border: 1px solid #d7e2f0;

    box-shadow:
        0 4px 16px rgba(37,99,235,0.07);

    margin-bottom: 8px;
}

.siri-icon {
    font-size: 27px;
    line-height: 28px;
    margin-bottom: 1px;
}

.siri-title {
    font-size: 31px;
    line-height: 35px;
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


/* ==========================================================
   STATUS
   ========================================================== */

.status-card {
    height: 38px;

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
    border: 1px solid #c5ecd2;
}

.status-listening {
    background: #fff0f0;
    color: #dc2626;
    border: 1px solid #ffd1d1;
}


/* ==========================================================
   CHAT CONTAINER
   ========================================================== */

.chat-area {
    border-radius: 15px;
    border: 1px solid #d7dee8;
    background: #ffffff;
    box-shadow: 0 2px 10px rgba(15,23,42,0.03);
}


/* ==========================================================
   EMPTY CHAT
   ========================================================== */

.empty-state {
    min-height: 290px;

    display: flex;
    flex-direction: column;

    justify-content: center;
    align-items: center;

    text-align: center;
}

.empty-icon {
    width: 68px;
    height: 68px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #eef4ff;

    font-size: 31px;

    margin-bottom: 12px;
}

.empty-title {
    font-size: 21px;
    font-weight: 750;
    color: #202938;
}

.empty-text {
    font-size: 13px;
    color: #7a8494;
    margin-top: 5px;
}


/* ==========================================================
   MESSAGE BOX
   ========================================================== */

[data-testid="stTextInput"] {
    margin-top: 2px !important;
}

[data-testid="stTextInput"] input {
    height: 44px !important;
    border-radius: 11px !important;

    border: 1px solid #ccd5e2 !important;

    background: #ffffff !important;

    padding: 0 14px !important;

    font-size: 14px !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #4d82e8 !important;

    box-shadow:
        0 0 0 2px rgba(77,130,232,.10) !important;
}


/* ==========================================================
   SEND
   ========================================================== */

.st-key-send_button button {
    height: 44px !important;
    border-radius: 11px !important;

    background: #ff4b55 !important;
    color: #ffffff !important;

    border: 1px solid #ff4b55 !important;

    font-weight: 700 !important;
}


/* ==========================================================
   START VOICE
   ========================================================== */

.st-key-start_voice button {
    height: 40px !important;
    border-radius: 10px !important;

    background: #2563d8 !important;
    color: white !important;

    border: 1px solid #2563d8 !important;

    font-weight: 700 !important;
}


/* ==========================================================
   STOP LISTENING
   ========================================================== */

.st-key-stop_voice button {
    height: 40px !important;
    border-radius: 10px !important;

    background: #dc3545 !important;
    color: white !important;

    border: 1px solid #dc3545 !important;
}


/* ==========================================================
   STOP SPEAKING
   ========================================================== */

.st-key-stop_speaking button {
    height: 38px !important;
    border-radius: 9px !important;

    background: #f97316 !important;
    color: white !important;

    border: 1px solid #f97316 !important;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 800px) {

    [data-testid="stMainBlockContainer"] {
        padding: 8px !important;
    }

    .siri-header {
        height: 86px;
    }

    .siri-title {
        font-size: 26px;
    }

    .siri-subtitle {
        font-size: 10px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = str(
            st.secrets["GROQ_API_KEY"]
        ).strip()
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
You are Personal SIRI, a helpful personal AI assistant.

Be clear, friendly and practical.

Help with:
Python, Java, SQL, AI, Generative AI,
Machine Learning, Cloud Computing, AWS,
Linux, Networking, Aptitude, Interviews,
Placements, Resume preparation and Projects.

For technical questions, provide useful
step-by-step explanations.
"""


# ============================================================
# AI
# ============================================================

def get_ai_response():

    if client is None:
        return (
            "⚠️ **Groq API is not connected.**\n\n"
            "Add `GROQ_API_KEY` in Streamlit "
            "Cloud → Settings → Secrets."
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
            max_tokens=1500,
        )

        return response.choices[0].message.content

    except Exception as error:

        return f"⚠️ **Groq Error**\n\n{error}"


# ============================================================
# CHAT FUNCTIONS
# ============================================================

def save_current_chat():

    if not st.session_state.messages:
        return

    chat = {
        "title": st.session_state.chat_title,
        "messages": list(
            st.session_state.messages
        ),
    }

    for i, old_chat in enumerate(
        st.session_state.history
    ):

        if old_chat["title"] == chat["title"]:

            st.session_state.history[i] = chat
            return

    st.session_state.history.append(chat)


def new_chat():

    save_current_chat()

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.listening = False


def clear_chat():

    st.session_state.messages = []

    st.session_state.chat_title = "New Chat"

    st.session_state.speak_text = ""

    st.session_state.listening = False


def load_chat(index):

    chat = st.session_state.history[index]

    st.session_state.chat_title = chat["title"]

    st.session_state.messages = list(
        chat["messages"]
    )


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

    if st.session_state.chat_title == "New Chat":

        title = message[:30]

        if len(message) > 30:
            title += "..."

        st.session_state.chat_title = title

    answer = get_ai_response()

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
# SPEECH RECOGNITION
# ============================================================

recognizer = sr.Recognizer()


def recognize_audio(audio):

    try:

        if audio is None:
            return ""

        audio_bytes = audio.getvalue()

        if not audio_bytes:
            return ""

        audio_file = io.BytesIO(
            audio_bytes
        )

        with sr.AudioFile(audio_file) as source:

            audio_data = recognizer.record(
                source
            )

        return recognizer.recognize_google(
            audio_data
        ).strip()

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
# TEXT TO SPEECH
# ============================================================

def browser_speak(text):

    if not text:
        return

    safe_text = json.dumps(str(text))

    if st.session_state.voice_gender == "Girl":

        voice_code = """
        let selectedVoice = voices.find(
            v => /female|zira|samantha|susan|aria|hazel/i.test(v.name)
        );
        """

    else:

        voice_code = """
        let selectedVoice = voices.find(
            v => /male|david|mark|george/i.test(v.name)
        );
        """

    st.html(
        f"""
        <script>

        const textToSpeak = {safe_text};

        function speakSiri() {{

            if (!window.speechSynthesis) {{
                return;
            }}

            window.speechSynthesis.cancel();

            const speech =
                new SpeechSynthesisUtterance(
                    textToSpeak
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
            200
        );

        </script>
        """
    )


def stop_speaking():

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
        '<div class="sidebar-title">'
        '🎙️ Personal SIRI'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Your Personal AI Voice & Chat Assistant'
        '</div>',
        unsafe_allow_html=True,
    )


    # NEW CHAT

    if st.button(
        "➕  New Chat",
        use_container_width=True,
        key="new_chat_button",
    ):

        new_chat()

        st.rerun()


    # HISTORY

    st.markdown("##### 🕘 HISTORY")

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
                use_container_width=True,
            ):

                load_chat(index)

                st.rerun()

    else:

        st.caption("No previous chats")


    # SETTINGS

    st.markdown("##### ⚙️ SETTINGS")

    st.session_state.tts_enabled = st.checkbox(
        "Voice Response",
        value=st.session_state.tts_enabled,
    )

    st.session_state.voice_gender = st.radio(
        "Voice",
        ["Girl", "Boy"],
        index=(
            0
            if st.session_state.voice_gender == "Girl"
            else 1
        ),
    )

    st.session_state.voice_speed = st.slider(
        "Speech Speed",
        0.7,
        1.4,
        st.session_state.voice_speed,
        0.1,
    )


    st.divider()


    if client:

        st.success("🟢 Groq Connected")

    else:

        st.error("🔴 Groq API Not Connected")


    if st.button(
        "🗑️ Clear Current Chat",
        use_container_width=True,
        key="clear_chat_button",
    ):

        clear_chat()

        st.rerun()


    if st.button(
        "🗑️ Clear All History",
        use_container_width=True,
        key="clear_history_button",
    ):

        st.session_state.history = []

        st.session_state.messages = []

        st.session_state.chat_title = "New Chat"

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
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
    """,
    unsafe_allow_html=True,
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
        "📅 " +
        now.strftime("%d %b %Y")
    )


with time_col:

    st.info(
        "🕐 " +
        now.strftime("%I:%M:%S %p")
    )


with status_col:

    if st.session_state.listening:

        st.markdown(
            """
            <div class="status-card status-listening">
                🔴 Listening...
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="status-card status-ready">
                🟢 Ready
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# CHAT
#
# ONLY THIS CONTAINER SCROLLS
# ============================================================

with st.container(
    height=400,
    border=True,
):

    if not st.session_state.messages:

        st.markdown(
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
        key="message_input",
    )


with send_col:

    send_clicked = st.button(
        "➤ Send",
        key="send_button",
        type="primary",
        use_container_width=True,
    )


if send_clicked:

    if user_message.strip():

        send_message(
            user_message
        )

        st.rerun()


# ============================================================
# START VOICE / STOP LISTENING
# ============================================================

voice_left, voice_center, voice_right = st.columns(
    [1, 4, 1]
)


with voice_center:

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
# VOICE RECORDING
# ============================================================

if st.session_state.listening:

    audio = st.audio_input(
        "🎤 Record your message",
        key=f"audio_{st.session_state.audio_key}",
    )

    if audio is not None:

        audio_bytes = audio.getvalue()

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

            text = recognize_audio(
                audio
            )

            st.session_state.listening = False

            if text:

                send_message(text)

                st.session_state.audio_key += 1

                st.rerun()


# ============================================================
# STOP AI SPEAKING
# ============================================================

if st.session_state.speak_text:

    _, center, _ = st.columns(
        [1, 2, 1]
    )

    with center:

        if st.button(
            "⏹️ Stop AI Speaking",
            key="stop_speaking",
            use_container_width=True,
        ):

            stop_speaking()

            st.session_state.speak_text = ""

            st.rerun()


# ============================================================
# AI VOICE
# ============================================================

if st.session_state.speak_text:

    answer = st.session_state.speak_text

    st.session_state.speak_text = ""

    browser_speak(answer)
