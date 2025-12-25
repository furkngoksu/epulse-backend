import logging
import time
from typing import Optional

from openai import OpenAI
from openai import OpenAIError

from app.core.config import settings
from app.exceptions.exceptions import (
    ServiceUnavailableException,
    BadGatewayException,
    GatewayTimeoutException,
)

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Simple wrapper around the OpenAI Assistants API using threads per session.
    """

    def __init__(self):
        self.client = (
            OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
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
            logger.error("Chatbot service not configured")
            raise ServiceUnavailableException(
                "Chatbot is not configured. Please set OPENAI_API_KEY and OPENAI_ASSISTANT_ID."
            )

        is_new_thread = thread_id is None
        thread_id = thread_id or self._create_thread()
        instructions = self._build_instructions(extra_context=extra_context)

        logger.info(
            "Chatbot query started",
            extra={
                "thread_id": thread_id,
                "is_new_thread": is_new_thread,
                "has_context": extra_context is not None,
            },
        )

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
                logger.debug(
                    "Patient context added to thread", extra={"thread_id": thread_id}
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
                max_completion_tokens=4096,
            )

            logger.debug(
                "OpenAI run created", extra={"thread_id": thread_id, "run_id": run.id}
            )

            self._wait_for_run_completion(
                thread_id=thread_id,
                run_id=run.id,
            )

            answer = self._get_latest_assistant_message(thread_id)

            logger.info(
                "Chatbot response generated successfully",
                extra={"thread_id": thread_id, "answer_length": len(answer)},
            )

        except OpenAIError as exc:
            logger.error(
                f"OpenAI API error: {str(exc)}", extra={"thread_id": thread_id}
            )
            raise BadGatewayException("Chatbot failed to generate response") from exc

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
            "If the question is unrelated to healthcare or the app, reply briefly that you are a health assistant and cannot help with unrelated topics. "
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
        logger.debug("New thread created", extra={"thread_id": thread.id})
        return thread.id

    def _wait_for_run_completion(self, thread_id: str, run_id: str):
        attempts = 0
        while attempts < 30:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id,
            )

            if run.status == "completed":
                logger.debug(
                    "Run completed",
                    extra={
                        "thread_id": thread_id,
                        "run_id": run_id,
                        "attempts": attempts,
                    },
                )
                return run

            if run.status in {"failed", "cancelled", "expired"}:
                logger.error(
                    f"Run failed with status: {run.status}",
                    extra={
                        "thread_id": thread_id,
                        "run_id": run_id,
                        "status": run.status,
                    },
                )
                raise BadGatewayException("Chatbot failed to generate response")

            attempts += 1
            time.sleep(0.5)

        logger.error(
            "Run timed out",
            extra={"thread_id": thread_id, "run_id": run_id, "attempts": attempts},
        )
        raise GatewayTimeoutException("Chatbot response timed out")

    def _get_latest_assistant_message(self, thread_id: str) -> str:
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=10,
        )

        for message in messages.data:
            if message.role == "assistant" and message.content:
                # Get the first text content block
                first_content = message.content[0]
                if hasattr(first_content, "text") and hasattr(
                    first_content.text, "value"
                ):  # type: ignore
                    content = first_content.text.value.strip()  # type: ignore
                    if content:
                        return content

        logger.error("No assistant message found", extra={"thread_id": thread_id})
        raise BadGatewayException("Chatbot failed to generate response")
