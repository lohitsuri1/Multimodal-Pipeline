"""Content strategy presets for monetizable niches.

Each preset defines long-form script structure, shorts structure,
image search queries, rotating themes, and platform packaging guidance.
"""
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Cost / Quality tiers
# ---------------------------------------------------------------------------
COST_TIERS: Dict[str, Dict[str, Any]] = {
    "free": {
        "description": "100% free – gTTS, Pexels/Pixabay free tier, gpt-3.5-turbo",
        "script_model": "gpt-3.5-turbo",
        "max_tokens": 2000,
        "tts": "gtts",
        "images_source": "pexels_pixabay",
        "max_images": 15,
        "max_tts_chars": 3000,
        "max_retries": 2,
        # Approximate cost per run (USD)
        "estimated_cost_usd": 0.003,
    },
    "low_cost": {
        "description": "Low cost – gpt-4o-mini, optional ElevenLabs starter",
        "script_model": "gpt-4o-mini",
        "max_tokens": 3000,
        "tts": "elevenlabs_or_gtts",
        "images_source": "pexels_pixabay",
        "max_images": 25,
        "max_tts_chars": 5000,
        "max_retries": 3,
        "estimated_cost_usd": 0.02,
    },
    "quality": {
        "description": "Higher quality – gpt-4o, ElevenLabs, Replicate image gen",
        "script_model": "gpt-4o",
        "max_tokens": 4000,
        "tts": "elevenlabs",
        "images_source": "replicate_or_pexels",
        "max_images": 40,
        "max_tts_chars": 10000,
        "max_retries": 3,
        "estimated_cost_usd": 0.20,
    },
}

# ---------------------------------------------------------------------------
# Output format options
# ---------------------------------------------------------------------------
OUTPUT_FORMATS: Dict[str, str] = {
    "long": "Generate one long-form YouTube script only",
    "shorts": "Generate 5–8 short-form scripts derived from the theme",
    "both": "Generate both long-form script and shorts",
}

