"""Script generator for the multimodal content pipeline.

Supports:
- Multiple niche presets (finance, ai_saas, passive_income, devotion)
- Cost tiers (free → gpt-3.5-turbo, low_cost → gpt-4o-mini, quality → gpt-4o)
- File-based caching to avoid re-billing identical requests
- Dry-run mode that estimates token usage without calling the API
- Shorts/reels scripts derived from the long-form script
"""
import openai
from typing import Any, Dict, List, Optional

from cache_manager import CacheManager
from config import Config
from presets import NICHE_PRESETS, COST_TIERS, get_preset, get_cost_tier


class DevotionalScriptGenerator:
    """Generate devotional scripts for Radha Krishna videos (legacy preset)."""

    def __init__(self):
        """Initialize the script generator."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        openai.api_key = Config.OPENAI_API_KEY
        self.duration_minutes = Config.VIDEO_DURATION_MINUTES

    def generate_script(self, theme: str = None) -> Dict[str, Any]:
        """
        Generate a devotional script.

        Args:
            theme: Optional theme for the devotional content

        Returns:
            Dictionary with script segments, timing, and metadata
        """
        prompt = self._create_prompt(theme)

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a spiritual guide creating devotional content about Radha Krishna. Your content is peaceful, uplifting, and appropriate for meditation and spiritual reflection."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )

            script_content = response.choices[0].message.content

            # Parse and structure the script
            return self._structure_script(script_content, theme)

        except Exception as e:
            raise Exception(f"Error generating script: {str(e)}")

    def _create_prompt(self, theme: str = None) -> str:
        """Create the prompt for script generation."""
        base_theme = theme or "divine love and devotion"

        prompt = f"""Create a {self.duration_minutes}-minute devotional meditation script about Radha Krishna.

Theme: {base_theme}

Requirements:
1. The script should be calming, spiritual, and appropriate for meditation
2. Include teachings about devotion, love, and spiritual growth
3. Reference stories or qualities of Radha and Krishna
4. The tone should be peaceful and reflective
5. Divide the content into approximately 6 segments of 5 minutes each
6. Each segment should have a clear theme or teaching
7. Use simple, accessible language
8. The content should be copyright-safe and original

Format your response as follows:
SEGMENT 1: [Title]
[Content for approximately 5 minutes of narration]

SEGMENT 2: [Title]
[Content for approximately 5 minutes of narration]

... continue for all 6 segments

