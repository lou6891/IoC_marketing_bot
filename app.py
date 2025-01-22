import streamlit as st
from src.agent import GPTAgent, generate_follow_up_suggestions
from src.constants import (
    FRONTEND_HTML_STYLES,
    FRONTEND_BOT_ICON,
    FRONTEND_OIC_LOGO_URL,
    FRONTEND_USER_ICON,
)


def process_and_display_gpt_streaming_response(
    gpt_agent: GPTAgent, bot_icon: str
) -> str:
    assistant_placeholder = st.empty()
    assistant_response = ""

    with st.chat_message("assistant", avatar=bot_icon):
        stream_response = gpt_agent.run(st.session_state["messages"])

        for chunk in stream_response:
            assistant_response += chunk
            assistant_placeholder.markdown(assistant_response)

    st.session_state["messages"].append(
        {"role": "assistant", "content": assistant_response}
    )


def generate_follow_up_suggestion(gpt_agent: GPTAgent) -> str:
    suggestions = generate_follow_up_suggestions(
        gpt_agent, st.session_state["messages"]
    )
    st.session_state["follow_ups"] = suggestions


def display_user_message_to_chat(chat_text: str, user_icon: str):
    with st.chat_message("user", avatar=user_icon):
        st.markdown(chat_text)


def handle_and_display_follow_up_suggestions() -> None:
    if st.session_state["follow_ups"]:
        st.markdown("**Suggerimenti di follow-up:**")
        for i, suggestion in enumerate(st.session_state["follow_ups"], start=1):
            if st.button(f"{i}. {suggestion}", key=f"follow_up_{i}"):
                # add follow up to pending user input, which is needed to run the agent with the follow up question
                st.session_state["pending_user_input"] = suggestion

                # reset follow up, update the frontend
                st.session_state["follow_ups"] = []
                st.rerun()


def display_conversation_history(user_icon: str, bot_icon: str) -> None:
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(
            message["role"], avatar=user_icon if message["role"] == "user" else bot_icon
        ):
            st.markdown(message["content"])


def chat_component(
    gpt_agent: GPTAgent,
    user_icon: str = FRONTEND_USER_ICON,
    bot_icon: str = FRONTEND_BOT_ICON,
) -> None:
    # INITIALIZE SESSION STATES #######################################################################################
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "follow_ups" not in st.session_state:
        st.session_state["follow_ups"] = []

    if "pending_user_input" not in st.session_state:
        st.session_state["pending_user_input"] = ""

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

    handle_and_display_follow_up_suggestions()


def main(
    oic_logo_url: str = FRONTEND_OIC_LOGO_URL,
    user_icon: str = FRONTEND_USER_ICON,
    bot_icon: str = FRONTEND_BOT_ICON,
):
    st.set_page_config(page_title="OiC Bot", page_icon=oic_logo_url)

    gpt_agent = GPTAgent(
        st.secrets["AZURE_OPENAI_API_KEY"],
        st.secrets["AZURE_OPENAI_ENDPOINT"],
        st.secrets["AZURE_OPENAI_MODEL_NAME"],
    )

    st.markdown(
        FRONTEND_HTML_STYLES,
        unsafe_allow_html=True,
    )

    # TITLE ###########################################################################################################
    st.markdown(
        f'<img src="{oic_logo_url}" class="custom-logo" width="150">',
        unsafe_allow_html=True,
    )

    # Adjust the title to align properly with space for the logo
    st.markdown(
        """
        <div class="app-title-container">
            <h1 class="app-title">Ottico in Cloud</h1>
            <h2 class="app-subtitle">Generatore marketing</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # chat ############################################################################################################
    chat_component(gpt_agent, user_icon, bot_icon)


if __name__ == "__main__":
    main()
