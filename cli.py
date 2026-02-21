"""CLI entry point for the Multimodal Pipeline.

Usage examples
--------------
  # Dry-run cost estimate for Channel A (finance), both long + shorts:
  python cli.py --channel A --output both --dry-run

  # Generate Channel B devotional long video (current week's theme):
  python cli.py --channel B --output long

  # Generate 4 shorts from Channel A with a custom theme:
  python cli.py --channel A --output shorts --theme "5 AI tools for passive income"

  # Full weekly run for Channel A (long + 4 shorts):
  python cli.py --channel A --output both --num-shorts 4
"""
import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict

from channel_presets import ChannelPreset, get_preset
from config import Config
from content_cache import ContentCache
from llm_client import call_llm


# ──────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description=(
            "Multimodal content pipeline for faceless YouTube / Instagram channels"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--channel", "-c",
        choices=["A", "B", "a", "b", "finance", "devotion"],
        default="B",
        metavar="CHANNEL",
        help=(
            "Channel preset: A/finance (Finance & AI Tools) or "
            "B/devotion (Devotion & Spirituality). Default: B"
        ),
    )
    parser.add_argument(
        "--output", "-o",
        choices=["long", "shorts", "both"],
        default="both",
        help="Output type: long video, shorts, or both. Default: both",
    )
    parser.add_argument(
        "--cost-tier", "-t",
        choices=["free", "low", "high"],
        default="free",
        help=(
            "Cost tier: free (gTTS + gpt-3.5), low (ElevenLabs basic + gpt-3.5), "
            "high (ElevenLabs professional + gpt-4). Default: free"
        ),
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Estimate costs without making API calls",
    )
    parser.add_argument(
        "--theme",
        default=None,
        help="Specific topic/theme override (uses preset topics by default)",
    )
    parser.add_argument(
        "--week", "-w",
        type=int,
        default=None,
        help="Week number for theme rotation (default: current ISO week)",
    )
    parser.add_argument(
        "--num-shorts",
        type=int,
        default=4,
        choices=range(1, 9),
        metavar="N",
        help="Number of shorts to generate (1-8). Default: 4",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable output caching for this run",
    )
    parser.add_argument(
        "--ideas",
        action="store_true",
        help="Generate a weekly content idea bank (topics, hooks, titles) and exit",
    )
    parser.add_argument(
        "--ideas-count",
        type=int,
        default=12,
        choices=range(6, 31),
        metavar="N",
        help="Number of idea topics to generate in idea mode (6-30). Default: 12",
    )
    return parser


# ──────────────────────────────────────────
# Cost estimation (dry-run)
# ──────────────────────────────────────────

def estimate_costs(
    preset: ChannelPreset,
    output_type: str,
    cost_tier: str,
    num_shorts: int,
) -> Dict[str, Any]:
    """Estimate API costs for a pipeline run without calling any external APIs."""

    # Rough word counts
    long_words = preset.long_video_duration_minutes * 130  # ~130 wpm
    short_words = preset.short_video_duration_seconds * 130 / 60  # ~130 wpm

    # Token estimates (1 token ≈ 0.75 words)
    long_input_tokens = 400
    long_output_tokens = int(long_words / 0.75)
    short_input_tokens = long_output_tokens + 400  # full script + prompt overhead
    short_output_tokens = int(short_words * num_shorts / 0.75) + 200
    title_tokens = 200  # per set

    model = "gpt-4" if cost_tier == "high" else "gpt-3.5-turbo"
    if model == "gpt-4":
        in_price, out_price = 0.03 / 1000, 0.06 / 1000
    else:
        in_price, out_price = 0.0015 / 1000, 0.002 / 1000

    script_cost = (long_input_tokens * in_price) + (long_output_tokens * out_price)
    shorts_cost = (short_input_tokens * in_price) + (short_output_tokens * out_price)
    titles_cost = (title_tokens * in_price) + (title_tokens * out_price)

    tts_chars = long_words * 5  # avg 5 chars/word
    if cost_tier == "free":
        tts_cost, tts_service = 0.0, "gTTS (free)"
    elif cost_tier == "low":
        tts_cost = (tts_chars / 1000) * 0.30  # ElevenLabs: $0.30 per 1 k chars
        tts_service = "ElevenLabs starter"
    else:
        tts_cost = (tts_chars / 1000) * 0.30
        tts_service = "ElevenLabs professional"

    total = (
        script_cost
        + (shorts_cost if output_type != "long" else 0.0)
        + titles_cost
        + tts_cost
    )

    return {
        "model": model,
        "tts_service": tts_service,
        "script_generation": round(script_cost, 4),
        "shorts_extraction": round(shorts_cost, 4) if output_type != "long" else 0.0,
        "titles_thumbnails": round(titles_cost, 4),
        "tts_narration": round(tts_cost, 4),
        "total_usd": round(total, 4),
        "images": "Free (Pexels / Pixabay)",
    }


