import streamlit as st
from src.agent import GPTAgent, generate_follow_up_suggestions


logo_url = "https://www.otticoincloud.it/wp-content/uploads/2023/10/OIC-Favicon.png"  # Replace with your logo URL
user_png = "public/user.png"
bot_png = "public/bot_round.png"


# =============================================================================
#                             MAIN APP
# =============================================================================
def main():
    st.set_page_config(page_title="OiC Bot", page_icon=logo_url)

    gpt_agent = GPTAgent(
        st.secrets["AZURE_OPENAI_API_KEY"],
        st.secrets["AZURE_OPENAI_ENDPOINT"],
        st.secrets["AZURE_OPENAI_MODEL_NAME"],
    )

    st.markdown(
        """
    <style>
        body {
            background-color: white;
        }
        .block-container {
            padding-top: 40px;
        }
        .custom-logo {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 1000;
            padding-top: 15px;
        }
        .app-title-container {
            margin-left: 250px;
            padding-top: 0px;
            padding-bottom: 10px;
        }
        h1.app-title {
            margin: 0;
            font-weight: bold;
            font-size: 3.5em;
            padding-top: 5px;
            padding-bottom: 0px;
        }
        h2.app-subtitle {
            margin: 0;
            font-size: 2em;
            font-weight: bold;
            /*
            white-space: nowrap;
            overflow: visible;
            padding-top: 0px;
            */
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Add a custom logo to the top-left
    st.markdown(
        f'<img src="{logo_url}" class="custom-logo" width="150">',
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

    # st.title("Ottico in Cloud - Chatbot")

    # Inizializziamo la session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "follow_ups" not in st.session_state:
        st.session_state["follow_ups"] = []

    # Variabile di sessione per gestire un input proveniente dal click su un follow-up
    if "pending_user_input" not in st.session_state:
        st.session_state["pending_user_input"] = ""

    # Mostriamo i messaggi esistenti (esclusi "system")
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(
            message["role"], avatar=user_png if message["role"] == "user" else bot_png
        ):
            st.markdown(message["content"])

    # 1. Leggiamo la chat_input
    chat_text = st.chat_input("Inserisci il tuo messaggio qui...")

    # 2. Se la variabile pending_user_input ha un testo, lo usiamo come se fosse chat_input.
    #    E resettiamo pending_user_input a stringa vuota.
    if st.session_state["pending_user_input"]:
        chat_text = st.session_state["pending_user_input"]
        st.session_state["pending_user_input"] = ""

    # Se abbiamo qualche testo (da chat_input o da follow-up), processiamo
    if chat_text:
        # Aggiungiamo il messaggio dell'utente alla sessione
        st.session_state["messages"].append({"role": "user", "content": chat_text})

        # Visualizziamo il messaggio dell'utente
        with st.chat_message("user", avatar=user_png):
            st.markdown(chat_text)

        # Prepara un contenitore per la risposta in streaming
        assistant_placeholder = st.empty()

        # Istanzia l'agente
        assistant_response = ""
        with st.chat_message("assistant", avatar=bot_png):
            # Inviamo tutti i messaggi (incluso system prompt) al modello, in streaming
            stream_response = gpt_agent.run(st.session_state["messages"])
            for chunk in stream_response:
                assistant_response += chunk
                assistant_placeholder.markdown(assistant_response)

        # Salviamo la risposta finale
        st.session_state["messages"].append(
            {"role": "assistant", "content": assistant_response}
        )

        # Generazione follow-up
        suggestions = generate_follow_up_suggestions(
            gpt_agent, st.session_state["messages"]
        )
        st.session_state["follow_ups"] = suggestions

    # Mostriamo i suggerimenti di follow-up
    if st.session_state["follow_ups"]:
        st.markdown("**Suggerimenti di follow-up:**")
        for i, suggestion in enumerate(st.session_state["follow_ups"], start=1):
            if st.button(f"{i}. {suggestion}", key=f"follow_up_{i}"):
                # Al click, mettiamo il testo scelto in pending_user_input
                st.session_state["pending_user_input"] = suggestion
                # Se vuoi, svuota i follow-up:
                st.session_state["follow_ups"] = []
                # Forziamo un reload immediato per processare la richiesta
                st.rerun()


if __name__ == "__main__":
    main()
