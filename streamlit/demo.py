import random
import logging
import streamlit as st
from demo.utils import response_generator
from demo.chat import single_document_qa
from demo.schema import ChatLog, ChatLogs

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

logger = logging.getLogger("lge")

# session state
# reload page when refreshed by default.
st.set_page_config(page_title="GenAI Demo", page_icon="./images/chang.jpeg")

st.markdown(
    """
<style>
[data-testid="stPopoverBody"] {
    border-color:white;
}
</style>
""",
    unsafe_allow_html=True,
)

DOCUMENTS = [
    {"title": "문서1", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "1"},
    {"title": "문서2", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "2"},
    {"title": "문서3", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "3"},
    {"title": "문서4", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "4"},
    {"title": "문서5", "keyword": ["키워드1", "키워드2"], "summary": "요약문입니다.", "doc_key": "5"},
]

# Initialize chat history
if "chatlogs" not in st.session_state:
    st.session_state.chatlogs = []


def clear_memory():
    st.session_state.messages = []


def search_documents(question: str):
    documents = random.sample(DOCUMENTS, 2)
    return documents


st.title("GenAI Demo")

with st.container():
    prompt = st.text_input("Your question ... ", key="input-question")
    logger.info(f"incoming user question: {st.session_state['input-question']}")

    if prompt:
        history = ChatLogs()
        cached, chatlog = history.if_cached(question=prompt)
        if cached:
            logger.debug(f"{prompt} found in history.")
            st.markdown(f"User: {prompt}")
            kl_documents = chatlog.documents
            st.markdown(f"AI: {chatlog.response}")
        else:
            st.markdown(f"User: {prompt}")
            kl_documents = search_documents(prompt)
            response = st.write_stream(response_generator())
            chatlog = ChatLog(question=prompt, response=response.replace("AI:", "").strip(), documents=kl_documents)
            history.add_chatlog(chatlog)

            # st.session_state.chat_history += [{"question":prompt, "response": response, "documents": kl_documents}]
    else:
        kl_documents = None

if kl_documents:
    for i, document in enumerate(kl_documents, start=1):
        with st.container(border=True):
            st.markdown(f"**Top {i}: {document['title']}**")
            st.text(document["keyword"])
            st.text(document["summary"])

            # multiturn chat modal with single document
            single_document_qa(document=document)