# ──────────────────────────────────────────
# Pipeline runners
# ──────────────────────────────────────────

def run_pipeline(args: argparse.Namespace) -> None:
    """Run the content pipeline with the given arguments."""
    if args.no_cache:
        Config.ENABLE_CACHE = False

    preset = get_preset(args.channel)
    week = args.week or datetime.now().isocalendar()[1]
    theme = args.theme or preset.topics[week % len(preset.topics)]

    print("=" * 70)
    print(f"🎬  MULTIMODAL PIPELINE – {preset.name.upper()}")
    print("=" * 70)
    print(f"  Channel   : {preset.channel_id} – {preset.name}")
    print(f"  Theme     : {theme}")
    print(f"  Output    : {args.output}")
    print(f"  Cost tier : {args.cost_tier}")
    print(f"  Week      : {week}")

    if args.ideas:
        if not Config.OPENAI_API_KEY and not Config.GOOGLE_API_KEY:
            raise ValueError("Either OPENAI_API_KEY or GOOGLE_API_KEY must be configured")
        _run_idea_engine(preset, theme, week, args)
        return

    if args.dry_run:
        costs = estimate_costs(preset, args.output, args.cost_tier, args.num_shorts)
        print("\n" + "─" * 70)
        print("  DRY RUN – Estimated costs (no API calls made)")
        print("─" * 70)
        print(f"  Model           : {costs['model']}")
        print(f"  TTS Service     : {costs['tts_service']}")
        print(f"  Script gen      : ${costs['script_generation']}")
        print(f"  Shorts extract  : ${costs['shorts_extraction']}")
        print(f"  Titles/Thumbs   : ${costs['titles_thumbnails']}")
        print(f"  TTS narration   : ${costs['tts_narration']}")
        print(f"  Images          : {costs['images']}")
        print("─" * 70)
        print(f"  TOTAL estimate  : ${costs['total_usd']}")
        print("=" * 70)
        return

    Config.validate_config()

    if preset.channel_id == "B":
        _run_devotion_pipeline(preset, theme, week, args)
    else:
        _run_finance_pipeline(preset, theme, week, args)


def _run_devotion_pipeline(
    preset: ChannelPreset,
    theme: str,
    week: int,
    args: argparse.Namespace,
) -> None:
    """Run the devotional pipeline (Channel B)."""
    from shorts_extractor import ShortsExtractor

    cache = ContentCache()

    if args.output in ("long", "both"):
        from devotional_pipeline import DevotionalVideoPipeline

        pipeline = DevotionalVideoPipeline()
        video_path = pipeline.generate_video(theme=theme, week_number=week)
        print(f"\n✓ Long video: {video_path}")

        extractor = ShortsExtractor()
        titles_key = {"type": "titles", "topic": theme, "channel": "B"}
        meta = cache.get(titles_key)
        if meta is None:
            meta = extractor.generate_titles_and_thumbnails(
                theme, preset.system_prompt
            )
            cache.set(titles_key, meta)

        _print_titles_thumbnails(meta)

    if args.output in ("shorts", "both"):
        _generate_shorts_for_preset(preset, theme, args.num_shorts, cache)


