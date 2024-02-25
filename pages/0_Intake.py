from openai import OpenAI
import time
import streamlit as st
from prompts.intake import intake_prompt


if "client" not in st.session_state:
    # Initialize the client
    st.session_state.client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    # Step 1: Create an Assistant
    st.session_state.assistant = st.session_state.client.beta.assistants.create(
        name="Divorce mediator",
        instructions=intake_prompt,
        model="gpt-4-turbo-preview",
    )

    # Step 2: Create a Thread
    st.session_state.thread = st.session_state.client.beta.threads.create()

container = st.container(height=600)

if user_prompt := st.chat_input("Say something"):
    # Step 3: Add a Message to a Thread
    message = st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id, role="user", content=user_prompt
    )
    # container.chat_message(f"{message.role}").write(f"{user_prompt}")

    # Step 4: Run the Assistant
    run = st.session_state.client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )

    while True:
        # Wait for 5 seconds
        time.sleep(5)

        # Retrieve the run status
        run_status = st.session_state.client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id, run_id=run.id
        )

        # If run is completed, get messages
        if run_status.status == "completed":
            messages = st.session_state.client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )

            # Loop through messages and print content based on role
            for msg in reversed(messages.data):
                role = msg.role
                content = msg.content[0].text.value
                container.chat_message(f"{role}").write(f"{content}")
            break
        else:
            container.chat_message("assistant").write(
                "Waiting for the Assistant to process..."
            )
            time.sleep(5)


