"""Configurable OpenAI-compatible AI provider.

The AI only writes the caller's line. All stage progression, safety checks
and decision tracking live in the scenario engine, never here.
If the provider is unconfigured or unreachable, callers receive None and
the engine falls back to deterministic lines.
"""

import logging
import os
import re
import ssl

import httpx

logger = logging.getLogger("scamsense.ai")


def _get_ssl_context() -> ssl.SSLContext:
    """Create a trusted SSL context supporting Windows system CA roots and certifi."""
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(cafile=certifi.where())
    except Exception:
        pass
    return ctx


def ai_config() -> dict | None:
    base = os.environ.get("AI_BASE_URL", "").strip().rstrip("/")
    key = os.environ.get("AI_API_KEY", "").strip()
    model = os.environ.get("AI_MODEL", "").strip()
    if not base or not key or not model:
        return None
    return {"base": base, "key": key, "model": model}


def ai_chat(cfg: dict, system: str, user: str, history: list[dict]) -> str | None:
    """One chat completion. Returns the raw content, or None on any failure."""
    try:
        messages = [{"role": "system", "content": system}, *history, {"role": "user", "content": user}]
        ssl_ctx = _get_ssl_context()
        resp = httpx.post(
            f"{cfg['base']}/chat/completions",
            headers={"Authorization": f"Bearer {cfg['key']}"},
            json={
                "model": cfg["model"],
                "messages": messages,
                "max_tokens": 220,
                "temperature": 0.7,
            },
            verify=ssl_ctx,
            timeout=20.0,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return (content or "").strip() or None
    except ssl.SSLError as exc:
        logger.warning("AI provider SSL certificate verification failed: %s", exc)
        return None
    except httpx.TimeoutException as exc:
        logger.warning("AI provider request timed out (timeout: 20.0s): %s", exc)
        return None
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 403:
            logger.warning(
                "AI provider HTTP 403 Forbidden: check API credentials or token quota allowance (%s)",
                exc.response.text[:200],
            )
        elif status == 429:
            logger.warning(
                "AI provider HTTP 429 Rate Limited: rate limit exceeded (%s)",
                exc.response.text[:200],
            )
        else:
            logger.warning("AI provider HTTP status %d error: %s", status, exc.response.text[:200])
        return None
    except httpx.ConnectError as exc:
        logger.warning("AI provider connection error (unreachable host or network drop): %s", exc)
        return None
    except (KeyError, IndexError, ValueError) as exc:
        logger.warning("AI provider returned unexpected or malformed response structure: %s", exc)
        return None
    except Exception as exc:
        logger.warning("AI provider request encountered unexpected error: %s", exc)
        return None


def sanitize_ai_text(text: str) -> str | None:
    """Safety net: strip anything operational out of an AI-generated line."""
    t = re.sub(r"https?://\S+", "", text)
    t = re.sub(r"(?<!\d)\d{5,}(?!\d)", "[withheld in training]", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 400:
        t = t[:397].rsplit(" ", 1)[0] + "…"
    return t or None