def _run_finance_pipeline(
    preset: ChannelPreset,
    theme: str,
    week: int,
    args: argparse.Namespace,
) -> None:
    """Run the finance / AI tools pipeline (Channel A)."""
    import openai
    from shorts_extractor import ShortsExtractor

    cache = ContentCache()
    extractor = ShortsExtractor()
    model = "gpt-4" if args.cost_tier == "high" else "gpt-3.5-turbo"

    # 1. Generate long-form script
    print("\n[1/3] Generating long-form script...")
    script_key = {"type": "long_script", "topic": theme, "channel": "A", "model": model}
    script_data = cache.get(script_key)
    if script_data is None:
        openai.api_key = Config.OPENAI_API_KEY
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": preset.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Create a {preset.long_video_duration_minutes}-minute educational "
                        f"video script about: {theme}\n\n"
                        "Structure it as 5-6 segments. Each segment should have a clear "
                        "heading and engaging content. Include actionable tips and specific "
                        "examples.\n\nFormat:\nSEGMENT 1: [Title]\n[Content]\n\nSEGMENT 2: …"
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=Config.MAX_TOKENS,
        )
        script_data = {
            "full_script": response.choices[0].message.content,
            "theme": theme,
        }
        cache.set(script_key, script_data)

    print(f"✓ Long script generated ({len(script_data['full_script'])} chars)")

    # 2. Titles and thumbnails
    print("\n[2/3] Generating titles and thumbnails...")
    titles_key = {"type": "titles", "topic": theme, "channel": "A"}
    meta = cache.get(titles_key)
    if meta is None:
        meta = extractor.generate_titles_and_thumbnails(theme, preset.system_prompt)
        cache.set(titles_key, meta)
    _print_titles_thumbnails(meta)

    # 3. Shorts
    if args.output in ("shorts", "both"):
        print("\n[3/3] Extracting shorts...")
        _extract_and_print_shorts(
            script_data["full_script"], preset, args.num_shorts, cache
        )

    # Save script to disk
    output_dir = Config.OUTPUT_DIR / f"finance_week{week}"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = theme[:40].replace(" ", "_").replace("/", "-")
    script_file = output_dir / f"{safe_name}_script.txt"
    with open(script_file, "w", encoding="utf-8") as fh:
        fh.write(f"Theme: {theme}\n")
        fh.write("Channel: A (Finance & AI Tools)\n")
        fh.write("=" * 70 + "\n\n")
        fh.write(script_data["full_script"])
    print(f"\n✓ Script saved: {script_file}")


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def _generate_shorts_for_preset(
    preset: ChannelPreset,
    theme: str,
    num_shorts: int,
    cache: ContentCache,
) -> None:
    """Generate a short basis script then extract shorts."""
    import openai

    basis_key = {"type": "short_basis", "topic": theme, "channel": preset.channel_id}
    basis_script = cache.get(basis_key)
    if basis_script is None:
        openai.api_key = Config.OPENAI_API_KEY
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": preset.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Write a 5-minute script about '{theme}' that contains "
                        f"{num_shorts} distinct, quotable moments or insights "
                        "suitable for short-form video clips."
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        basis_script = response.choices[0].message.content
        cache.set(basis_key, basis_script)

    _extract_and_print_shorts(basis_script, preset, num_shorts, cache)


def _extract_and_print_shorts(
    script: str,
    preset: ChannelPreset,
    num_shorts: int,
    cache: ContentCache,
) -> None:
    """Extract shorts from *script* and print them."""
    from shorts_extractor import ShortsExtractor

    extractor = ShortsExtractor()
    shorts_key = {
        "type": "shorts",
        "script_prefix": script[:200],
        "n": num_shorts,
        "channel": preset.channel_id,
    }
    shorts = cache.get(shorts_key)
    if shorts is None:
        shorts = extractor.extract_shorts(script, num_shorts=num_shorts)
        cache.set(shorts_key, shorts)

    print(f"\n✓ Extracted {len(shorts)} shorts:\n")
    for i, short in enumerate(shorts, 1):
        print(f"  SHORT {i}: {short.get('title', 'Untitled')}")
        hook_preview = short.get("hook", "")[:80]
        print(f"  Hook   : {hook_preview}{'…' if len(short.get('hook','')) > 80 else ''}")
        print(f"  Caption: {short.get('caption', '')}")
        print(f"  Tags   : {' '.join(short.get('hashtags', []))}")
        print()


