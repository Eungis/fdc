import time
import streamlit as st


def clear_memory():
    st.session_state.messages = []


def response_generator():
    response = "Hey here you go!! This is multiturn chat!!"
    for i, word in enumerate(response.split()):
        if i == 0:
            yield "AI: " + word + " "
        else:
            yield word + " "
        time.sleep(0.05)


def single_document_qa(document: dict):
    with st.popover(f"Multiturn QA", use_container_width=True):
        st.markdown(f"**{document['title']}**")
        if clear := st.button("Clear Memory", key=f"{document['doc_key']}-clear-btn", on_click=clear_memory):
            st.rerun()

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if prompt := st.chat_input("Your question ... ", key=f"{document['doc_key']}-input-btn"):
            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                response = st.write_stream(response_generator())

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
