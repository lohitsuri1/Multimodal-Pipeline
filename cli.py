"""CLI entry point for the Multimodal Content Pipeline.

Usage examples:

  # Devotional video (default, free tier)
  python cli.py

  # Finance long-form script, low-cost tier
  python cli.py --niche finance --output-type long --cost-tier low_cost

  # AI/SaaS niche, generate both long + shorts, quality tier
  python cli.py --niche ai_saas --output-type both --cost-tier quality

  # Passive income, dry-run to estimate cost only
  python cli.py --niche passive_income --dry-run

  # Use a custom theme
  python cli.py --niche finance --theme "How to Invest Your First $1,000"

  # List available niches and tiers
  python cli.py --list-niches
  python cli.py --list-tiers
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from config import Config
from presets import (
    COST_TIERS,
    NICHE_PRESETS,
    OUTPUT_FORMATS,
    list_niches,
    list_tiers,
)
from script_generator import ContentScriptGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Multimodal Content Pipeline – generate YouTube scripts and shorts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--niche",
        choices=list_niches(),
        default=Config.DEFAULT_NICHE,
        help=(
            "Content niche preset. "
            f"Default: {Config.DEFAULT_NICHE!r}. "
            "Options: " + ", ".join(list_niches())
        ),
    )
    parser.add_argument(
        "--output-type",
        choices=list(OUTPUT_FORMATS.keys()),
        default="both",
        dest="output_type",
        help=(
            "Output format. "
            "'long' = long-form script only; "
            "'shorts' = shorts/reels only; "
            "'both' = long + shorts (default)."
        ),
    )
    parser.add_argument(
        "--cost-tier",
        choices=list_tiers(),
        default=Config.DEFAULT_COST_TIER,
        dest="cost_tier",
        help=(
            "API cost tier. "
            f"Default: {Config.DEFAULT_COST_TIER!r}. "
            "Options: " + ", ".join(list_tiers())
        ),
    )
    parser.add_argument(
        "--theme",
        default=None,
        help="Custom theme/topic for the script (overrides niche default).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Estimate cost/usage without calling paid APIs.",
    )
    parser.add_argument(
        "--list-niches",
        action="store_true",
        dest="list_niches",
        help="Print available niche presets and exit.",
    )
    parser.add_argument(
        "--list-tiers",
        action="store_true",
        dest="list_tiers",
        help="Print available cost tiers and exit.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        dest="output_dir",
        help="Directory to save generated scripts (default: output_videos/).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print result as JSON instead of human-readable text.",
    )
    return parser


def print_niches():
    print("\nAvailable niche presets:")
    for key, preset in NICHE_PRESETS.items():
        print(f"  {key:<20} {preset['description']}")
    print()


def print_tiers():
    print("\nAvailable cost tiers:")
    for key, tier in COST_TIERS.items():
        est = tier.get("estimated_cost_usd", "?")
        print(
            f"  {key:<12} model={tier['script_model']:<16} "
            f"~${est:.3f}/run   {tier['description']}"
        )
    print(
        "\nDecision table:\n"
        "  free       → 100% free, gTTS + gpt-3.5-turbo. Best for testing.\n"
        "  low_cost   → ~$0.02/run, gpt-4o-mini + optional ElevenLabs starter.\n"
        "               Recommended for regular content production.\n"
        "  quality    → ~$0.20/run, gpt-4o + ElevenLabs + Replicate images.\n"
        "               Use for flagship/hero content only.\n"
    )


def _save_result(result: dict, output_dir: Path, niche: str) -> Path:
    """Save generated script result to a text file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{niche}_script_{ts}.json"
    out_path = output_dir / filename
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)
    return out_path


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_niches:
        print_niches()
        return 0

    if args.list_tiers:
        print_tiers()
        return 0

    # Summarise active configuration
    if not args.json_output:
        print("=" * 70)
        print("🎬  MULTIMODAL CONTENT PIPELINE")
        print("=" * 70)
        print(f"  Niche      : {args.niche}")
        print(f"  Output type: {args.output_type}")
        print(f"  Cost tier  : {args.cost_tier}")
        if args.theme:
            print(f"  Theme      : {args.theme}")
        if args.dry_run:
            print("  Mode       : DRY RUN (no API calls)")
        print()

    generator = ContentScriptGenerator(
        niche=args.niche,
        cost_tier=args.cost_tier,
        output_format=args.output_type,
        dry_run=args.dry_run,
    )

    result = generator.generate(theme=args.theme)

    if args.json_output:
        print(json.dumps(result, indent=2))
        return 0

    # Human-readable output
    if args.dry_run:
        print("📊 DRY RUN – Cost Estimate")
        print(f"   Model            : {result['model']}")
        print(f"   Est. input tokens: {result['estimated_input_tokens']}")
        print(f"   Est. output tokens: {result['estimated_output_tokens']}")
        print(f"   Est. cost (USD)  : ${result['estimated_cost_usd']:.5f}")
        print(f"   Niche            : {result['niche']}")
        print(f"   Output format    : {result['output_format']}")
        return 0

    # Save and summarise
    output_dir = Path(args.output_dir) if args.output_dir else Config.OUTPUT_DIR
    saved_path = _save_result(result, output_dir, args.niche)

    print(f"✓ Script generated – Theme: {result['theme']}")

    if "long_script" in result:
        sections = result["long_script"].get("sections", [])
        print(f"  Long-form  : {len(sections)} sections, "
              f"{result['long_script'].get('duration_minutes', '?')} minutes")
        cached = result["long_script"].get("cached", False)
        if cached:
            print("  (long-form loaded from cache – no API call)")

    if "shorts" in result:
        print(f"  Shorts     : {len(result['shorts'])} scripts")

    pkg = result.get("packaging", {})
    if pkg:
        print(f"\n📦 Packaging guidance:")
        print(f"   Title template  : {pkg.get('title_template', '')}")
        print(f"   Thumbnail text  : {pkg.get('thumbnail_text', '')}")

    if "cost_estimate" in result:
        est = result["cost_estimate"]
        print(f"\n💰 Actual API cost estimate: ~${est.get('estimated_cost_usd', 0):.5f}")

    print(f"\n📁 Saved to: {saved_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
