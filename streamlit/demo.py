import random
import logging
import streamlit as st
import pandas as pd
from datetime import datetime
from uuid import uuid4
from streamlit_js_eval import streamlit_js_eval
from demo.utils import response_generator
from demo.chat import single_document_qa

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

# ----- initialize variables ---- #
LOGGER = logging.getLogger("lge")
PREV_CHAT_PATH = "streamlit/demo/data/previous_chats.csv"
SESSION_ID = st.runtime.scriptrunner.script_run_context.get_script_run_ctx().session_id

# ----- set page configuration ---- #
st.set_page_config(page_title="GenAI Demo", page_icon="streamlit/demo/data/chang.jpeg")

# ----- set custom css ---- #
st.markdown(
    """
<style>
[data-testid="stPopoverBody"] {
    border-color:white;
}
[data-testid="stHorizontalBlock"] {
    display: flex;
    align-items: center;
}
div.stButton > button.st-emotion-cache-hc3laj {
    background-color: #F36E6C;
}
</style>
""",
    unsafe_allow_html=True,
)

# ----- temporal sample documents ---- #
DOCUMENTS = [
    {"title": "문서1", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "1"},
    {"title": "문서2", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "2"},
    {"title": "문서3", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "3"},
    {"title": "문서4", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "4"},
    {"title": "문서5", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "5"},
]

# ---- initialize session_state variables ---- #
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

if "session_id" not in st.session_state:
    st.session_state.session_id = SESSION_ID

if "session_history" not in st.session_state:
    st.session_state.session_history = ""

try:
    if "chat_df" not in st.session_state:
        st.session_state.chat_df = pd.read_csv(PREV_CHAT_PATH)
except FileNotFoundError:
    st.session_state.chat_df = pd.DataFrame(
        columns=["session_id", "chat_id", "role", "content", "documents", "created_at"]
    )


# ----- tools ----- #
def clear_memory():
    st.session_state.messages = []


def delete_chatlog(session_id: str):
    LOGGER.debug(f"To delete session_id: {session_id}")
    chat_df = st.session_state.chat_df
    chat_df = chat_df[chat_df["session_id"] != session_id].reset_index(drop=True)
    st.session_state.chat_df = chat_df
    LOGGER.debug(f"Remaining session_id: {chat_df.session_id.unique().tolist()}")
    chat_df.to_csv(PREV_CHAT_PATH, index=None)

    # reset session_id to new one
    st.session_state.session_id = str(uuid4())


def search_documents(question: str):
    documents = random.sample(DOCUMENTS, 2)
    return documents


def get_button_label(chat_df: pd.DataFrame, session_id: str):
    first_msg = chat_df[(chat_df["session_id"] == session_id) & (chat_df["role"] == "User")].iloc[0]["content"]
    return f"Session {session_id[0:7]}: {' '.join(first_msg.split()[:5])}..."


def submit():
    # in order to clear the input question after submission
    st.session_state["prompt"] = st.session_state["input-question"]
    st.session_state["input-question"] = ""


# ----- web title ----- #
st.title("GenAI Demo")

# ----- side bar to show previous chats ----- #
col1, col2 = st.sidebar.columns([0.6, 0.4])
with col1:
    st.title("Previous Chats")
with col2:
    new_chat_button = st.button("New Chat", type="primary")
    if new_chat_button:
        # if new chat button was hit, refresh entire page
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

chat_df = st.session_state["chat_df"]
session_history = st.empty()

for i, session_id in enumerate(chat_df["session_id"].unique()):
    button_label = get_button_label(chat_df, session_id)

    # if button is clicked, show chat history below the web title
    col1, col2 = st.sidebar.columns([9, 1])

    button = col1.button(button_label, use_container_width=True)
    if button:
        # clear the text_input
        st.session_state.prompt = ""

        loaded_chat = chat_df[chat_df["session_id"] == session_id]
        loaded_chat = "\n".join(f"{row.role}: {row.content}" for _, row in loaded_chat.iterrows())
        st.session_state.session_history = loaded_chat

        # show session_history below the header
        session_history.text(st.session_state.session_history)

        # change the session_id to that the selected previous session_id
        st.session_state.session_id = session_id

    delete_button = col2.button(label="x", key=i, on_click=delete_chatlog, args=(session_id,))


# ----- waiting for user input ----- #
LOGGER.debug(f"Session ID: {st.session_state.session_id}")
st.text_input("Your question ... ", key="input-question", on_change=submit)
LOGGER.debug(f"incoming user question: {st.session_state['prompt']}")

# show session_history continuously above the text_input field
session_history.text(st.session_state.session_history)

if prompt := st.session_state.prompt:
    chat_df = st.session_state["chat_df"]

    session_chat_df = chat_df[chat_df["session_id"] == st.session_state.session_id]
    cached_chat_df = session_chat_df[(session_chat_df["role"] == "User") & (session_chat_df["content"] == prompt)]

    # in order not to rerun the same user question with llm
    if len(cached_chat_df) >= 1:
        LOGGER.debug(f"{prompt} found in session_history.")

        chat_id = cached_chat_df["chat_id"].iat[0]
        cached_chat = session_chat_df[(session_chat_df["chat_id"] == chat_id) & (session_chat_df["role"] == "AI")]
        response, documents = cached_chat["content"].iat[0], cached_chat["documents"].iat[0]

        st.markdown(f"User: {prompt}")
        st.markdown(f"AI: {response}")

    else:
        st.markdown(f"User: {prompt}")

        documents = search_documents(prompt)
        response = st.write_stream(response_generator())
        response = response.replace("AI:", "").strip()  # remove prefix

        # update session_history
        st.session_state.session_history += f"\nUser: {prompt}\nAI: {response}"
        session_history.text(st.session_state.session_history)

        # save conversation log to chat_df (only if the question is never seen throughout the session)
        chat_id = uuid4()
        user_msg = pd.DataFrame(
            [
                {
                    "session_id": st.session_state.session_id,
                    "chat_id": chat_id,
                    "role": "User",
                    "content": prompt,
                    "documents": None,
                    "created_at": datetime.now(),
                }
            ]
        )

        ai_msg = pd.DataFrame(
            [
                {
                    "session_id": st.session_state.session_id,
                    "chat_id": chat_id,
                    "role": "AI",
                    "content": response,
                    "documents": documents,
                    "created_at": datetime.now(),
                }
            ]
        )

        if len(chat_df) == 0:
            chat_df = pd.concat([user_msg, ai_msg]).reset_index(drop=True)
        else:
            chat_df = pd.concat([chat_df, user_msg, ai_msg], ignore_index=True).reset_index(drop=True)

        st.session_state.chat_df = chat_df

        # overwrite existing csv
        chat_df.to_csv(PREV_CHAT_PATH, index=None)

else:
    documents = None


# ---- show documents & support multiturn --- #
if documents:
    # show list of documents
    for i, document in enumerate(documents, start=1):
        with st.container(border=True):
            st.markdown(f"**Top {i}: {document['title']}**")
            st.text(document["keyword"])
            st.text(document["summary"])

            # multiturn chat modal with single document
            single_document_qa(document=document, session_id=st.session_state.session_id)
