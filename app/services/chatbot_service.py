import time
from typing import Optional

from fastapi import HTTPException, status
from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings


class ChatbotService:
    """
    Simple wrapper around the OpenAI Assistants API using threads per session.
    """

    def __init__(self):
        self.client = (
            OpenAI(api_key=settings.OPENAI_API_KEY)
            if settings.OPENAI_API_KEY
            else None
        )
        self.assistant_id = settings.OPENAI_ASSISTANT_ID

    def get_answer(
        self,
        question: str,
        thread_id: Optional[str] = None,
        extra_context: Optional[str] = None,
        persist_context: bool = False,
    ) -> tuple[str, str]:
        if not self.client or not self.assistant_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "CHATBOT_DISABLED",
                    "message": (
                        "Chatbot is not configured. Please set OPENAI_API_KEY "
                        "and OPENAI_ASSISTANT_ID."
                    ),
                },
            )

        is_new_thread = thread_id is None
        thread_id = thread_id or self._create_thread()
        instructions = self._build_instructions(extra_context=extra_context)

        try:
            if extra_context and (persist_context or is_new_thread):
                # Persist patient context in the thread history so follow-up questions see it.
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="assistant",
                    content=(
                        "Patient context (use only if it helps answer questions): "
                        f"{extra_context}"
                    ),
                )

            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=question,
            )

            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                instructions=instructions,
                temperature=0.2,
                max_completion_tokens=400,
            )

            self._wait_for_run_completion(
                thread_id=thread_id,
                run_id=run.id,
            )

            answer = self._get_latest_assistant_message(thread_id)
        except OpenAIError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "CHATBOT_ERROR",
                    "message": "Chatbot yanit uretirken hata olustu.",
                },
            ) from exc

        return answer, thread_id

    def _build_instructions(self, extra_context: Optional[str] = None) -> str:
        base = (
            "You are a concise healthcare assistant for the E-Pulse mobile app. "
            "E-Pulse helps patients track medications, receive prescriptions from doctors, "
            "and book appointments. Answer in the same language as the user's question. "
            "Lead with a direct, practical answer to the user's question. "
            "Avoid diagnosis. Do not invent dosages. "
            "If a medication is known, include what it is for, how it is typically taken, "
            "common side effects, and key precautions. Keep it concise. "
            "Add a brief safety note only when the topic clearly involves medication use or health risk."
        )

        if extra_context:
            base += (
                " Use the following patient context only if it helps answer the question: "
                f"{extra_context}"
            )

        return base

    def _create_thread(self) -> str:
        thread = self.client.beta.threads.create()
        return thread.id

    def _wait_for_run_completion(self, thread_id: str, run_id: str):
        attempts = 0
        while attempts < 30:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id,
            )

            if run.status == "completed":
                return run

            if run.status in {"failed", "cancelled", "expired"}:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "code": "CHATBOT_ERROR",
                        "message": "Chatbot yanit uretirken hata olustu.",
                    },
                )

            attempts += 1
            time.sleep(0.5)

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "CHATBOT_TIMEOUT",
                "message": "Chatbot yaniti zamaninda uretemedi.",
            },
        )

    def _get_latest_assistant_message(self, thread_id: str) -> str:
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=10,
        )

        for message in messages.data:
            if message.role == "assistant" and message.content:
                content = message.content[0].text.value.strip()
                if content:
                    return content

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "CHATBOT_ERROR",
                "message": "Chatbot yanit uretirken hata olustu.",
            },
        )
