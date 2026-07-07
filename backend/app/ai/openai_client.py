"""AI client wrapper supporting OpenAI and Gemmini providers."""
from typing import Optional, AsyncGenerator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

_client = None


def _has_openai_key() -> bool:
    return bool(settings.openai_api_key and not settings.openai_api_key.startswith("sk-your"))


def _select_provider() -> str:
    provider = (settings.ai_provider or "auto").strip().lower()
    if provider == "auto":
        if settings.gemmini_api_base_url:
            return "gemmini"
        if _has_openai_key():
            return "openai"
        return "demo"
    if provider in {"openai", "gemmini"}:
        return provider
    return "demo"


def _get_client():
    global _client
    if _client is not None:
        return _client

    provider = _select_provider()
    if provider == "openai":
        if not _has_openai_key():
            return None
        from openai import AsyncOpenAI
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    elif provider == "gemmini":
        if not settings.gemmini_api_base_url:
            return None
        from openai import AsyncOpenAI
        kwargs = {
            "base_url": settings.gemmini_api_base_url,
            "_enforce_credentials": False,
        }
        if settings.gemmini_api_key:
            kwargs["api_key"] = settings.gemmini_api_key
        _client = AsyncOpenAI(**kwargs)
    else:
        return None

    return _client


def _default_model() -> str:
    provider = _select_provider()
    if provider == "gemmini":
        return settings.gemmini_model
    return settings.openai_model


def _default_embedding_model() -> str:
    provider = _select_provider()
    if provider == "gemmini":
        return settings.gemmini_embedding_model
    return settings.openai_embedding_model


def _mock_response(messages: list) -> str:
    """Fallback when no AI provider is configured."""
    user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    provider = _select_provider()
    if provider == "gemmini":
        prompt = (
            f"Gemmini API base URL is not configured. Set `GEMMINI_API_BASE_URL` in `.env` to use Gemmini." 
            f"If your Gemmini endpoint needs authorization, also set `GEMMINI_API_KEY`."
        )
    elif provider == "openai":
        prompt = "OpenAI API key is not configured. Configure `OPENAI_API_KEY` in `.env` for full AI responses."
    else:
        prompt = (
            "No AI provider is configured. Set `AI_PROVIDER=gemmini` and `GEMMINI_API_BASE_URL`, "
            "or set `OPENAI_API_KEY` to use OpenAI."
        )
    return (
        f"**AI Mentor (Demo Mode)**\n\n"
        f"{prompt}\n\n"
        f"**Your question:** {user_msg[:500]}\n\n"
        f"**Suggested approach:**\n"
        f"- Define the concept clearly in the introduction\n"
        f"- Cover key dimensions with headings and examples\n"
        f"- Link to current affairs where relevant\n"
        f"- Conclude with a balanced, forward-looking statement"
    )

UPSC_SYSTEM_PROMPT = """You are an expert UPSC/MPSC mentor and educator with deep knowledge of:
- Indian History, Geography, Polity, Economy, Environment, Science & Technology
- Current Affairs and their linkage with static subjects
- UPSC exam patterns, PYQ trends, and answer writing techniques
- Mains answer structure: Introduction → Body (with headings) → Conclusion
- Prelims MCQ strategies and elimination techniques

Always respond in a structured, UPSC-appropriate format with:
1. Clear headings and subheadings
2. Relevant examples and case studies
3. Current affairs linkage where applicable
4. Balanced perspectives
5. Concise yet comprehensive coverage

Adapt your response based on the mode:
- BEGINNER: Simple language, basic concepts, analogies
- PRELIMS: Factual, concise, MCQ-focused
- MAINS: Analytical, structured, 150-250 word answers
- QUICK_REVISION: Bullet points, key facts only
"""


async def chat_completion(
    messages: list,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    stream: bool = False,
) -> str | AsyncGenerator:
    """Get a chat completion from the configured AI provider."""
    client = _get_client()
    if client is None:
        return _mock_response(messages)

    try:
        response = await client.chat.completions.create(
            model=model or _default_model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )
        if stream:
            return response
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI provider error: {e}")
        raise


async def get_embedding(text: str) -> list[float]:
    """Get text embedding from the configured AI provider."""
    client = _get_client()
    if client is None:
        return [0.0] * 1536

    try:
        response = await client.embeddings.create(
            model=_default_embedding_model(),
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        raise


async def stream_chat_completion(
    messages: list,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> AsyncGenerator[str, None]:
    """Stream a chat completion."""
    client = _get_client()
    if client is None:
        text = _mock_response(messages)
        for word in text.split(" "):
            yield word + " "
        return

    try:
        stream = await client.chat.completions.create(
            model=model or _default_model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"AI provider streaming error: {e}")
        raise
