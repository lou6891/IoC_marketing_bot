import streamlit as st
from src.frontend_components.utils import show_selected_answers

def create_pills(
    question: str, option_map: dict[int, str], selection_mode: str = "multi"
) -> str | list[str]:
    return st.pills(
        question,
        options=option_map,
        format_func=lambda option: option_map[option],
        selection_mode=selection_mode,
        key=",".join(option_map.values()),
    )

def verify_and_show_selected_answers(answers: dict) -> None:
    if (
        answers["shop_type"] is not None
        and answers["age"] is not None
        and answers["communication_type"] is not None
        and answers["occasion"] is not None
    ):
        if st.button("Invia"):
            st.session_state.answers = answers
            st.session_state.page = "chat"
            st.rerun()
    else:
        st.write("**Compila tutte le domande per abilitare il pulsante di invio.**")


def user_questioner():
    answers = {}
    st.subheader(
        "Questo questionario raccoglie informazioni per generare messaggi WhatsApp per i clienti in diverse occasioni."
    )

    st.write("1. Quale tipo di ottico sei?")
    shop_type_map = {
        0: "Lusso",
        1: "Bambini",
        2: "Sportivo",
        3: "Tecnico",
        4: "Sole",
        5: "Vista (occhiali da vista)",
        6: "Lenti a contatto",
        7: "Controllo della vista",
    }
    shop_type_selected_keys = create_pills(
        "Seleziona una o più opzioni:", shop_type_map
    )
    answers["shop_type"] = (
        [shop_type_map[key] for key in shop_type_selected_keys]
        if shop_type_selected_keys
        else None
    )

    # Domanda 2: Fascia d'età del target
    st.write("2. Qual è la fascia d'età del pubblico target di questa comunicazione?")
    age_map = {
        0: "0-10 anni",
        1: "11-18 anni",
        2: "19-30 anni",
        3: "31-50 anni",
        4: "51-65 anni",
        5: "65+ anni",
    }
    age_selected_keys = create_pills("Seleziona una o più fasce d'età:", age_map)
    answers["age"] = (
        [age_map[key] for key in age_selected_keys] if age_selected_keys else None
    )

    # Domanda 3: Tono di voce
    st.write("3. Qual è il tono di voce di questa comunicazione?")
    communication_type_map = {
        0: "Professionale",
        1: "Amichevole",
        2: "Informale",
        3: "Formale",
        4: "Elegante",
        5: "Tecnico",
    }
    communication_type_selected_key = create_pills(
        "Seleziona una opzione:", communication_type_map, selection_mode="single"
    )
    answers["communication_type"] = (
        communication_type_map[communication_type_selected_key]
        if isinstance(communication_type_selected_key, int)
        else None
    )

    st.write("4. Qual è l'occasione di questa comunicazione?")
    occasion_map = {
        0: "Promozione speciale",
        1: "Promemoria appuntamento",
        2: "Ringraziamento per la fedeltà",
        3: "Promozione stagionale",
        4: "Compleanno",
        5: "Promozione post vendita",
        6: "Richiesta valutazione",
        # 2: "Nuovo prodotto disponibile",
    }
    occasion_selected_key = create_pills(
        "Seleziona una opzione:", occasion_map, selection_mode="single"
    )
    answers["occasion"] = (
        occasion_map[occasion_selected_key]
        if isinstance(occasion_selected_key, int)
        else None
    )

    st.subheader("Le tue risposte")

    show_selected_answers(answers)

    verify_and_show_selected_answers(answers)