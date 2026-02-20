"""Extract short-form videos from a long-form script.

Input:  a structured script dict (as produced by the pipeline)
Output: a list of short dicts, each ready for a YouTube Short or Instagram Reel.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _split_into_sections(full_script: str) -> List[Dict[str, str]]:
    """
    Parse a long-form script into named sections.

    Expects section headers in the form:
        HOOK:          ...
        PROMISE:       ...
        SECTION N: Title
        RECAP:         ...
        CTA:           ...
    Returns a list of {'title': str, 'content': str} dicts.
    """
    sections: List[Dict[str, str]] = []
    current_title: Optional[str] = None
    current_lines: List[str] = []

    header_re = re.compile(
        r"^(HOOK|PROMISE|RECAP|CTA|SECTION\s+\d+)[\s:]+(.*)$", re.IGNORECASE
    )

    for line in full_script.splitlines():
        stripped = line.strip()
        m = header_re.match(stripped)
        if m:
            if current_title is not None:
                sections.append(
                    {"title": current_title, "content": "\n".join(current_lines).strip()}
                )
            label = m.group(1).upper()
            extra = m.group(2).strip()
            current_title = f"{label}: {extra}" if extra else label
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(stripped)

    if current_title is not None and current_lines:
        sections.append(
            {"title": current_title, "content": "\n".join(current_lines).strip()}
        )

    return sections


def _word_count(text: str) -> int:
    return len(text.split())


def _first_sentence(text: str) -> str:
    """Return the first sentence (up to ~150 chars) of a text block."""
    for punct in (".", "!", "?"):
        idx = text.find(punct)
        if 0 < idx < 200:
            return text[: idx + 1].strip()
    return text[:150].strip()


def _last_sentence(text: str) -> str:
    """Return the last sentence of a text block."""
    for punct in (".", "!", "?"):
        idx = text.rfind(punct)
        if idx > 0:
            # Find start of that sentence
            start = max(text.rfind(".", 0, idx - 1), text.rfind("!", 0, idx - 1),
                        text.rfind("?", 0, idx - 1))
            return text[start + 1: idx + 1].strip()
    return text[-150:].strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_shorts(
    script_data: Dict[str, Any],
    count: int = 4,
    preset=None,
) -> List[Dict[str, Any]]:
    """
    Derive *count* shorts from a long-form script.

    Parameters
    ----------
    script_data:
        Dict produced by the pipeline with at least a ``full_script`` string
        and optionally a ``segments`` list of ``{'title', 'content'}`` dicts.
    count:
        Number of shorts to produce (default 4; max capped at 8).
    preset:
        Optional ``ContentPreset`` object; used to inject shorts_guidance and
        default b-roll keywords.

    Returns
    -------
    List of dicts, each with:
        - ``title``           : Short title derived from source section
        - ``hook``            : First attention-grabbing sentence (≤ 150 chars)
        - ``body``            : Core content, trimmed to ~60 s of narration (~120 words)
        - ``cta``             : Call-to-action closing line
        - ``caption_text``    : On-screen caption text (≤ 60 chars)
        - ``broll_keywords``  : List[str] of suggested b-roll search terms
        - ``source_section``  : Title of the originating section
        - ``estimated_words`` : Word count of hook + body + CTA combined
    """
    count = min(max(1, count), 8)

    # Prefer structured segments; fall back to full_script parsing
    segments: List[Dict[str, str]] = script_data.get("segments") or []
    if not segments:
        segments = _split_into_sections(script_data.get("full_script", ""))

    # Remove purely structural labels (HOOK, PROMISE, RECAP, CTA alone)
    structural_labels = {"HOOK", "PROMISE", "RECAP", "CTA"}
    content_sections = [
        s for s in segments
        if not any(s["title"].upper().startswith(lbl) for lbl in structural_labels)
        and len(s["content"].split()) >= 30
    ]

    # If we don't have enough distinct content sections, fall back to all segments
    if len(content_sections) < count:
        content_sections = [s for s in segments if len(s["content"].split()) >= 20]

    # Clamp count to what is available
    count = min(count, len(content_sections))

    # Spread selection evenly across available sections
    if len(content_sections) > count:
        step = len(content_sections) / count
        indices = [int(i * step) for i in range(count)]
        selected = [content_sections[i] for i in indices]
    else:
        selected = content_sections[:count]

    # Pull b-roll keywords from preset or use defaults
    if preset and hasattr(preset, "default_broll_keywords"):
        broll_pool: List[str] = list(preset.default_broll_keywords)
    else:
        broll_pool = [
            "relevant visual",
            "concept illustration",
            "close-up detail",
            "wide establishing shot",
            "person explaining",
        ]

    shorts: List[Dict[str, Any]] = []
    for i, section in enumerate(selected):
        content = section["content"]
        words = content.split()

        hook = _first_sentence(content)

        # Body: up to ~120 words (roughly 60 s at average narration pace)
        body_words = words[len(hook.split()): len(hook.split()) + 120]
        body = " ".join(body_words).strip()
        if not body:
            body = content[len(hook):].strip()[:500]

        cta = (
            "Follow for more! Like and share if this helped you."
            if not preset or preset.name == "finance_ai_saas"
            else "Share this with someone who needs peace today. 🙏"
        )

        # Caption: first meaningful phrase, ≤ 60 chars
        caption = hook[:57].rstrip() + "..." if len(hook) > 60 else hook

        # Rotate through b-roll pool
        broll = [broll_pool[(i * 2 + j) % len(broll_pool)] for j in range(3)]

        total_words = _word_count(hook) + _word_count(body) + _word_count(cta)

        shorts.append(
            {
                "title": f"Short {i + 1}: {section['title'][:50]}",
                "hook": hook,
                "body": body,
                "cta": cta,
                "caption_text": caption,
                "broll_keywords": broll,
                "source_section": section["title"],
                "estimated_words": total_words,
            }
        )

    return shorts


def shorts_dry_run_estimate(
    script_data: Dict[str, Any],
    count: int = 4,
) -> Dict[str, Any]:
    """
    Return an estimate of shorts extraction without generating content.

    No API calls are made.
    """
    segments = script_data.get("segments") or _split_into_sections(
        script_data.get("full_script", "")
    )
    full_script_word_count = _word_count(script_data.get("full_script", ""))
    return {
        "available_sections": len(segments),
        "requested_shorts": count,
        "shorts_that_will_be_produced": min(count, 8, len(segments)),
        "source_script_words": full_script_word_count,
        "estimated_total_short_words": min(count, 8) * 150,
        "api_calls_required": 0,
    }


class ShortsExtractor:
    """Backward-compatible class wrapper used by the CLI."""

    def extract_shorts(
        self,
        script: str,
        num_shorts: int = 4,
        preset=None,
    ) -> List[Dict[str, Any]]:
        script_data = {"full_script": script, "segments": []}
        extracted = extract_shorts(script_data, count=num_shorts, preset=preset)

        normalized: List[Dict[str, Any]] = []
        for short in extracted:
            title = short.get("title", "")
            source_section = short.get("source_section", "")
            caption_text = short.get("caption_text", "")

            hashtags = ["#shorts", "#ai"]
            if source_section:
                first_word = source_section.split(":", 1)[0].strip().lower()
                if first_word and first_word.isalpha():
                    hashtags.append(f"#{first_word}")

            normalized.append(
                {
                    **short,
                    "title": title,
                    "caption": caption_text,
                    "hashtags": hashtags,
                }
            )

        return normalized

    def generate_titles_and_thumbnails(
        self,
        theme: str,
        system_prompt: str = "",
    ) -> Dict[str, List[str]]:
        theme_clean = (theme or "this topic").strip()
        titles = [
            f"{theme_clean}: 5 Practical Insights",
            f"What Most People Miss About {theme_clean}",
            f"How to Get Results with {theme_clean}",
            f"Beginner's Guide to {theme_clean}",
            f"The Smart Way to Approach {theme_clean}",
        ]
        thumbnails = [
            "DON'T MISS THIS",
            "START HERE",
            "DO THIS NOW",
            "TOP 5 TIPS",
            "GAME CHANGER",
        ]
        return {"titles": titles, "thumbnails": thumbnails}
