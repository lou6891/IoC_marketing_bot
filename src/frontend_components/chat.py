import streamlit as st
from src.agent import GPTAgent
from src.constants import (
    FRONTEND_BOT_ICON,
    FRONTEND_USER_ICON,
)
from src.frontend_components.utils import show_selected_answers

DEFAULT_FOLLOW_UP = ["Image generation"]


def reset_chat(messages_value: list | None = []) -> None:
    st.session_state["messages"] = messages_value
    st.session_state["pending_user_input"] = ""
    st.session_state["follow_ups"]: list = DEFAULT_FOLLOW_UP


def process_first_automatic_bot_response(gpt_agent: GPTAgent):
    assistant_response = ""
    stream_response = gpt_agent.query_chat_message(st.session_state["messages"])

    for chunk in stream_response:
        assistant_response += chunk

    st.session_state["messages"].append(
        {"role": "assistant", "content": assistant_response}
    )


def process_and_display_gpt_streaming_response(
    gpt_agent: GPTAgent, bot_icon: str
) -> str:
    assistant_placeholder = st.empty()
    assistant_response = ""

    with st.chat_message("assistant", avatar=bot_icon):
        stream_response = gpt_agent.query_chat_message(st.session_state["messages"])

        for chunk in stream_response:
            assistant_response += chunk
            assistant_placeholder.markdown(assistant_response)

    st.session_state["messages"].append(
        {"role": "assistant", "content": assistant_response}
    )


def generate_follow_up_suggestion(gpt_agent: GPTAgent) -> str:
    messages = st.session_state["messages"]

    suggestions = gpt_agent.generate_follow_ups(messages)
    st.session_state["follow_ups"] = [*DEFAULT_FOLLOW_UP, *suggestions]


def display_user_message_to_chat(chat_text: str, user_icon: str):
    with st.chat_message("user", avatar=user_icon):
        st.markdown(chat_text)


def handle_and_display_follow_up_suggestions(gpt_agent: GPTAgent) -> None:
    if st.session_state["follow_ups"]:
        st.markdown("**Suggerimenti di follow-up:**")
        for i, suggestion in enumerate(st.session_state["follow_ups"], start=1):
            if suggestion != "Image generation" and st.button(
                f"{i}. {suggestion}", key=f"follow_up_{i}"
            ):
                # add follow up to pending user input, which is needed to run the agent with the follow up question
                st.session_state["pending_user_input"] = suggestion

                # reset follow up, update the frontend
                st.session_state["follow_ups"] = DEFAULT_FOLLOW_UP
                st.rerun()

            if suggestion == "Image generation":
                with st.expander("Genera Immagine"):
                    if st.button(
                        f"Genera un'immagine data la conversazione",
                        key="generate_image_",
                    ):
                        image = gpt_agent.generate_images(st.session_state["messages"])
                        st.image(image)


def display_conversation_history(user_icon: str, bot_icon: str) -> None:
    if st.session_state["messages"] is None:
        return

    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(
            message["role"], avatar=user_icon if message["role"] == "user" else bot_icon
        ):
            st.markdown(message["content"])


def chat_component(
    user_icon: str = FRONTEND_USER_ICON,
    bot_icon: str = FRONTEND_BOT_ICON,
) -> None:
    gpt_agent = GPTAgent(
        st.session_state.answers,
        st.secrets["AZURE_OPENAI_API_KEY"],
        st.secrets["AZURE_OPENAI_ENDPOINT"],
        st.secrets["AZURE_OPENAI_MODEL_NAME"],
    )

    # INITIALIZE SESSION STATES #######################################################################################
    if "follow_ups" not in st.session_state:
        st.session_state["follow_ups"] = DEFAULT_FOLLOW_UP

    if "pending_user_input" not in st.session_state:
        st.session_state["pending_user_input"] = ""

    if "messages" not in st.session_state or st.session_state["messages"] is None:
        st.session_state["messages"] = []
        process_first_automatic_bot_response(gpt_agent)
        generate_follow_up_suggestion(gpt_agent)

    if "answers" in st.session_state:
        answers = st.session_state.answers
        st.subheader("Importazioni della comunicatione")
        show_selected_answers(answers)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cambia le mie esigenze", use_container_width=True):
            st.session_state.page = "questions"
            reset_chat(messages_value=None)
            st.rerun()

    with col2:
        if st.button("Ricomincia la conversazione", use_container_width=True):
            reset_chat()

    # Show existing messages
    display_conversation_history(user_icon, bot_icon)

    chat_text = st.chat_input("Inserisci il tuo messaggio qui...")

    # The user has clicked on a follow up, use the follow up as chat input to query the model
    if st.session_state["pending_user_input"]:
        chat_text = st.session_state["pending_user_input"]
        st.session_state["pending_user_input"] = ""

    # if the user has selected a follow up (chat_text = pending_user_input) or has sent a message
    if chat_text:
        st.session_state["messages"].append({"role": "user", "content": chat_text})

        display_user_message_to_chat(chat_text, user_icon)
        process_and_display_gpt_streaming_response(gpt_agent, bot_icon)

        generate_follow_up_suggestion(gpt_agent)

    handle_and_display_follow_up_suggestions(gpt_agent)
