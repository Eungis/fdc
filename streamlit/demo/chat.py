import time
import streamlit as st


def clear_memory(message_key: str):
    st.session_state[message_key] = []


def response_generator():
    response = "Hey here you go!! This is multiturn chat!!"
    for i, word in enumerate(response.split()):
        if i == 0:
            yield "AI: " + word + " "
        else:
            yield word + " "
        time.sleep(0.05)


def single_document_qa(document: dict):
    with st.popover("Multiturn QA", use_container_width=True):
        st.markdown(f"**{document['title']}**")
        message_key = f"message-{document['doc_key']}"

        if clear := st.button(
            "Clear Memory", key=f"{document['doc_key']}-clear-btn", on_click=clear_memory, args=(message_key,)
        ):
            st.rerun()

        prompt = st.chat_input("Your question ... ", key=f"{document['doc_key']}-input-btn")

        # initialize chat history
        if message_key not in st.session_state:
            st.session_state[message_key] = []
        else:
            # display chat messages from history
            for message in st.session_state[message_key]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt:
            # add user message to chat history
            messages = st.session_state[message_key]
            messages.append({"role": "user", "content": prompt})

            # display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # display assistant response in chat message container
            with st.chat_message("assistant"):
                response = st.write_stream(response_generator())

            # add assistant response to chat history
            messages = st.session_state[message_key]
            messages.append({"role": "assistant", "content": response})
