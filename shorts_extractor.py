"""Extract short-form video segments from long-form scripts."""
import re
import openai
from typing import Any, Dict, List

from config import Config


class ShortsExtractor:
    """Extract short segments from long-form scripts for YouTube Shorts / Instagram Reels."""

    # Average spoken words per second (~130 wpm)
    WORDS_PER_SECOND: float = 130 / 60
    # Characters to keep from the long script when building the extraction prompt
    SCRIPT_EXCERPT_CHARS: int = 4000

    def __init__(self):
        """Initialize the shorts extractor."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = Config.OPENAI_API_KEY

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def extract_shorts(
        self,
        long_script: str,
        num_shorts: int = 4,
        max_duration_seconds: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Extract short video segments from a long-form script.

        Args:
            long_script: Full long-form script text.
            num_shorts: Number of shorts to extract (1-8).
            max_duration_seconds: Max duration of each short in seconds.

        Returns:
            List of short dicts with keys: title, hook, script, caption,
            hashtags, format, max_duration_seconds.
        """
        num_shorts = min(max(num_shorts, 1), 8)
        prompt = self._build_extraction_prompt(long_script, num_shorts, max_duration_seconds)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a social media video specialist who extracts highly "
                        "engaging short-form video segments from long-form scripts. "
                        "You optimize for viewer retention and engagement."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=min(Config.MAX_TOKENS, 3000),
        )

        raw = response.choices[0].message.content
        return self._parse_shorts(raw, num_shorts)

    def generate_titles_and_thumbnails(
        self,
        topic: str,
        preset_system_prompt: str,
        num_options: int = 3,
    ) -> Dict[str, List[str]]:
        """
        Generate title and thumbnail text options for a video.

        Args:
            topic: Video topic/theme.
            preset_system_prompt: System prompt for the channel preset.
            num_options: Number of options to generate (default 3).

        Returns:
            Dict with 'titles' and 'thumbnails' lists.
        """
        prompt = (
            f"Generate {num_options} title options and {num_options} thumbnail text "
            f"options for a video about:\n\nTopic: {topic}\n\n"
            "Requirements:\n"
            "- Titles: Engaging, SEO-friendly, under 70 characters, include a benefit "
            "or curiosity gap\n"
            "- Thumbnail text: Short (3-7 words), high-contrast visual text that "
            "complements the title\n\n"
            f"Format your response as:\nTITLES:\n"
            + "\n".join(f"{i}. [Title option {i}]" for i in range(1, num_options + 1))
            + f"\n\nTHUMBNAILS:\n"
            + "\n".join(
                f"{i}. [Thumbnail text option {i}]" for i in range(1, num_options + 1)
            )
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": preset_system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=500,
        )

        raw = response.choices[0].message.content
        return self._parse_titles_thumbnails(raw)

    def estimate_cost(
        self, long_script: str, num_shorts: int = 4
    ) -> Dict[str, Any]:
        """
        Estimate API cost for shorts extraction without making API calls.

        Args:
            long_script: The long-form script.
            num_shorts: Number of shorts to extract.

        Returns:
            Dict with cost breakdown.
        """
        # Rough token estimates: 1 token ~ 4 chars
        input_tokens = len(long_script) // 4 + 500
        output_tokens = num_shorts * 200

        # GPT-3.5-turbo pricing (per 1 k tokens)
        input_cost = (input_tokens / 1000) * 0.0015
        output_cost = (output_tokens / 1000) * 0.002

        return {
            "model": "gpt-3.5-turbo",
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": round(input_cost + output_cost, 4),
        }

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _build_extraction_prompt(
        self, script: str, num_shorts: int, max_seconds: int
    ) -> str:
        max_words = int(max_seconds * self.WORDS_PER_SECOND)
        # Limit input to avoid exceeding context window
        script_excerpt = script[: self.SCRIPT_EXCERPT_CHARS]

        return (
            f"From the following long-form script, extract exactly {num_shorts} "
            "short-form video segments.\n\n"
            "Each short should:\n"
            "- Be highly engaging and retain viewer attention within the first 3 seconds\n"
            f"- Be approximately {max_words} words ({max_seconds} seconds when spoken)\n"
            "- Work as a standalone video clip\n"
            "- Be formatted for vertical 9:16 video (YouTube Shorts / Instagram Reels)\n"
            "- Start with a strong hook\n\n"
            "For each short, provide:\n"
            "SHORT [N]: [Title]\n"
            "HOOK: [First 1-2 sentences that grab attention]\n"
            "SCRIPT: [Full narration script for the short]\n"
            "CAPTION: [Social media caption with emojis, max 150 chars]\n"
            "HASHTAGS: [5-8 relevant hashtags]\n"
            "---\n\n"
            f"LONG-FORM SCRIPT:\n{script_excerpt}\n\n"
            f"Extract {num_shorts} shorts now:"
        )

    def _parse_shorts(self, raw: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse raw LLM output into a list of structured short dicts."""
        shorts = []
        # Split on SHORT N: markers (case-insensitive)
        blocks = re.split(r"(?i)SHORT\s+\d+\s*:", raw)
        # Drop any leading text before the first SHORT marker
        blocks = [b for b in blocks if b.strip()]

        for block in blocks:
            lines = block.strip().split("\n")
            if not lines:
                continue

            title = lines[0].strip()
            hook = ""
            script_parts: List[str] = []
            caption = ""
            hashtags: List[str] = []
            current_section = None

            for line in lines[1:]:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.upper().startswith("HOOK:"):
                    current_section = "hook"
                    hook = stripped[5:].strip()
                elif stripped.upper().startswith("SCRIPT:"):
                    current_section = "script"
                    val = stripped[7:].strip()
                    if val:
                        script_parts = [val]
                    else:
                        script_parts = []
                elif stripped.upper().startswith("CAPTION:"):
                    current_section = "caption"
                    caption = stripped[8:].strip()
                elif stripped.upper().startswith("HASHTAGS:"):
                    current_section = "hashtags"
                    tag_text = stripped[9:].strip()
                    hashtags = [t for t in tag_text.split() if t.startswith("#")]
                elif stripped == "---":
                    break
                else:
                    if current_section == "hook":
                        hook += " " + stripped
                    elif current_section == "script":
                        script_parts.append(stripped)
                    elif current_section == "caption":
                        caption += " " + stripped

            if title or script_parts:
                shorts.append(
                    {
                        "title": title,
                        "hook": hook.strip(),
                        "script": " ".join(script_parts).strip(),
                        "caption": caption.strip(),
                        "hashtags": hashtags,
                        "format": "9:16",
                        "max_duration_seconds": 60,
                    }
                )

        return shorts[:expected_count]

    def _parse_titles_thumbnails(self, raw: str) -> Dict[str, List[str]]:
        """Parse title and thumbnail options from LLM response."""
        titles: List[str] = []
        thumbnails: List[str] = []
        current_section = None

        for line in raw.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            upper = stripped.upper()
            if upper.startswith("TITLES:") or upper == "TITLES":
                current_section = "titles"
            elif upper.startswith("THUMBNAILS:") or upper == "THUMBNAILS":
                current_section = "thumbnails"
            elif stripped[0].isdigit() and ". " in stripped:
                content = stripped.split(". ", 1)[1].strip()
                if current_section == "titles":
                    titles.append(content)
                elif current_section == "thumbnails":
                    thumbnails.append(content)

        return {"titles": titles, "thumbnails": thumbnails}
