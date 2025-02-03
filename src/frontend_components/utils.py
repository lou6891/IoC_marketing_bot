
import streamlit as st


def show_selected_answers(answers: dict) -> None:
    col1, col2 = st.columns(2)

    col1.markdown(
        f"""
    **Tipologia di ottico:**  
    {", ".join(answers["shop_type"]) if answers["shop_type"] else "Non selezionato"}
    """
    )
    col2.markdown(
        f"""
        **Fascia d'età del target:**  
        {", ".join(answers["age"]) if answers["age"] else "Non selezionato"}
        """
    )
    col1.markdown(
        f"""
        **Tono di voce:**  
        {answers["communication_type"] if answers["communication_type"] else "Non selezionato"}
        """
    )
    col2.markdown(
        f"""
        **Occasione della comunicazione:**  
        {answers["occasion"] if answers["occasion"] else "Non selezionato"}
        """
    )
    col1.markdown(
        f"""
        **Tipo di Promozione:**  
        {answers["promotion_type"] if answers["promotion_type"] else "Non selezionato"}
        """
    )