End with a peaceful closing reflection."""

        return prompt

    def _structure_script(self, script_content: str, theme: str) -> Dict:
        """Structure the raw script into segments."""
        segments = []
        current_segment = None
        current_content = []

        for line in script_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check if it's a segment header
            if line.startswith('SEGMENT'):
                if current_segment:
                    # Save previous segment
                    segments.append({
                        'title': current_segment,
                        'content': ' '.join(current_content).strip(),
                        'duration': 300  # 5 minutes per segment
                    })
                    current_content = []

                # Extract title
                if ':' in line:
                    current_segment = line.split(':', 1)[1].strip()
                else:
                    current_segment = f"Part {len(segments) + 1}"
            else:
                current_content.append(line)

        # Add last segment
        if current_segment and current_content:
            segments.append({
                'title': current_segment,
                'content': ' '.join(current_content).strip(),
                'duration': 300
            })

        return {
            'theme': theme or 'divine love and devotion',
            'total_duration': self.duration_minutes * 60,
            'segments': segments,
            'full_script': '\n\n'.join(s['content'] for s in segments)
        }

    def get_weekly_themes(self) -> List[str]:
        """Get suggested themes for weekly videos."""
        return [
            "The Divine Love of Radha and Krishna",
            "Krishna's Teachings on Dharma",
            "Radha's Devotion and Surrender",
            "The Flute of Krishna - Call to the Soul",
            "Rasleela - The Divine Dance",
            "Krishna's Childhood - Innocence and Joy",
            "Radha's Separation - Deepening Devotion",
            "Krishna as the Supreme Friend",
            "The Gopis' Love - Pure Devotion",
            "Krishna's Message in the Bhagavad Gita",
            "Radha's Grace and Compassion",
            "The Yamuna River - Sacred Waters"
        ]


class ContentScriptGenerator:
    """Generate scripts for any niche preset with cost-tier and cache support."""

    # Approximate cost per 1 000 tokens (USD) – conservative estimates.
    # Source: https://openai.com/api/pricing  (last checked January 2025)
    # Update these values if OpenAI changes its pricing.
    _COST_PER_1K_INPUT = {
        "gpt-3.5-turbo": 0.0005,
        "gpt-4o-mini": 0.00015,
        "gpt-4o": 0.005,
        "gpt-4": 0.03,
    }
    _COST_PER_1K_OUTPUT = {
        "gpt-3.5-turbo": 0.0015,
        "gpt-4o-mini": 0.0006,
        "gpt-4o": 0.015,
        "gpt-4": 0.06,
    }

    def __init__(
        self,
        niche: str = "devotion",
        cost_tier: str = "free",
        output_format: str = "both",
        dry_run: bool = False,
    ):
        """
        Initialise the generator.

        Args:
            niche: One of the keys in NICHE_PRESETS (e.g. 'finance').
            cost_tier: 'free', 'low_cost', or 'quality'.
            output_format: 'long', 'shorts', or 'both'.
            dry_run: If True, estimate cost without calling paid APIs.
        """
        self.niche = niche
        self.preset = get_preset(niche)
        self.tier_cfg = get_cost_tier(cost_tier)
        self.output_format = output_format
        self.dry_run = dry_run

        # Effective model: tier value, capped by Config.OPENAI_MODEL if set
        self.model = self.tier_cfg["script_model"]
        self.max_tokens = min(self.tier_cfg["max_tokens"], Config.MAX_TOKENS)

        self.cache: Optional[CacheManager] = (
            CacheManager(str(Config.CACHE_DIR)) if Config.ENABLE_CACHE else None
        )

        if not dry_run:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not configured")
            openai.api_key = Config.OPENAI_API_KEY

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate_cost(self, theme: str = None) -> Dict[str, Any]:
        """Return estimated token usage and cost without calling the API."""
        long_form_cfg = self.preset["long_form"]
        duration = long_form_cfg["duration_minutes"]

        # Rough estimate: ~150 words/minute → ~200 tokens/minute
        est_output_tokens = duration * 200
        est_input_tokens = 300  # system + user prompt overhead

        shorts_tokens = 0
        if self.output_format in ("shorts", "both"):
            count = self.preset["shorts"]["count"]
            shorts_tokens = count * 200 + 150  # each short ~200 output tokens

        total_input = est_input_tokens
        total_output = est_output_tokens + shorts_tokens

        input_cost = (total_input / 1000) * self._COST_PER_1K_INPUT.get(self.model, 0.005)
        output_cost = (total_output / 1000) * self._COST_PER_1K_OUTPUT.get(self.model, 0.015)

        return {
            "model": self.model,
            "estimated_input_tokens": total_input,
            "estimated_output_tokens": total_output,
            "estimated_cost_usd": round(input_cost + output_cost, 5),
            "niche": self.niche,
            "output_format": self.output_format,
            "theme": theme or self.preset["themes"][0],
            "cached": False,
        }

    def generate(self, theme: str = None) -> Dict[str, Any]:
        """
        Generate script content for the configured niche and format.

        Returns a dict with keys: theme, niche, long_script (if requested),
        shorts (list, if requested), packaging, cost_estimate.
        """
        resolved_theme = theme or self.preset["themes"][0]
        cost_estimate = self.estimate_cost(resolved_theme)

        if self.dry_run:
            cost_estimate["dry_run"] = True
            return cost_estimate

        result: Dict[str, Any] = {
            "theme": resolved_theme,
            "niche": self.niche,
            "packaging": self.preset["packaging"],
            "cost_estimate": cost_estimate,
        }

        if self.output_format in ("long", "both"):
            result["long_script"] = self._generate_long_form(resolved_theme)

        if self.output_format in ("shorts", "both"):
            long_text = result.get("long_script", {}).get("full_script", "")
            result["shorts"] = self._generate_shorts(resolved_theme, long_text)

        return result

    def get_themes(self) -> List[str]:
        """Return the rotating theme list for the active niche."""
        return self.preset["themes"]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_long_form(self, theme: str) -> Dict[str, Any]:
        """Generate a long-form script, using cache when available."""
        cache_key = {"type": "long_form", "niche": self.niche, "theme": theme, "model": self.model}

        if self.cache:
            cached = self.cache.get(cache_key, namespace="scripts")
            if cached:
                cached["cached"] = True
                return cached

        long_cfg = self.preset["long_form"]
        system_prompt = long_cfg["system_prompt"]
        user_prompt = self._build_long_form_prompt(theme, long_cfg)

        script_text = self._call_openai(system_prompt, user_prompt)
        structured = self._structure_long_form(script_text, theme, long_cfg)

        if self.cache:
            self.cache.set(cache_key, structured, namespace="scripts")

        return structured

    def _generate_shorts(self, theme: str, long_script: str = "") -> List[Dict[str, Any]]:
        """Generate shorts derived from the long-form script (or theme alone)."""
        count = self.preset["shorts"]["count"]
        cache_key = {
            "type": "shorts",
            "niche": self.niche,
            "theme": theme,
            "count": count,
            "model": self.model,
        }

        if self.cache:
            cached = self.cache.get(cache_key, namespace="scripts")
            if cached:
                for s in cached:
                    s["cached"] = True
                return cached

        long_cfg = self.preset["long_form"]
        system_prompt = long_cfg["system_prompt"]
        intro_template = long_cfg.get(
            "shorts_intro_prompt",
            "Derive {count} short-form video scripts (60 seconds each) from the following content.",
        )
        intro = intro_template.format(count=count)

        source = long_script if long_script else f"Theme: {theme}"
        # Cap source to avoid very large prompts that push past the model's
        # context window; leaving headroom for the structural instructions.
        _MAX_SOURCE_CHARS = 3000
        user_prompt = (
            f"{intro}\n\n"
            f"Niche: {self.preset['name']}\n"
            f"Theme: {theme}\n\n"
            f"SOURCE CONTENT:\n{source[:_MAX_SOURCE_CHARS]}\n\n"
            "Format each short as:\n"
            "SHORT [N]: [Title]\nHOOK: ...\nBODY: ...\nCTA: ...\n"
        )

        raw = self._call_openai(system_prompt, user_prompt)
        shorts = self._parse_shorts(raw, count, theme)

        if self.cache:
            self.cache.set(cache_key, shorts, namespace="scripts")

        return shorts

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Make an OpenAI chat completion call with retry and token guardrails."""
        for attempt in range(max(1, self.tier_cfg.get("max_retries", 2))):
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content
            except openai.RateLimitError:
                if attempt == self.tier_cfg.get("max_retries", 2) - 1:
                    raise
            except Exception:
                raise
        return ""  # unreachable, satisfies type checker

    def _build_long_form_prompt(self, theme: str, long_cfg: dict) -> str:
        """Build the user prompt for a long-form script."""
        structure = long_cfg["structure"]
        duration = long_cfg["duration_minutes"]
        sections = "\n".join(f"  - {s}" for s in structure["sections"])

        return (
            f"Create a {duration}-minute YouTube script about: {theme}\n\n"
            f"Niche: {self.preset['name']}\n\n"
            f"STRUCTURE TO FOLLOW:\n"
            f"HOOK: {structure['hook']}\n"
            f"PROMISE: {structure['promise']}\n"
            f"SECTIONS:\n{sections}\n"
            f"CTA: {structure['cta']}\n\n"
            "Format as:\n"
            "HOOK:\n[hook content]\n\n"
            "PROMISE:\n[promise content]\n\n"
            "SECTION 1: [Title]\n[content]\n\n"
            "SECTION 2: [Title]\n[content]\n\n"
            "...\n\n"
            "CTA:\n[call to action]\n\n"
            "Requirements:\n"
            "- Original, copyright-safe content\n"
            "- Retention-first structure (hook in first 30 seconds)\n"
            "- Conversational, engaging tone\n"
            f"- Approximate read time: {duration} minutes\n"
        )

    def _structure_long_form(self, raw: str, theme: str, long_cfg: dict) -> Dict[str, Any]:
        """Parse raw script text into a structured dict."""
        sections = []
        current_title = None
        current_lines: List[str] = []

        for line in raw.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.upper().startswith("SECTION") and ":" in stripped:
                if current_title:
                    sections.append({
                        "title": current_title,
                        "content": " ".join(current_lines).strip(),
                    })
                current_title = stripped.split(":", 1)[1].strip()
                current_lines = []
            else:
                current_lines.append(stripped)

        if current_title and current_lines:
            sections.append({
                "title": current_title,
                "content": " ".join(current_lines).strip(),
            })

        return {
            "theme": theme,
            "niche": self.niche,
            "duration_minutes": long_cfg["duration_minutes"],
            "sections": sections,
            "full_script": raw,
            "cached": False,
        }

    def _parse_shorts(self, raw: str, expected_count: int, theme: str) -> List[Dict[str, Any]]:
        """Parse raw shorts text into a list of structured dicts."""
        shorts: List[Dict[str, Any]] = []
        current: Dict[str, Any] = {}

        for line in raw.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            upper = stripped.upper()
            if upper.startswith("SHORT") and ":" in stripped:
                if current:
                    shorts.append(current)
                title = stripped.split(":", 1)[1].strip()
                current = {"title": title, "hook": "", "body": "", "cta": "", "cached": False}
            elif upper.startswith("HOOK:"):
                current["hook"] = stripped.split(":", 1)[1].strip()
            elif upper.startswith("BODY:"):
                current["body"] = stripped.split(":", 1)[1].strip()
            elif upper.startswith("CTA:"):
                current["cta"] = stripped.split(":", 1)[1].strip()

        if current:
            shorts.append(current)

        return shorts

