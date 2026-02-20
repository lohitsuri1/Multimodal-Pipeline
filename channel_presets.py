"""Channel presets for faceless content creation pipelines."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ChannelPreset:
    """Configuration preset for a content channel."""

    channel_id: str
    name: str
    niche: str
    description: str
    long_video_duration_minutes: int
    short_video_duration_seconds: int
    shorts_per_long: int
    topics: List[str]
    visual_queries: List[str]
    tone: str
    system_prompt: str
    short_hook_style: str
    thumbnail_style: str


CHANNEL_A_FINANCE = ChannelPreset(
    channel_id="A",
    name="Finance & AI Tools",
    niche="finance/AI/SaaS/passive income",
    description=(
        "Educational content about finance, AI tools, SaaS businesses, "
        "and passive income streams"
    ),
    long_video_duration_minutes=7,
    short_video_duration_seconds=60,
    shorts_per_long=4,
    topics=[
        "How to earn passive income with AI tools",
        "Best free AI tools to automate your business",
        "SaaS business ideas with $0 startup cost",
        "How to invest $100 per month and grow wealth",
        "Top passive income streams for beginners",
        "AI tools that save 10 hours per week",
        "How to build a digital product business",
        "Dividend investing for beginners",
        "Best side hustles using AI automation",
        "How to monetize a YouTube channel with AI content",
        "Financial freedom roadmap for millennials",
        "Budget investing with index funds",
    ],
    visual_queries=[
        "money finance investment",
        "laptop computer work",
        "artificial intelligence technology",
        "business growth chart",
        "passive income online",
        "modern office workspace",
        "cryptocurrency bitcoin",
        "stock market trading",
        "entrepreneur success",
        "digital marketing",
    ],
    tone="educational, motivational, clear",
    system_prompt=(
        "You are an expert financial educator and AI tools specialist creating "
        "educational content about finance, AI tools, SaaS businesses, and passive income. "
        "Your content is accurate, actionable, and accessible to beginners. "
        "Always include practical steps and avoid get-rich-quick promises."
    ),
    short_hook_style="question or shocking statistic",
    thumbnail_style="bold number or claim (e.g., '$500/month with this AI tool')",
)

CHANNEL_B_DEVOTION = ChannelPreset(
    channel_id="B",
    name="Devotion & Spirituality",
    niche="devotion/spirituality",
    description=(
        "Devotional and spiritual content about Radha Krishna, "
        "meditation, and spiritual growth"
    ),
    long_video_duration_minutes=10,
    short_video_duration_seconds=60,
    shorts_per_long=4,
    topics=[
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
    visual_queries=[
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
    tone="peaceful, reflective, uplifting",
    system_prompt=(
        "You are a spiritual guide creating devotional content about Radha Krishna. "
        "Your content is peaceful, uplifting, and appropriate for meditation "
        "and spiritual reflection."
    ),
    short_hook_style="inspiring quote or devotional question",
    thumbnail_style="spiritual imagery with devotional quote",
)

PRESETS: Dict[str, ChannelPreset] = {
    "A": CHANNEL_A_FINANCE,
    "B": CHANNEL_B_DEVOTION,
    "finance": CHANNEL_A_FINANCE,
    "devotion": CHANNEL_B_DEVOTION,
}


def get_preset(channel: str) -> ChannelPreset:
    """
    Get channel preset by ID or name.

    Args:
        channel: Channel ID ('A', 'B') or name ('finance', 'devotion')

    Returns:
        ChannelPreset for the specified channel

    Raises:
        ValueError: If channel is not found
    """
    key = channel.upper() if len(channel) == 1 else channel.lower()
    if key not in PRESETS:
        raise ValueError(
            f"Unknown channel '{channel}'. Available: {list(PRESETS.keys())}"
        )
    return PRESETS[key]
