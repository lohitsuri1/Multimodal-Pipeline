"""Multi-provider LLM router for the Multimodal Pipeline.

Tries OpenAI first (if ``OPENAI_API_KEY`` is set), then automatically falls
back to Google Gemini (if ``GOOGLE_API_KEY`` is set) on any failure.

Usage
-----
    from llm_client import call_llm

    text = call_llm(system="You are helpful.", user="Tell me a joke.")
"""

import os
from typing import List, Optional

# OpenAI → Gemini model name mapping
_OPENAI_TO_GEMINI = {
    "gpt-3.5-turbo": "gemini-2.0-flash",
    "gpt-4o-mini": "gemini-2.0-flash",
    "gpt-4o": "gemini-1.5-pro",
    "gpt-4": "gemini-1.5-pro",
}


def _call_openai(system: str, user: str, model: str, max_tokens: int) -> str:
    """Call OpenAI chat completions and return the assistant message text."""
    import openai

    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _call_gemini(system: str, user: str, model: str, max_tokens: int) -> str:
    """Call Google Gemini and return the response text."""
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    gemini_model = _OPENAI_TO_GEMINI.get(model, "gemini-2.0-flash")
    gm = genai.GenerativeModel(
        model_name=gemini_model,
        system_instruction=system,
    )
    resp = gm.generate_content(
        user,
        generation_config={"max_output_tokens": max_tokens, "temperature": 0.7},
    )
    return resp.text


def call_llm(
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 2000,
    providers: Optional[List[str]] = None,
) -> str:
    """Try OpenAI first, fall back to Gemini automatically.

    Args:
        system: System prompt.
        user: User prompt.
        model: OpenAI model name (used as-is for OpenAI; mapped to a Gemini
            equivalent when falling back).
        max_tokens: Maximum tokens to generate.
        providers: Ordered list of provider names to try, e.g.
            ``["openai", "gemini"]``.  Defaults to the value of the
            ``LLM_PROVIDER_ORDER`` environment variable, or
            ``["openai", "gemini"]`` if that is not set.

    Returns:
        The assistant/model response as a plain string.

    Raises:
        RuntimeError: If every configured provider fails.
    """
    if providers is None:
        order_env = os.environ.get("LLM_PROVIDER_ORDER", "openai,gemini")
        providers = [p.strip() for p in order_env.split(",") if p.strip()]

    errors: List[str] = []

    for provider in providers:
        if provider == "openai":
            if not os.environ.get("OPENAI_API_KEY"):
                continue
            try:
                return _call_openai(system, user, model, max_tokens)
            except Exception as exc:
                error_type = type(exc).__name__
                print(f"[LLM] OpenAI failed ({error_type}) → falling back to Gemini")
                errors.append(f"openai: {error_type}: {exc}")

        elif provider == "gemini":
            if not os.environ.get("GOOGLE_API_KEY"):
                continue
            try:
                return _call_gemini(system, user, model, max_tokens)
            except Exception as exc:
                error_type = type(exc).__name__
                print(f"[LLM] Gemini failed ({error_type})")
                errors.append(f"gemini: {error_type}: {exc}")

    if errors:
        raise RuntimeError(
            "All LLM providers failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )
    raise RuntimeError(
        "No LLM provider is configured. "
        "Set OPENAI_API_KEY or GOOGLE_API_KEY in your .env file."
    )