def _print_titles_thumbnails(meta: dict) -> None:
    print("\n📌 Title options:")
    for i, t in enumerate(meta.get("titles", []), 1):
        print(f"   {i}. {t}")
    print("\n🖼️  Thumbnail text options:")
    for i, t in enumerate(meta.get("thumbnails", []), 1):
        print(f"   {i}. {t}")


def _strip_code_fences(text: str) -> str:
    """Remove optional markdown code fences from model output."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()

    # Best-effort JSON extraction if the model adds explanatory text.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def _run_idea_engine(
    preset: ChannelPreset,
    theme: str,
    week: int,
    args: argparse.Namespace,
) -> None:
    """Generate and save a weekly idea bank for the selected channel."""
    cache = ContentCache()
    idea_key = {
        "type": "idea_bank",
        "channel": preset.channel_id,
        "theme": theme,
        "week": week,
        "ideas_count": args.ideas_count,
    }

    ideas = cache.get(idea_key)
    if ideas is None:
        system_prompt = (
            f"{preset.system_prompt}\n\n"
            "You are also a YouTube + Instagram growth strategist. "
            "Return only valid JSON."
        )
        user_prompt = (
            f"Create a weekly content idea bank for channel '{preset.name}' "
            f"(niche: {preset.niche}, tone: {preset.tone}).\n"
            f"Anchor around this seed theme: '{theme}'.\n"
            f"Generate exactly {args.ideas_count} ideas.\n\n"
            "Return strict JSON with this shape:\n"
            "{\n"
            "  \"channel\": string,\n"
            "  \"week\": number,\n"
            "  \"seed_theme\": string,\n"
            "  \"ideas\": [\n"
            "    {\n"
            "      \"topic\": string,\n"
            "      \"long_video_angle\": string,\n"
            "      \"short_hooks\": [string, string, string, string],\n"
            "      \"title_options\": [string, string, string],\n"
            "      \"thumbnail_text\": string,\n"
            "      \"seo_keywords\": [string, string, string, string],\n"
            "      \"neo_banana_polish_prompt\": string\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "- Keep claims realistic and platform-safe.\n"
            "- Avoid repetition across ideas.\n"
            "- Optimize hooks for retention in first 3 seconds.\n"
            "- neo_banana_polish_prompt should describe a short visual style prompt for external app polishing.\n"
        )

        raw = call_llm(
            system=system_prompt,
            user=user_prompt,
            model="gpt-4o-mini",
            max_tokens=min(Config.MAX_TOKENS, 3500),
        )
        parsed = json.loads(_strip_code_fences(raw))
        ideas = parsed
        cache.set(idea_key, ideas)

    output_dir = Config.OUTPUT_DIR / f"ideas_channel{preset.channel_id}_week{week}"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_dir / f"idea_bank_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as fh:
        json.dump(ideas, fh, ensure_ascii=False, indent=2)

    print("\n🧠 IDEA ENGINE OUTPUT")
    print("─" * 70)
    print(f"Saved: {json_file}")

    idea_items = ideas.get("ideas", []) if isinstance(ideas, dict) else []
    for i, item in enumerate(idea_items[:5], 1):
        topic = item.get("topic", "Untitled")
        title1 = (item.get("title_options") or ["-"])[0]
        hook1 = (item.get("short_hooks") or ["-"])[0]
        print(f"{i}. {topic}")
        print(f"   Title: {title1}")
        print(f"   Hook : {hook1}")

    if len(idea_items) > 5:
        print(f"... and {len(idea_items) - 5} more ideas in the JSON file")


# ──────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────

def main() -> None:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        run_pipeline(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"\n❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
