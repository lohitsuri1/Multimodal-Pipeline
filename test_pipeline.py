"""Test script to validate the devotional pipeline modules."""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from config import Config
        from script_generator import DevotionalScriptGenerator
        from voice_narrator import VoiceNarrator
        from visual_assets import VisualAssetFetcher
        from music_handler import BackgroundMusicHandler
        from video_compositor import VideoCompositor
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration module."""
    print("\nTesting configuration...")
    try:
        from config import Config
        
        # Ensure directories are created
        Config.ensure_directories()
        
        # Check directories exist
        assert Config.OUTPUT_DIR.exists(), "Output directory not created"
        assert Config.TEMP_DIR.exists(), "Temp directory not created"
        
        # Check settings
        assert Config.VIDEO_DURATION_MINUTES == 30, "Duration should be 30 minutes"
        assert Config.VIDEO_WIDTH == 1920, "Width should be 1920"
        assert Config.VIDEO_HEIGHT == 1080, "Height should be 1080"
        
        print("✓ Configuration working correctly")
        print(f"  Output dir: {Config.OUTPUT_DIR}")
        print(f"  Temp dir: {Config.TEMP_DIR}")
        print(f"  Duration: {Config.VIDEO_DURATION_MINUTES} minutes")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_music_handler():
    """Test music handler module."""
    print("\nTesting music handler...")
    try:
        from music_handler import BackgroundMusicHandler
        
        handler = BackgroundMusicHandler()
        
        # Test getting sources
        sources = handler.get_royalty_free_sources()
        assert len(sources) > 0, "Should have music sources"
        print(f"✓ Found {len(sources)} royalty-free music sources")
        
        # Test requirements
        requirements = handler.get_music_requirements()
        assert 'duration' in requirements, "Should have duration requirement"
        print("✓ Music requirements generated")
        
        # Test instructions
        instructions = handler.setup_music_instructions()
        assert len(instructions) > 0, "Should have instructions"
        print("✓ Music setup instructions generated")
        
        return True
    except Exception as e:
        print(f"✗ Music handler error: {e}")
        return False

def test_visual_queries():
    """Test visual asset queries."""
    print("\nTesting visual asset queries...")
    try:
        from visual_assets import VisualAssetFetcher
        
        fetcher = VisualAssetFetcher()
        queries = fetcher.get_devotional_queries()
        
        assert len(queries) > 0, "Should have devotional queries"
        print(f"✓ Found {len(queries)} devotional search queries")
        print(f"  Examples: {queries[:3]}")
        
        return True
    except Exception as e:
        print(f"✗ Visual assets error: {e}")
        return False

def test_weekly_themes():
    """Test script generator themes."""
    print("\nTesting weekly themes...")
    try:
        from script_generator import DevotionalScriptGenerator
        
        # This will fail without API key, but we can test theme list
        try:
            generator = DevotionalScriptGenerator()
            themes = generator.get_weekly_themes()
            
            assert len(themes) == 12, "Should have 12 weekly themes"
            print(f"✓ Found {len(themes)} weekly themes")
            print(f"  Theme 1: {themes[0]}")
            print(f"  Theme 2: {themes[1]}")
            
            return True
        except ValueError as e:
            if "OpenAI API key" in str(e):
                print("⚠ Skipped (requires OpenAI API key)")
                return True
            raise
            
    except Exception as e:
        print(f"✗ Script generator error: {e}")
        return False

def test_ffmpeg():
    """Test FFmpeg availability."""
    print("\nTesting FFmpeg...")
    try:
        from video_compositor import VideoCompositor
        
        compositor = VideoCompositor()
        has_ffmpeg = compositor.check_ffmpeg()
        
        if has_ffmpeg:
            print("✓ FFmpeg is installed and available")
            return True
        else:
            print("✗ FFmpeg is not installed")
            print("  Install with: sudo apt-get install ffmpeg")
            return False
            
    except Exception as e:
        print(f"✗ FFmpeg check error: {e}")
        return False

def test_presets():
    """Smoke test for content strategy presets."""
    print("\nTesting content strategy presets...")
    try:
        from presets import (
            NICHE_PRESETS, COST_TIERS, OUTPUT_FORMATS,
            get_preset, get_cost_tier, list_niches, list_tiers,
        )

        # All four niches must be present
        for niche in ("finance", "ai_saas", "passive_income", "devotion"):
            assert niche in NICHE_PRESETS, f"Missing niche: {niche}"
            p = get_preset(niche)
            assert "long_form" in p, f"{niche}: missing long_form"
            assert "shorts" in p, f"{niche}: missing shorts"
            assert "themes" in p, f"{niche}: missing themes"
            assert len(p["themes"]) >= 5, f"{niche}: too few themes"
            assert "packaging" in p, f"{niche}: missing packaging"

        # devotion preset preserves the original 12 themes
        devotion_themes = get_preset("devotion")["themes"]
        assert len(devotion_themes) == 12, "Devotion preset should have 12 themes"

        # Cost tiers
        for tier in ("free", "low_cost", "quality"):
            t = get_cost_tier(tier)
            assert "script_model" in t
            assert "max_tokens" in t

        # Output formats
        for fmt in ("long", "shorts", "both"):
            assert fmt in OUTPUT_FORMATS

        # list helpers
        assert set(list_niches()) == set(NICHE_PRESETS.keys())
        assert set(list_tiers()) == set(COST_TIERS.keys())

        print(f"✓ {len(NICHE_PRESETS)} niche presets validated")
        print(f"✓ {len(COST_TIERS)} cost tiers validated")
        return True
    except Exception as e:
        print(f"✗ Presets error: {e}")
        return False


def test_cache_manager():
    """Smoke test for the CacheManager."""
    print("\nTesting cache manager...")
    try:
        import tempfile
        from cache_manager import CacheManager

        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir)

            # JSON round-trip
            inputs = {"niche": "finance", "theme": "budgeting", "model": "gpt-3.5-turbo"}
            value = {"full_script": "Hello world", "sections": []}
            cache.set(inputs, value, namespace="scripts")
            retrieved = cache.get(inputs, namespace="scripts")
            assert retrieved == value, "Cache get/set mismatch"

            # Different inputs → cache miss
            miss = cache.get({"niche": "other"}, namespace="scripts")
            assert miss is None, "Expected cache miss"

            # TTS path helpers
            from pathlib import Path
            tts_path = cache.get_tts_cache_path("test text", {"lang": "en"})
            assert isinstance(tts_path, Path)
            assert tts_path.parent.exists()

            # stats
            stats = cache.stats()
            assert "scripts" in stats

        print("✓ CacheManager get/set/miss/tts-path/stats work correctly")
        return True
    except Exception as e:
        print(f"✗ CacheManager error: {e}")
        return False


def test_cost_estimator():
    """Smoke test for dry-run cost estimation."""
    print("\nTesting cost estimator (dry run)...")
    try:
        from script_generator import ContentScriptGenerator

        for niche in ("finance", "devotion", "passive_income"):
            gen = ContentScriptGenerator(
                niche=niche,
                cost_tier="free",
                output_format="both",
                dry_run=True,
            )
            est = gen.estimate_cost()
            assert "estimated_cost_usd" in est
            assert est["estimated_cost_usd"] >= 0
            assert "model" in est
            assert "estimated_output_tokens" in est

            # generate() in dry_run should also return an estimate (no API call)
            result = gen.generate()
            assert "estimated_cost_usd" in result
            assert result.get("dry_run") is True

        print("✓ Cost estimator returns valid estimates for all niches")
        return True
    except Exception as e:
        print(f"✗ Cost estimator error: {e}")
        return False


def test_cli_dry_run():
    """Smoke test for CLI dry-run mode (no API calls)."""
    print("\nTesting CLI dry-run...")
    try:
        from cli import main as cli_main

        for niche in ("finance", "ai_saas", "passive_income", "devotion"):
            ret = cli_main(["--niche", niche, "--dry-run", "--output-type", "both"])
            assert ret == 0, f"CLI dry-run failed for niche {niche}"

        # --list-niches and --list-tiers should exit 0
        assert cli_main(["--list-niches"]) == 0
        assert cli_main(["--list-tiers"]) == 0

        print("✓ CLI dry-run and listing commands work for all niches")
        return True
    except Exception as e:
        print(f"✗ CLI error: {e}")
        return False


def test_config_guardrails():
    """Smoke test for Config guardrail attributes."""
    print("\nTesting config guardrails...")
    try:
        from config import Config

        guardrails = Config.get_guardrails()
        for key in ("max_tokens", "max_images", "max_tts_chars", "max_retries", "enable_cache"):
            assert key in guardrails, f"Missing guardrail: {key}"

        assert Config.MAX_TOKENS > 0
        assert Config.MAX_IMAGES > 0
        assert Config.MAX_TTS_CHARS > 0
        assert Config.DEFAULT_NICHE in ("devotion", "finance", "ai_saas", "passive_income")
        assert Config.DEFAULT_COST_TIER in ("free", "low_cost", "quality")

        print("✓ Config guardrails present and valid")
        return True
    except Exception as e:
        print(f"✗ Config guardrails error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("🎬  MULTIMODAL CONTENT PIPELINE - MODULE VALIDATION")
    print("=" * 70)

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Config Guardrails", test_config_guardrails),
        ("Music Handler", test_music_handler),
        ("Visual Queries", test_visual_queries),
        ("Weekly Themes", test_weekly_themes),
        ("FFmpeg Check", test_ffmpeg),
        ("Content Presets", test_presets),
        ("Cache Manager", test_cache_manager),
        ("Cost Estimator", test_cost_estimator),
        ("CLI Dry Run", test_cli_dry_run),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✨ All tests passed! Pipeline modules are ready.")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API keys to .env")
        print("  3. Run: python cli.py --niche finance --dry-run")
        print("  4. Run: python devotional_pipeline.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running pipeline.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