# ---------------------------------------------------------------------------
# Niche presets
# ---------------------------------------------------------------------------
NICHE_PRESETS: Dict[str, Dict[str, Any]] = {
    "finance": {
        "name": "Finance",
        "description": "Personal finance, investing, and wealth building",
        "long_form": {
            "duration_minutes": 8,
            "structure": {
                "hook": (
                    "Open with a surprising financial statistic or a common money "
                    "mistake the viewer is probably making right now."
                ),
                "promise": (
                    "Promise one specific, actionable financial insight they will "
                    "have by the end of the video."
                ),
                "sections": [
                    "The Problem – why most people get this wrong",
                    "The Strategy – the proven method",
                    "Step-by-Step Breakdown – actionable steps",
                    "Real-World Examples – relatable scenarios",
                    "Common Pitfalls – what to avoid",
                ],
                "cta": (
                    "Ask viewer to subscribe and mention a free resource "
                    "(calculator, checklist, or guide) linked in the description."
                ),
            },
            "system_prompt": (
                "You are a financial educator creating engaging YouTube content "
                "about personal finance, investing, and wealth building. "
                "Your tone is clear, trustworthy, and actionable. "
                "Structure every video with a strong hook, a clear promise, "
                "numbered steps, and a memorable call to action."
            ),
            "shorts_intro_prompt": (
                "Derive {count} short-form video scripts (60 seconds each) "
                "from the following long-form script. Each short must open "
                "with a shocking hook in the first 3 seconds, deliver ONE "
                "key takeaway, and end with a follow CTA."
            ),
        },
        "shorts": {
            "count": 6,
            "max_seconds": 60,
            "structure": {
                "hook": "Shocking stat or contrarian take in the first 3 seconds",
                "body": "One key takeaway, concisely explained (≤45 s)",
                "cta": "Follow for more finance tips",
            },
        },
        "image_queries": [
            "money investing",
            "stock market chart",
            "wealth financial planning",
            "budget spreadsheet",
            "compound interest",
            "real estate investment",
        ],
        "themes": [
            "The 50/30/20 Budgeting Rule Explained",
            "Index Fund Investing for Beginners",
            "How to Build an Emergency Fund Fast",
            "Compound Interest: The 8th Wonder of the World",
            "5 Money Mistakes That Keep You Broke",
            "Passive Income Streams That Actually Work",
            "How to Pay Off Debt Quickly",
            "Retirement Planning at Every Age",
            "Tax-Efficient Investing Strategies",
            "Real Estate vs Stock Market: Which Wins?",
            "Building a 6-Figure Investment Portfolio",
            "The Truth About Credit Scores",
        ],
        "packaging": {
            "title_template": "[Number] Ways to [Outcome] (Without [Pain Point])",
            "thumbnail_text": "SHORT HOOK – 5 WORDS MAX",
            "description_template": (
                "In this video I break down [topic] so you can [benefit]. "
                "No fluff – just actionable steps.\n\n"
                "🔗 Free resource: [LINK]\n"
                "📧 Newsletter: [LINK]\n"
            ),
        },
    },

    "ai_saas": {
        "name": "AI & SaaS Tools",
        "description": "AI tools, SaaS products, and technology for productivity",
        "long_form": {
            "duration_minutes": 8,
            "structure": {
                "hook": (
                    "Demo the most impressive feature of the tool in the very "
                    "first 15 seconds – show, don't tell."
                ),
                "promise": (
                    "Show exactly how much time or money this tool saves "
                    "with a concrete example."
                ),
                "sections": [
                    "What Is It? – 60-second overview",
                    "Key Features Demo – screen recording walkthrough",
                    "Use Cases – 3 real-world scenarios",
                    "Pricing & Alternatives – honest comparison",
                    "Pro Tips – advanced tricks",
                ],
                "cta": (
                    "Direct viewer to try the tool via the affiliate link in the "
                    "description. Include affiliate disclosure."
                ),
            },
            "system_prompt": (
                "You are a tech reviewer creating engaging YouTube content about "
                "AI tools and SaaS products. "
                "Your tone is enthusiastic, honest, and practical. "
                "Focus on real use cases and concrete value. "
                "Structure: impressive demo hook → promise → feature walkthrough "
                "→ pricing → pro tips → CTA."
            ),
            "shorts_intro_prompt": (
                "Derive {count} short-form video scripts (60 seconds each) "
                "from the following long-form script. Each short must open with "
                "a wow-moment or time-saving demo in the first 3 seconds, "
                "highlight ONE killer feature, and end with a 'Full review in bio' CTA."
            ),
        },
        "shorts": {
            "count": 7,
            "max_seconds": 60,
            "structure": {
                "hook": "Wow-moment or time-saving demo in the first 3 seconds",
                "body": "One killer feature or use case (≤45 s)",
                "cta": "Full review in bio",
            },
        },
        "image_queries": [
            "artificial intelligence technology",
            "software productivity",
            "laptop coding automation",
            "data analytics dashboard",
            "machine learning",
            "tech startup workspace",
        ],
        "themes": [
            "Top 5 AI Tools That Will Replace Your Workflow",
            "ChatGPT vs Claude: Which AI Wins?",
            "How to Build a SaaS with No-Code Tools",
            "AI Writing Tools: Honest Review",
            "Automate Your Business with These AI Tools",
            "The Best AI Image Generators Compared",
            "How Founders Use AI to 10x Productivity",
            "AI Tools for Content Creators",
            "Build Your Own AI Chatbot in 10 Minutes",
            "The Future of SaaS: AI-First Products",
            "AI vs Human: Who Writes Better?",
            "5 AI Tools Every Entrepreneur Needs",
        ],
        "packaging": {
            "title_template": "I Tried [Tool] for [Time Period] – Here's What Happened",
            "thumbnail_text": "HONEST REVIEW",
            "description_template": (
                "I tested [tool] for [duration]. Here's my honest take.\n\n"
                "🔗 Try it free: [AFFILIATE LINK] (affiliate – I earn a small "
                "commission at no extra cost to you)\n"
                "📋 Full breakdown: [BLOG POST LINK]\n"
            ),
        },
    },

    "passive_income": {
        "name": "Passive Income",
        "description": "Building passive income streams and financial freedom",
        "long_form": {
            "duration_minutes": 9,
            "structure": {
                "hook": (
                    "Share a real passive income result in the first 10 seconds "
                    "(income screenshot, milestone, or surprising number)."
                ),
                "promise": (
                    "Show the viewer the exact steps to replicate the result, "
                    "with realistic expectations."
                ),
                "sections": [
                    "Why Most People Fail – mindset and common traps",
                    "The Opportunity – why this method works now",
                    "Step-by-Step Setup – detailed walkthrough",
                    "Scaling Up – how to grow from $100 to $1,000/month",
                    "My Results – transparent income report",
                ],
                "cta": (
                    "Offer a free starter resource (template, course, checklist) "
                    "and ask for a subscribe."
                ),
            },
            "system_prompt": (
                "You are a passive income educator creating engaging YouTube content "
                "about building income streams, online business, and financial freedom. "
                "Be specific, actionable, and honest about realistic expectations. "
                "Structure: result hook → promise → why people fail → opportunity → "
                "steps → scale → results → CTA."
            ),
            "shorts_intro_prompt": (
                "Derive {count} short-form video scripts (60 seconds each) "
                "from the following long-form script. Each short must open with "
                "a real income result or surprising fact, deliver ONE actionable "
                "passive income tip, and end with a follow CTA."
            ),
        },
        "shorts": {
            "count": 6,
            "max_seconds": 60,
            "structure": {
                "hook": "Income result or surprising fact in the first 3 seconds",
                "body": "One actionable passive income tip (≤45 s)",
                "cta": "Follow for my passive income journey",
            },
        },
        "image_queries": [
            "passive income online business",
            "laptop freedom lifestyle",
            "entrepreneurship side hustle",
            "financial freedom",
            "digital product creator",
            "remote work",
        ],
        "themes": [
            "7 Passive Income Ideas That Actually Work",
            "How I Made $X with Digital Products",
            "YouTube Monetization: Complete Guide",
            "Affiliate Marketing for Beginners",
            "Print on Demand: Start with $0",
            "Building a Newsletter Business",
            "Stock Photography Income Guide",
            "Creating and Selling Online Courses",
            "Dividend Investing for Passive Income",
            "Dropshipping in 2024: Is It Still Worth It?",
            "The REAL Cost of Financial Freedom",
            "How to Monetize a Blog in 6 Months",
        ],
        "packaging": {
            "title_template": "How I Made $[Amount] with [Method] (Step-by-Step)",
            "thumbnail_text": "$[AMOUNT]/MONTH",
            "description_template": (
                "In this video I walk through exactly how I [result]. "
                "Real numbers, no hype.\n\n"
                "🎁 Free starter kit: [LINK]\n"
                "📊 My income reports: [LINK]\n"
            ),
        },
    },

    "devotion": {
        "name": "Devotion & Spirituality",
        "description": "Radha Krishna devotional content, meditation, and spiritual growth",
        "long_form": {
            "duration_minutes": 30,
            "structure": {
                "hook": (
                    "Open with a peaceful invocation or a profound spiritual "
                    "question that stirs the listener's heart."
                ),
                "promise": (
                    "Offer deep spiritual insight and inner peace through "
                    "Radha Krishna's eternal teachings."
                ),
                "sections": [
                    "Divine Opening – invocation and setting intention",
                    "Story or Teaching – scripture or lila narrative",
                    "Reflection – meaning for daily life",
                    "Meditation Guidance – guided practice",
                    "Closing Blessing – peace and gratitude",
                ],
                "cta": "Subscribe for weekly devotional videos",
            },
            "system_prompt": (
                "You are a spiritual guide creating devotional content about "
                "Radha Krishna. Your content is peaceful, uplifting, and "
                "appropriate for meditation and spiritual reflection."
            ),
            "shorts_intro_prompt": (
                "Derive {count} short devotional clips (60 seconds each) from "
                "the following long-form script. Each clip should open with a "
                "profound spiritual quote or visual moment, share one teaching "
                "or devotional message, and invite the viewer to follow for "
                "daily wisdom."
            ),
        },
        "shorts": {
            "count": 5,
            "max_seconds": 60,
            "structure": {
                "hook": "A profound spiritual quote or invocation",
                "body": "One teaching or devotional message (≤45 s)",
                "cta": "Follow for daily devotional wisdom",
            },
        },
        "image_queries": [
            "lotus flower meditation",
            "temple spiritual sunrise",
            "divine light nature",
            "peaceful river forest",
            "candle prayer devotion",
            "radha krishna artwork",
        ],
        "themes": [
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
        "packaging": {
            "title_template": "[Theme] | Radha Krishna Devotional | [Duration] Minutes",
            "thumbnail_text": "PEACEFUL MEDITATION",
            "description_template": (
                "Join us for [duration] minutes of peaceful devotional meditation "
                "on [theme]. 🙏\n\n"
                "🕉️ Subscribe for weekly spiritual videos\n"
                "📖 Script & resources: [LINK]\n"
            ),
        },
    },
}


def get_preset(niche: str) -> Dict[str, Any]:
    """Return preset for a given niche key (case-insensitive)."""
    key = niche.lower().replace("-", "_")
    if key not in NICHE_PRESETS:
        valid = ", ".join(NICHE_PRESETS.keys())
        raise ValueError(f"Unknown niche '{niche}'. Valid options: {valid}")
    return NICHE_PRESETS[key]


def get_cost_tier(tier: str) -> Dict[str, Any]:
    """Return cost tier configuration."""
    if tier not in COST_TIERS:
        valid = ", ".join(COST_TIERS.keys())
        raise ValueError(f"Unknown cost tier '{tier}'. Valid options: {valid}")
    return COST_TIERS[tier]


def list_niches() -> List[str]:
    """Return list of available niche keys."""
    return list(NICHE_PRESETS.keys())


def list_tiers() -> List[str]:
    """Return list of available cost tier keys."""
    return list(COST_TIERS.keys())
