import streamlit as st

from src.constants import (
    FRONTEND_BOT_ICON,
    FRONTEND_HTML_STYLES,
    FRONTEND_OIC_LOGO_URL,
    FRONTEND_USER_ICON,
)
from src.frontend_components.chat import chat_component
from src.frontend_components.questionnaire import user_questioner


def display_logo(oic_logo_url: str) -> None:
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


def main(
    oic_logo_url: str = FRONTEND_OIC_LOGO_URL,
    user_icon: str = FRONTEND_USER_ICON,
    bot_icon: str = FRONTEND_BOT_ICON,
):
    st.set_page_config(page_title="OiC Bot", page_icon=oic_logo_url)

    display_logo(oic_logo_url)

    if "page" not in st.session_state:
        st.session_state.page = "questions"

    if st.session_state.page == "questions":
        user_questioner()
    elif st.session_state.page == "chat":
        chat_component(user_icon, bot_icon)


if __name__ == "__main__":
    main()
