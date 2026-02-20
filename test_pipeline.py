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
        from channel_presets import get_preset, CHANNEL_A_FINANCE, CHANNEL_B_DEVOTION
        from shorts_extractor import ShortsExtractor
        from content_cache import ContentCache
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

        # New cost/safety controls
        assert Config.MAX_TOKENS > 0, "MAX_TOKENS should be positive"
        assert Config.MAX_RETRIES > 0, "MAX_RETRIES should be positive"
        assert Config.MAX_IMAGES > 0, "MAX_IMAGES should be positive"
        assert Config.MAX_TTS_CHARS > 0, "MAX_TTS_CHARS should be positive"
        assert isinstance(Config.ENABLE_CACHE, bool), "ENABLE_CACHE should be bool"
        assert Config.RATE_LIMIT_PER_MINUTE > 0, "RATE_LIMIT_PER_MINUTE should be positive"
        
        print("✓ Configuration working correctly")
        print(f"  Output dir: {Config.OUTPUT_DIR}")
        print(f"  Temp dir: {Config.TEMP_DIR}")
        print(f"  Duration: {Config.VIDEO_DURATION_MINUTES} minutes")
        print(f"  MAX_TOKENS: {Config.MAX_TOKENS}")
        print(f"  ENABLE_CACHE: {Config.ENABLE_CACHE}")
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


def test_channel_presets():
    """Test channel preset module."""
    print("\nTesting channel presets...")
    try:
        from channel_presets import (
            CHANNEL_A_FINANCE,
            CHANNEL_B_DEVOTION,
            get_preset,
        )

        # Check Channel A
        assert CHANNEL_A_FINANCE.channel_id == "A"
        assert len(CHANNEL_A_FINANCE.topics) >= 10, "Channel A should have topics"
        assert len(CHANNEL_A_FINANCE.visual_queries) > 0, "Channel A should have visual queries"
        assert CHANNEL_A_FINANCE.long_video_duration_minutes > 0
        assert CHANNEL_A_FINANCE.shorts_per_long > 0

        # Check Channel B
        assert CHANNEL_B_DEVOTION.channel_id == "B"
        assert len(CHANNEL_B_DEVOTION.topics) >= 10, "Channel B should have topics"

        # Check get_preset helper
        assert get_preset("A").channel_id == "A"
        assert get_preset("B").channel_id == "B"
        assert get_preset("finance").channel_id == "A"
        assert get_preset("devotion").channel_id == "B"
        assert get_preset("a").channel_id == "A"

        try:
            get_preset("unknown")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

        print(f"✓ Channel A topics: {len(CHANNEL_A_FINANCE.topics)}")
        print(f"✓ Channel B topics: {len(CHANNEL_B_DEVOTION.topics)}")
        print("✓ get_preset() lookups work correctly")
        return True
    except Exception as e:
        print(f"✗ Channel presets error: {e}")
        return False


def test_content_cache():
    """Test file-based content cache."""
    print("\nTesting content cache...")
    import tempfile
    from pathlib import Path

    try:
        from content_cache import ContentCache
        from config import Config

        with tempfile.TemporaryDirectory() as tmp:
            cache = ContentCache(cache_dir=Path(tmp))
            cache.enabled = True  # force-enable regardless of env

            key = {"type": "test", "value": "hello"}

            # Cache miss
            assert cache.get(key) is None, "Should be cache miss initially"

            # Store and retrieve
            cache.set(key, {"data": 42})
            result = cache.get(key)
            assert result == {"data": 42}, f"Expected {{data: 42}}, got {result}"

            # Identical key → same result
            cache.set({"value": "hello", "type": "test"}, {"data": 99})
            result2 = cache.get(key)
            assert result2 == {"data": 99}, "Same key (different order) should overwrite"

            # Clear
            removed = cache.clear()
            assert removed >= 1, "clear() should remove entries"
            assert cache.get(key) is None, "Should be empty after clear"

        print("✓ Cache miss/hit/overwrite/clear all work correctly")
        return True
    except Exception as e:
        print(f"✗ Content cache error: {e}")
        return False


