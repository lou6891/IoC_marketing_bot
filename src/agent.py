import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

from src.prompts import FOLLOW_UP_SYSTEM_PROMPT, SYSTEM_PROMPT, IMAGE_PROMPT

load_dotenv(override=True)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME")
AZURE_OPENAI_IMAGE_MODEL_NAME = os.getenv("AZURE_OPENAI_IMAGE_MODEL_NAME")


class FollowUP(BaseModel):
    text: str


class FollowUps(BaseModel):
    questions: list[FollowUP]


class GPTAgent:
    def __init__(
        self,
        user_form_answers: dict,
        api_key: str = AZURE_OPENAI_API_KEY,
        azure_endpoint: str = AZURE_OPENAI_ENDPOINT,
        model: str = AZURE_OPENAI_MODEL_NAME,
        image_model: str = AZURE_OPENAI_IMAGE_MODEL_NAME,
    ) -> None:
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version="2024-08-01-preview",
        )

        self.model = model
        self.image_model = image_model

        self.user_form_answers = user_form_answers
        self.chat_system_prompt = self.generate_chat_system_prompt(user_form_answers)
        self.follow_up_system_prompt = self.generate_follow_up_system_prompt(
            user_form_answers
        )

    @staticmethod
    def generate_chat_system_prompt(user_form_answers: dict[str, list | str]) -> str:
        return SYSTEM_PROMPT.format(
            shop_type=user_form_answers["shop_type"],
            age=user_form_answers["age"],
            communication_type=user_form_answers["communication_type"],
            occasion=user_form_answers["occasion"],
            promotion_type=user_form_answers["promotion_type"],
        )

    @staticmethod
    def generate_follow_up_system_prompt(
        user_form_answers: dict[str, list | str],
    ) -> str:
        return FOLLOW_UP_SYSTEM_PROMPT.format(
            shop_type=user_form_answers["shop_type"],
            age=user_form_answers["age"],
            communication_type=user_form_answers["communication_type"],
            occasion=user_form_answers["occasion"],
            promotion_type=user_form_answers["promotion_type"],

        )

    @staticmethod
    def generate_image_prompt(
        user_form_answers: dict[str, list | str], chat_history: str
    ) -> str:
        return IMAGE_PROMPT.format(
            shop_type=user_form_answers["shop_type"],
            age=user_form_answers["age"],
            communication_type=user_form_answers["communication_type"],
            occasion=user_form_answers["occasion"],
            promotion_type=user_form_answers["promotion_type"],
            chat_history=chat_history,
        )

    @staticmethod
    def process_stream(stream_response):
        """Genera i chunk di testo in streaming."""
        for chunk in stream_response:
            if len(chunk.choices) == 0:
                continue

            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

    @staticmethod
    def generate_follow_up_message_context(conversation: list):
        last_user_message = ""
        last_assistant_message = ""
        for msg in reversed(conversation):
            if msg["role"] == "user" and not last_user_message:
                last_user_message = msg["content"]
            elif msg["role"] == "assistant" and not last_assistant_message:
                last_assistant_message = msg["content"]
            if last_user_message and last_assistant_message:
                break
        return last_user_message, last_assistant_message

    def streaming_query(self, messages):
        """Invia la richiesta di chat in streaming al modello."""
        response = self.client.chat.completions.create(
            stream=True,
            model=self.model,
            messages=messages,
            temperature=0.6,
        )
        return response

    def query_chat_message(self, messages: list):
        """
        Prepara i messaggi da inviare al modello: inserisce il system prompt
        come primo messaggio, poi effettua la chiamata streaming e produce i chunk.
        """
        messages.insert(0, {"role": "system", "content": self.chat_system_prompt})
        response = self.streaming_query(messages)
        yield from self.process_stream(response)

    def generate_follow_ups(self, conversation: list):
        last_user_message, last_assistant_message = (
            self.generate_follow_up_message_context(conversation)
        )

        if not last_user_message and not last_assistant_message:
            return []

        user_prompt = (
            f"Conversazione:\n"
            f"Ultima richiesta dell'utente: {last_user_message}\n"
            f"Ultimo messaggio generato dal bot: {last_assistant_message}\n"
        )

        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self.follow_up_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            response_format=FollowUps,
        )

        content = response.choices[0].message.parsed
        return [question.text for question in content.questions]

    def generate_images(self, conversation: list[dict]) -> str:
        prompt = self.generate_image_prompt(self.user_form_answers, str(conversation))

        response = self.client.images.generate(
            model=self.image_model,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        url = response.data[0].url

        return url
