import json

import requests
import streamlit as st


def main():
    st.title("Huvi's AI Butler")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    conversation_history = """"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            conversation_history += message["role"] + ": " + message["content"] + "\n"
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        system_message = f""" This is the conversation history so far: {conversation_history.strip()}. Please keep in mind the conversation history when you respond. 
        If there are no conversation history, start a new and welcome the user."""
        full_prompt = f"""
            <|im_start|>system
            {system_message}<|im_end|>
            <|im_start|>user
            {prompt}<|im_end|>
            <|im_start|>assistant
        """
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                llm_response = requests.post(
                    url="http://localhost:8080/completion",
                    stream=True,
                    data=json.dumps(
                        {"prompt": full_prompt, "n_predict": 500, "stream": True}
                    ),
                )

                for chunk in llm_response.iter_content(chunk_size=2000):
                    # Display AI message in chat message container
                    print(chunk.decode("utf-8")[6:].strip())
                    if chunk.decode("utf-8")[6:].strip() != "[DONE]":
                        print("chunk", chunk.decode("utf-8")[6:].strip())
                        data = json.loads(chunk.decode("utf-8")[6:].strip())
                        full_response += data["content"] or ""
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                print(f"An error occurred: {e}. Skipping this line.")
        st.session_state.messages.append(
            {"role": "assisstant", "content": full_response, "avatar": "assistant"}
        )


if __name__ == "__main__":
    main()
