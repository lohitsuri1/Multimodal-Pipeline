"""Content presets for faceless video channels.

Defines two channel presets:
  - finance_ai_saas: Finance, AI tools, SaaS and passive income
  - devotional:      Radha Krishna devotional / spirituality
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ContentPreset:
    """Defines all generation parameters for one channel preset."""

    name: str
    channel_description: str

    # Long-form script generation
    long_form_system_prompt: str          # system role for the LLM
    long_form_user_template: str          # user prompt; use {theme} and {duration_minutes}

    # Shorts extraction guidance (plain-text hint sent to the extractor)
    shorts_guidance: str

    # Packaging: prompts that ask the LLM to return 3 title options + 3 thumbnail texts
    title_prompt_template: str            # use {theme}
    thumbnail_prompt_template: str        # use {theme}

    # Platform cues injected into generated content
    platform_cues: Dict[str, str]         # keys: youtube_long, youtube_shorts, instagram_reels

    # Weekly theme rotation list
    default_themes: List[str]

    # Default b-roll keyword pool
    default_broll_keywords: List[str]


# ---------------------------------------------------------------------------
# Finance / AI / SaaS / passive income preset
# ---------------------------------------------------------------------------

FINANCE_AI_SAAS = ContentPreset(
    name="finance_ai_saas",
    channel_description=(
        "A faceless YouTube/Instagram channel covering AI tools, SaaS products, "
        "passive income strategies, and personal finance — optimised for retention."
    ),
    long_form_system_prompt=(
        "You are an expert content strategist and scriptwriter for a faceless YouTube "
        "channel focused on AI tools, SaaS businesses, and passive income. "
        "Your scripts are engaging, data-driven, and optimised for retention. "
        "Use a conversational yet authoritative tone. "
        "Never use filler phrases; every sentence must earn its place."
    ),
    long_form_user_template=(
        "Write a {duration_minutes}-minute YouTube script on the topic: {theme}\n\n"
        "Use this EXACT retention-first structure:\n"
        "HOOK (0–30 s): Open with a bold claim or surprising stat that stops the scroll.\n"
        "PROMISE (30–60 s): Tell viewers exactly what they will learn and why it matters.\n"
        "SECTION 1: [First major point with proof/example]\n"
        "SECTION 2: [Second major point with proof/example]\n"
        "SECTION 3: [Third major point with proof/example]\n"
        "SECTION 4: [Fourth major point with proof/example] (add more sections as needed)\n"
        "RECAP: Bullet-point summary of the key takeaways (30 s).\n"
        "CTA: Tell viewers to like, subscribe, and watch the next recommended video (20 s).\n\n"
        "Requirements:\n"
        "- Each SECTION header must be on its own line as: SECTION N: [Title]\n"
        "- Aim for ~{words_per_minute} words per minute of narration.\n"
        "- Include at least one concrete case study or real-world example.\n"
        "- Keep language accessible to a general audience (no jargon without explanation).\n"
        "- Content must be 100 %% original and copyright-safe."
    ),
    shorts_guidance=(
        "Extract the most shareable, self-contained insights. Each short should feel like "
        "a mini revelation. Prioritise surprising stats, contrarian takes, and actionable "
        "tips that stand alone without needing the full video context. "
        "Finance / AI / SaaS hooks work best when they open with a dollar figure or "
        "a direct question ('Did you know this FREE tool makes $10k/month?')."
    ),
    title_prompt_template=(
        "Generate exactly 3 compelling YouTube titles for a video about: {theme}\n"
        "Channel niche: AI tools, SaaS, passive income.\n"
        "Rules: under 70 characters, include a power word or number, no clickbait.\n"
        "Return ONLY the 3 titles, one per line, numbered 1–3."
    ),
    thumbnail_prompt_template=(
        "Generate exactly 3 thumbnail text options for a YouTube video about: {theme}\n"
        "Channel niche: AI tools, SaaS, passive income.\n"
        "Rules: max 5 words per option, bold & punchy, conveys urgency or curiosity.\n"
        "Return ONLY the 3 options, one per line, numbered 1–3."
    ),
    platform_cues={
        "youtube_long": (
            "16:9 widescreen. Use chapter markers matching each SECTION. "
            "End-screen card at final 20 s. Closed-caption SRT recommended."
        ),
        "youtube_shorts": (
            "9:16 vertical. Max 60 s. First 3 s must show the hook on-screen as bold text. "
            "Add captions burned-in or as SRT. No intro music longer than 1 s."
        ),
        "instagram_reels": (
            "9:16 vertical. Max 90 s. Hook in first 2 s. "
            "Add on-screen captions at bottom third. "
            "Trending audio optional but boosts reach. Safe zone: keep text within centre 80%%."
        ),
    },
    default_themes=[
        "5 AI Tools That Replace a Full Marketing Team",
        "How to Build a $5k/Month SaaS With No Code",
        "Passive Income With AI: 7 Real Strategies",
        "ChatGPT Side Hustles That Actually Work in 2025",
        "Best Free AI Tools for Entrepreneurs",
        "How to Automate Your Business With AI Agents",
        "Top SaaS Trends to Watch This Year",
        "Building a Personal Finance Dashboard With AI",
        "AI for Investing: What You Need to Know",
        "Productize Your Skills: Turning Expertise Into SaaS",
        "Zero-Budget Marketing With AI Tools",
        "How to Validate a SaaS Idea in 24 Hours",
    ],
    default_broll_keywords=[
        "laptop screen code",
        "dashboard analytics",
        "money passive income",
        "AI robot technology",
        "smartphone app startup",
        "office entrepreneur",
        "chart growth business",
        "coffee work remote",
        "dollar bills finance",
        "server cloud computing",
    ],
)


# ---------------------------------------------------------------------------
# Devotional / spirituality preset (preserves existing devotional behaviour)
# ---------------------------------------------------------------------------

DEVOTIONAL = ContentPreset(
    name="devotional",
    channel_description=(
        "A faceless YouTube/Instagram channel featuring Radha Krishna devotional content — "
        "peaceful meditation scripts, spiritual teachings, and bhakti reflections."
    ),
    long_form_system_prompt=(
        "You are a spiritual guide creating devotional content about Radha Krishna. "
        "Your content is peaceful, uplifting, and appropriate for meditation and "
        "spiritual reflection."
    ),
    long_form_user_template=(
        "Create a {duration_minutes}-minute devotional meditation script about Radha Krishna.\n\n"
        "Theme: {theme}\n\n"
        "Use this EXACT retention-first structure:\n"
        "HOOK: Open with a beautiful verse, story, or question that invites stillness.\n"
        "PROMISE: Briefly tell listeners what spiritual insight they will receive today.\n"
        "SECTION 1: [Opening invocation / setting the devotional mood]\n"
        "SECTION 2: [Core teaching or story related to the theme]\n"
        "SECTION 3: [Deepening reflection — personal application]\n"
        "SECTION 4: [Mantra, kirtan suggestion, or guided visualisation]\n"
        "RECAP: Summarise the main spiritual insight in 3–5 sentences.\n"
        "CTA: Invite listeners to share the video, subscribe, and join the community.\n\n"
        "Requirements:\n"
        "- Each SECTION header on its own line: SECTION N: [Title]\n"
        "- Calming, reverent tone throughout.\n"
        "- Include references to Radha, Krishna, or Bhagavad Gita where natural.\n"
        "- Approximately {words_per_minute} words per minute.\n"
        "- 100 %% original and copyright-safe."
    ),
    shorts_guidance=(
        "Extract moments of pure devotion: a beautiful verse, a moving story fragment, "
        "or a simple spiritual practice. Each short should create a feeling of peace "
        "or inspiration within 30–60 seconds. Devotional hooks work best as a "
        "gentle question or a surprising spiritual fact."
    ),
    title_prompt_template=(
        "Generate exactly 3 YouTube titles for a devotional video about: {theme}\n"
        "Channel niche: Radha Krishna devotion, spirituality, meditation.\n"
        "Rules: under 70 characters, evoke peace/devotion, no sensational claims.\n"
        "Return ONLY the 3 titles, one per line, numbered 1–3."
    ),
    thumbnail_prompt_template=(
        "Generate exactly 3 thumbnail text options for a devotional video about: {theme}\n"
        "Channel niche: Radha Krishna devotion, spirituality, meditation.\n"
        "Rules: max 5 words, peaceful and inviting, suitable for spiritual audience.\n"
        "Return ONLY the 3 options, one per line, numbered 1–3."
    ),
    platform_cues={
        "youtube_long": (
            "16:9 widescreen. Gentle Ken-Burns effect on images. "
            "Soft background music at 10–20 %% volume. "
            "End-screen card at final 20 s. Timestamps for each section recommended."
        ),
        "youtube_shorts": (
            "9:16 vertical. Max 60 s. Show hook text on screen for first 3 s. "
            "Soft ambient audio. Burned-in Sanskrit or translated verse as caption."
        ),
        "instagram_reels": (
            "9:16 vertical. Max 90 s. Calming transition between visuals. "
            "On-screen captions for accessibility. "
            "Safe zone: keep text within centre 80 %% of frame."
        ),
    },
    default_themes=[
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
        "The Yamuna River - Sacred Waters",
    ],
    default_broll_keywords=[
        "hindu temple",
        "lotus flower",
        "diya lamp",
        "peacock feather",
        "sunrise spiritual",
        "meditation nature",
        "indian spiritual",
        "sacred geometry",
        "mandala art",
        "spiritual light",
    ],
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

PRESETS: Dict[str, ContentPreset] = {
    "finance_ai_saas": FINANCE_AI_SAAS,
    "devotional": DEVOTIONAL,
}


def get_preset(name: str) -> ContentPreset:
    """Return a preset by name, raising ValueError if not found."""
    if name not in PRESETS:
        raise ValueError(
            f"Unknown preset '{name}'. Available presets: {list(PRESETS.keys())}"
        )
    return PRESETS[name]