def test_shorts_extractor_parser():
    """Test the shorts parser with mock LLM output (no API key required)."""
    print("\nTesting shorts extractor parser...")
    try:
        from shorts_extractor import ShortsExtractor
        from config import Config

        # Temporarily set a dummy key so __init__ doesn't raise
        original_key = Config.OPENAI_API_KEY
        try:
            Config.OPENAI_API_KEY = "dummy_key_for_parser_test"
            import openai
            openai.api_key = "dummy_key_for_parser_test"

            extractor = ShortsExtractor.__new__(ShortsExtractor)

            mock_output = """
SHORT 1: Earn Passive Income Today
HOOK: Did you know 90% of millionaires have multiple income streams?
SCRIPT: Here is how you can start earning passive income with just $100 a month.
CAPTION: 💰 Start your passive income journey today! #money
HASHTAGS: #passiveincome #finance #money #investing #sidehustle
---
SHORT 2: Top AI Tool of 2024
HOOK: This single AI tool replaced my entire team of 5 assistants.
SCRIPT: I'm going to show you the one AI tool that changed my business forever.
CAPTION: 🤖 The AI tool everyone is talking about #AI #tools
HASHTAGS: #aitools #productivity #automation #tech #business
---
"""
            shorts = extractor._parse_shorts(mock_output, 2)

            assert len(shorts) == 2, f"Expected 2 shorts, got {len(shorts)}"
            assert shorts[0]["title"] == "Earn Passive Income Today"
            assert "90%" in shorts[0]["hook"]
            assert "#passiveincome" in shorts[0]["hashtags"]
            assert shorts[0]["format"] == "9:16"
            assert shorts[1]["title"] == "Top AI Tool of 2024"
        finally:
            Config.OPENAI_API_KEY = original_key

        print("✓ Shorts parser correctly extracts title/hook/script/caption/hashtags")
        return True
    except Exception as e:
        print(f"✗ Shorts extractor parser error: {e}")
        return False


def test_cli_dry_run():
    """Test CLI dry-run cost estimation without making API calls."""
    print("\nTesting CLI dry-run cost estimation...")
    try:
        from channel_presets import CHANNEL_A_FINANCE, CHANNEL_B_DEVOTION
        from cli import estimate_costs

        for preset in (CHANNEL_A_FINANCE, CHANNEL_B_DEVOTION):
            for output_type in ("long", "shorts", "both"):
                for tier in ("free", "low", "high"):
                    costs = estimate_costs(preset, output_type, tier, 4)
                    assert "total_usd" in costs
                    assert costs["total_usd"] >= 0
                    assert "model" in costs

        print("✓ Cost estimation works for all channel/output/tier combinations")
        return True
    except Exception as e:
        print(f"✗ CLI dry-run error: {e}")
        return False


def test_api_server_imports():
    """Test that the API server module can be imported and routes registered."""
    print("\nTesting API server imports...")
    try:
        from api_server import app

        routes = {r.path for r in app.routes}
        assert "/health" in routes, "/health route missing"
        assert "/api/presets" in routes, "/api/presets route missing"
        assert "/api/estimate" in routes, "/api/estimate route missing"
        assert "/api/generate/titles" in routes, "/api/generate/titles route missing"
        assert "/api/generate/shorts" in routes, "/api/generate/shorts route missing"

        print(f"✓ API server has {len(routes)} registered routes")
        return True
    except Exception as e:
        print(f"✗ API server import error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("🕉️  DEVOTIONAL PIPELINE - MODULE VALIDATION")
    print("=" * 70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Music Handler", test_music_handler),
        ("Visual Queries", test_visual_queries),
        ("Weekly Themes", test_weekly_themes),
        ("FFmpeg Check", test_ffmpeg),
        ("Channel Presets", test_channel_presets),
        ("Content Cache", test_content_cache),
        ("Shorts Extractor Parser", test_shorts_extractor_parser),
        ("CLI Dry-Run", test_cli_dry_run),
        ("API Server", test_api_server_imports),
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
        print("  3. Run: python cli.py --channel B --output both  (devotion)")
        print("         python cli.py --channel A --output both  (finance)")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running pipeline.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
