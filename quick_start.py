#!/usr/bin/env python3
"""CLI entry point for the Multimodal Pipeline.

Usage
-----
    python quick_start.py \\
        --preset finance_ai_saas \\
        --output both \\
        --tier free \\
        --shorts-count 4 \\
        --theme "5 AI Tools That Replace a Full Marketing Team"

    # Estimate usage without calling paid APIs
    python quick_start.py --preset devotional --output both --dry-run

Flags
-----
    --preset    finance_ai_saas | devotional  (default: devotional)
    --output    long | shorts | both          (default: both)
    --tier      free | low_cost | hq          (default: free)
    --theme     Custom topic/theme string     (default: auto-rotate from preset)
    --shorts-count  1-8                       (default: 4)
    --dry-run   Estimate calls/tokens, no paid API usage
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from config import Config
from content_presets import get_preset
from pipeline_cache import get_cached, make_cache_key, set_cached
from shorts_extractor import extract_shorts, shorts_dry_run_estimate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORDS_PER_MINUTE = {"free": 130, "low_cost": 140, "hq": 150}


def _openai_generate(system: str, user: str, max_tokens: int = None) -> str:
    """Thin wrapper around OpenAI chat completions."""
    import openai

    openai.api_key = Config.OPENAI_API_KEY
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=max_tokens or Config.MAX_TOKENS_PER_CALL,
    )
    return response.choices[0].message.content


def _parse_numbered_list(text: str, limit: int = 3) -> list[str]:
    items = []
    for line in text.splitlines():
        line = line.strip().lstrip("0123456789.-) ")
        if line:
            items.append(line)
    return items[:limit]


def _select_theme(preset, theme_arg: str | None) -> str:
    if theme_arg:
        return theme_arg
    week = datetime.now().isocalendar()[1]
    themes = preset.default_themes
    return themes[week % len(themes)]


def _save_output(data: dict, preset_name: str, output_type: str) -> Path:
    """Save generation output as JSON and return the path."""
    Config.ensure_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{preset_name}_{output_type}_{timestamp}.json"
    out_path = Config.OUTPUT_DIR / filename
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return out_path


# ---------------------------------------------------------------------------
# Core generation logic
# ---------------------------------------------------------------------------

def run_dry_run(args: argparse.Namespace, preset) -> None:
    """Print a usage estimate without calling any paid APIs."""
    theme = _select_theme(preset, args.theme)
    wpm = WORDS_PER_MINUTE.get(args.tier, 130)
    duration = Config.VIDEO_DURATION_MINUTES

    print("\n" + "=" * 65)
    print("DRY-RUN ESTIMATE (no paid API calls made)")
    print("=" * 65)
    print(f"  Preset  : {args.preset}")
    print(f"  Theme   : {theme}")
    print(f"  Output  : {args.output}")
    print(f"  Tier    : {args.tier}")
    print()

    api_calls = 0

    if args.output in ("long", "both"):
        target_words = duration * wpm
        approx_tokens = int(target_words * 1.4)
        print(f"  Long script     : ~{target_words} words  →  ~{approx_tokens} tokens  (1 API call)")
        print(f"  Titles          : ~100 tokens  (1 API call)")
        print(f"  Thumbnail texts : ~75 tokens   (1 API call)")
        api_calls += 3

    if args.output in ("shorts", "both"):
        est = shorts_dry_run_estimate({"full_script": "", "segments": []}, count=args.shorts_count)
        print(f"  Shorts          : {est['shorts_that_will_be_produced']} shorts  "
              f"(0 extra API calls — extracted from long script)")

    print()
    print(f"  Total estimated API calls : {api_calls}")
    print(f"  Caching                   : enabled — re-runs with same inputs = 0 calls")
    print("=" * 65 + "\n")


def generate_long(args: argparse.Namespace, preset, theme: str) -> dict:
    """Generate long-form script + packaging. Returns result dict."""
    wpm = WORDS_PER_MINUTE.get(args.tier, 130)
    duration = Config.VIDEO_DURATION_MINUTES

    cache_key = make_cache_key(
        preset=args.preset, theme=theme, output="long",
        tier=args.tier, duration=duration,
    )
    cached = get_cached(cache_key, "scripts")
    if cached:
        print("  ✓ Long script loaded from cache (no API call)")
        return cached

    print("  Calling OpenAI for long-form script…")
    user_prompt = preset.long_form_user_template.format(
        theme=theme,
        duration_minutes=duration,
        words_per_minute=wpm,
    )
    script_text = _openai_generate(
        preset.long_form_system_prompt, user_prompt,
        max_tokens=Config.MAX_TOKENS_PER_CALL,
    )

    print("  Generating titles…")
    title_raw = _openai_generate(
        "You are a YouTube title specialist.",
        preset.title_prompt_template.format(theme=theme),
        max_tokens=200,
    )
    titles = _parse_numbered_list(title_raw)

    print("  Generating thumbnail texts…")
    thumb_raw = _openai_generate(
        "You are a YouTube thumbnail copy specialist.",
        preset.thumbnail_prompt_template.format(theme=theme),
        max_tokens=150,
    )
    thumbnail_texts = _parse_numbered_list(thumb_raw)

    result = {
        "preset": args.preset,
        "theme": theme,
        "tier": args.tier,
        "long_script": script_text,
        "titles": titles,
        "thumbnail_texts": thumbnail_texts,
        "platform_cues": preset.platform_cues,
    }
    set_cached(cache_key, result, "scripts")
    return result


def generate_shorts(args: argparse.Namespace, preset, theme: str, script_data: dict) -> list:
    """Extract shorts from a long script. Returns list of short dicts."""
    import hashlib
    script_text = script_data.get("long_script", "")
    stable_hash = hashlib.sha256(script_text.encode()).hexdigest()[:16]
    cache_key = make_cache_key(
        preset=args.preset, theme=theme, output="shorts",
        tier=args.tier, shorts_count=args.shorts_count,
        script_hash=stable_hash,
    )
    cached = get_cached(cache_key, "shorts")
    if cached:
        print("  ✓ Shorts loaded from cache (no API call)")
        return cached

    print(f"  Extracting {args.shorts_count} shorts from long script…")
    shorts = extract_shorts(script_data, count=args.shorts_count, preset=preset)
    set_cached(cache_key, shorts, "shorts")
    return shorts


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_long_result(result: dict) -> None:
    theme = result.get("theme", "")
    print("\n" + "─" * 65)
    print(f"📝  LONG-FORM SCRIPT  |  Theme: {theme}")
    print("─" * 65)

    script = result.get("long_script", "")
    # Print first 600 chars as preview
    preview = script[:600].strip()
    if len(script) > 600:
        preview += "\n  … [truncated — full script saved to file]"
    print(preview)

    print("\n📦  PACKAGING")
    print("  Titles:")
    for t in result.get("titles", []):
        print(f"    • {t}")
    print("  Thumbnail texts:")
    for t in result.get("thumbnail_texts", []):
        print(f"    • {t}")

    print("\n📺  PLATFORM CUES")
    for platform, cue in result.get("platform_cues", {}).items():
        print(f"  [{platform}] {cue}")


def _print_shorts(shorts: list) -> None:
    print("\n" + "─" * 65)
    print(f"✂️   SHORTS  ({len(shorts)} extracted)")
    print("─" * 65)
    for i, s in enumerate(shorts, 1):
        print(f"\n  Short {i}: {s['title']}")
        print(f"  Hook   : {s['hook']}")
        print(f"  CTA    : {s['cta']}")
        print(f"  Caption: {s['caption_text']}")
        print(f"  B-roll : {', '.join(s['broll_keywords'])}")
        print(f"  ~{s['estimated_words']} words")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multimodal Pipeline CLI — generate faceless video content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--preset",
        choices=["finance_ai_saas", "devotional"],
        default="devotional",
        help="Content channel preset (default: devotional)",
    )
    parser.add_argument(
        "--output",
        choices=["long", "shorts", "both"],
        default="both",
        help="What to generate (default: both)",
    )
    parser.add_argument(
        "--tier",
        choices=["free", "low_cost", "hq"],
        default="free",
        help="Quality / cost tier (default: free)",
    )
    parser.add_argument(
        "--theme",
        default=None,
        help="Topic or theme for this video (default: auto-rotate from preset)",
    )
    parser.add_argument(
        "--shorts-count",
        type=int,
        default=4,
        metavar="N",
        help="Number of shorts to extract (1–8, default: 4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Estimate usage without making paid API calls",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.shorts_count = max(1, min(8, args.shorts_count))

    Config.ensure_directories()

    try:
        preset = get_preset(args.preset)
    except ValueError as exc:
        print(f"❌  {exc}", file=sys.stderr)
        return 1

    theme = _select_theme(preset, args.theme)

    print("=" * 65)
    print("🎬  MULTIMODAL PIPELINE")
    print("=" * 65)
    print(f"  Preset : {args.preset}")
    print(f"  Theme  : {theme}")
    print(f"  Output : {args.output}")
    print(f"  Tier   : {args.tier}")
    print(f"  Shorts : {args.shorts_count}")
    print(f"  Dry run: {args.dry_run}")
    print()

    # ---- Dry-run short-circuit ------------------------------------------
    if args.dry_run:
        run_dry_run(args, preset)
        return 0

    # ---- Live generation ------------------------------------------------
    if not Config.OPENAI_API_KEY:
        print(
            "❌  OPENAI_API_KEY is not set.\n"
            "   Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        return 1

    output_data: dict = {
        "preset": args.preset,
        "theme": theme,
        "tier": args.tier,
        "generated_at": datetime.now().isoformat(),
    }

    long_result: dict = {}

    # ---- Long script --------------------------------------------------------
    if args.output in ("long", "both"):
        print("[1] Generating long-form script + packaging…")
        try:
            long_result = generate_long(args, preset, theme)
        except Exception as exc:
            print(f"❌  Script generation failed: {exc}", file=sys.stderr)
            return 1
        output_data.update(long_result)
        _print_long_result(long_result)

    # ---- Shorts extraction --------------------------------------------------
    if args.output in ("shorts", "both"):
        if args.output == "shorts" and not long_result:
            print(
                "⚠️  Shorts extraction requires a long script. Switching output to 'both'.",
            )
            args.output = "both"
            print("[1] Generating long-form script first…")
            try:
                long_result = generate_long(args, preset, theme)
            except Exception as exc:
                print(f"❌  Script generation failed: {exc}", file=sys.stderr)
                return 1
            output_data.update(long_result)
            _print_long_result(long_result)

        print(f"\n[2] Extracting {args.shorts_count} shorts…")
        try:
            shorts = generate_shorts(args, preset, theme, long_result)
        except Exception as exc:
            print(f"❌  Shorts extraction failed: {exc}", file=sys.stderr)
            return 1
        output_data["shorts"] = shorts
        _print_shorts(shorts)

    # ---- Save to file -------------------------------------------------------
    output_type = args.output
    saved_path = _save_output(output_data, args.preset, output_type)
    print(f"\n✅  Output saved to: {saved_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
