import asyncio
import json
import logging
import uuid

from .answer_validator import validate_answer
from .business_config import load_business
from .cache import get, put
from .context_selector import context_text, select_context
from .contracts import BotReply, Source, Status
from .conversation import local_reply
from .faq import lookup
from .security import clean_input, injection_suspected


# Usa o logger já configurado pelo Uvicorn e exibido no Render.
log = logging.getLogger("uvicorn.error")

COMPLEX = (
    "explique",
    "por que",
    "porque",
    "resuma",
    "compare",
    "relacione",
    "analise",
    "interprete",
    "justifique",
    "sintetize",
)


def _emit(request_id, state, **extra):
    log.info(
        json.dumps(
            {
                "request_id": request_id,
                "state": state,
                **extra,
            },
            ensure_ascii=False,
        )
    )


def _reply(
    request_id,
    answer,
    source,
    status="answered",
    evidence="",
    cached=False,
):
    return BotReply(
        answer=answer,
        source=source,
        status=status,
        evidence=evidence,
        cached=cached,
        request_id=request_id,
    ).as_dict()


def is_open(question):
    normalized = question.lower()
    return any(marker in normalized for marker in COMPLEX)


def sync_answer(question):
    request_id = uuid.uuid4().hex[:12]
    clean_question = clean_input(question)

    _emit(
        request_id,
        "RECEIVED",
        length=len(clean_question),
    )

    if injection_suspected(clean_question):
        _emit(
            request_id,
            "REJECTED",
            reason="prompt_injection",
        )

        return _reply(
            request_id,
            (
                "Não posso atender a esse tipo de instrução. "
                "Faça uma pergunta sobre os serviços da empresa."
            ),
            Source.LOCAL,
            Status.REJECTED,
        )

    direct = local_reply(clean_question)

    if direct:
        _emit(request_id, "ROUTED_LOCAL")

        return _reply(
            request_id,
            direct,
            Source.LOCAL,
        )

    if not is_open(clean_question):
        faq = lookup(clean_question)

        if faq:
            _emit(request_id, "ROUTED_FAQ")

            return {
                **faq,
                "request_id": request_id,
            }

    context = select_context(clean_question)

    if not context:
        _emit(
            request_id,
            "FAILED",
            reason="no_context",
        )

        message = load_business()["conversa"]["informacao_ausente"]

        return _reply(
            request_id,
            message,
            Source.FALLBACK,
            Status.ABSENT,
        )

    cached = get(clean_question)

    if cached:
        _emit(request_id, "CACHE_HIT")

        return {
            **cached,
            "request_id": request_id,
        }

    _emit(
        request_id,
        "CONTEXT_FOUND",
        keys=[item["key"] for item in context],
    )

    try:
        from .gemini import ask

        generated_text = ask(
            clean_question,
            context_text(context),
        )

        if not generated_text:
            raise ValueError("insufficient_context")

        valid, reason = validate_answer(
            clean_question,
            generated_text,
            context,
        )

        if not valid:
            raise ValueError(
                f"answer_validation:{reason}"
            )

        evidence = "\n".join(
            item["text"] for item in context
        )

        result = _reply(
            request_id,
            generated_text,
            Source.GEMINI,
            evidence=evidence,
        )

        put(clean_question, result)

        _emit(
            request_id,
            "DELIVERED",
            source="gemini",
        )

        return result

    except Exception as exc:
        log.exception(
            (
                "GeminiError | request_id=%s | "
                "pergunta=%r | tipo=%s | mensagem=%s"
            ),
            request_id,
            clean_question[:120],
            type(exc).__name__,
            str(exc)[:500],
        )

        _emit(
            request_id,
            "FAILED",
            error=type(exc).__name__,
            reason=str(exc)[:500],
        )

        message = load_business()["conversa"]["indisponibilidade_ia"]

        return _reply(
            request_id,
            message,
            Source.FALLBACK,
            Status.FAILED,
        )


async def answer(question):
    return await asyncio.to_thread(
        sync_answer,
        question,
    )
