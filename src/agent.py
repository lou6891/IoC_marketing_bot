import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

from src.prompts import SYSTEM_PROMPT

load_dotenv(override=True)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME")



class FollowUP(BaseModel):
    text: str


class FollowUps(BaseModel):
    questions: list[FollowUP]

# =============================================================================
#                           AGENTE GPT
# =============================================================================
class GPTAgent:
    def __init__(
        self,
        api_key: str = AZURE_OPENAI_API_KEY,
        azure_endpoint: str = AZURE_OPENAI_ENDPOINT,
        model: str = AZURE_OPENAI_MODEL_NAME,
    ) -> None:
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version="2024-08-01-preview",
        )
        self.model = model

    def process_stream(self, stream_response):
        """Genera i chunk di testo in streaming."""
        for chunk in stream_response:
            if len(chunk.choices) == 0:
                continue

            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    def streaming_query(self, messages):
        """Invia la richiesta di chat in streaming al modello."""
        response = self.client.chat.completions.create(
            stream=True,
            model=self.model,
            messages=messages,
            temperature=0.4,
        )
        return response

    def run(self, messages: list):
        """
        Prepara i messaggi da inviare al modello: inserisce il system prompt
        come primo messaggio, poi effettua la chiamata streaming e produce i chunk.
        """
        # Inseriamo il system prompt come primo messaggio, ma non lo mostreremo a schermo.
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        response = self.streaming_query(messages)
        yield from self.process_stream(response)


# =============================================================================
#                FUNZIONE PER GENERARE MESSAGGI DI FOLLOW-UP
# =============================================================================



def generate_follow_up_suggestions(agent: GPTAgent, conversation: list):
    """
    Usa l'ultima domanda dell'utente e l'ultima risposta dell'assistente
    per generare 3 possibili domande di follow-up in formato JSON.
    """
    # Recupera l'ultima domanda dell'utente e l'ultima risposta dell'assistente
    last_user = ""
    last_assistant = ""
    for msg in reversed(conversation):
        if msg["role"] == "user" and not last_user:
            last_user = msg["content"]
        elif msg["role"] == "assistant" and not last_assistant:
            last_assistant = msg["content"]
        if last_user and last_assistant:
            break

    # Se per qualche ragione non ci sono abbastanza messaggi, nessun follow-up
    if not last_user or not last_assistant:
        return []

    # Prompt di sistema apposito per la generazione di follow-up
    system_prompt = """
    Sei un assistente che fornisce esclusivamente 3 possibili domande di follow-up. 
    Che l'utente potrebbe fare a un modello GPT che genera messsaggi marketing per negozi di ottica.
    """
    # Prompt utente: passiamo la breve conversazione per contestualizzare
    user_prompt = (
        f"Conversazione:\n"
        f"Utente: {last_user}\n"
        f"Assistente: {last_assistant}\n"
        "Genera 3 possibili domande di follow-up, brevi, come array JSON."
    )

    # Facciamo una chiamata 'non in streaming' per recuperare in un colpo solo la lista
    response = agent.client.beta.chat.completions.parse(
        model=agent.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        response_format=FollowUps,
    )

    # Prendiamo il testo della risposta
    content = response.choices[0].message.parsed
    return [question.text for question in content.questions]