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

def test_content_presets():
    """Test content preset system."""
    print("\nTesting content presets...")
    try:
        from content_presets import get_preset, PRESETS

        # Both required presets must exist
        assert "finance_ai_saas" in PRESETS, "finance_ai_saas preset missing"
        assert "devotional" in PRESETS, "devotional preset missing"

        for name in ("finance_ai_saas", "devotional"):
            preset = get_preset(name)
            assert preset.name == name
            assert preset.long_form_system_prompt
            assert "{theme}" in preset.long_form_user_template
            assert "{duration_minutes}" in preset.long_form_user_template
            assert len(preset.default_themes) >= 1
            assert set(preset.platform_cues.keys()) == {
                "youtube_long", "youtube_shorts", "instagram_reels"
            }
            assert preset.title_prompt_template
            assert preset.thumbnail_prompt_template
            assert len(preset.default_broll_keywords) >= 3

        # Unknown preset raises ValueError
        try:
            get_preset("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        print(f"✓ Content presets validated ({len(PRESETS)} presets)")
        return True
    except Exception as e:
        print(f"✗ Content presets error: {e}")
        return False


def test_shorts_extractor():
    """Test shorts extraction module."""
    print("\nTesting shorts extractor...")
    try:
        from shorts_extractor import extract_shorts, shorts_dry_run_estimate

        # Build a minimal structured script
        sample_script = (
            "HOOK: Did you know AI can replace your marketing team?\n"
            "You are about to discover 5 tools that do exactly that.\n\n"
            "PROMISE: In this video you will learn the top tools and how to use them.\n\n"
            "SECTION 1: Tool One\n"
            "This is the first major point. It covers many things about AI and productivity. "
            "Use it every day to save hours. Many entrepreneurs rely on it for content. "
            "Results are immediate and the pricing is fair for most budgets.\n\n"
            "SECTION 2: Tool Two\n"
            "This is the second major point. It focuses on automation and scheduling. "
            "You can integrate it with your existing workflow. "
            "Teams of all sizes benefit from this approach.\n\n"
            "SECTION 3: Tool Three\n"
            "This is the third major point. Analytics and insights are the core feature. "
            "It helps you understand your audience. Data drives better decisions always.\n\n"
            "RECAP: Quick summary of the three tools and how they help.\n"
            "CTA: Like and subscribe for more AI tips every week!\n"
        )
        script_data = {"full_script": sample_script, "segments": []}

        # Default count
        shorts = extract_shorts(script_data, count=4)
        assert isinstance(shorts, list)
        assert 1 <= len(shorts) <= 4
        for s in shorts:
            assert "hook" in s
            assert "body" in s
            assert "cta" in s
            assert "caption_text" in s
            assert "broll_keywords" in s
            assert isinstance(s["broll_keywords"], list)
            assert len(s["caption_text"]) <= 63  # 60 chars + optional "..."

        # Dry-run estimate (no API calls)
        est = shorts_dry_run_estimate(script_data, count=4)
        assert est["api_calls_required"] == 0
        assert "shorts_that_will_be_produced" in est

        # Count clamping
        shorts_max = extract_shorts(script_data, count=100)
        assert len(shorts_max) <= 8

        print(f"✓ Shorts extractor: produced {len(shorts)} shorts from sample script")
        return True
    except Exception as e:
        print(f"✗ Shorts extractor error: {e}")
        return False


def test_pipeline_cache():
    """Test disk-based caching module."""
    print("\nTesting pipeline cache...")
    try:
        import tempfile, os
        from unittest.mock import patch
        from pathlib import Path
        from config import Config

        # Point cache to a temp directory for this test
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(Config, "CACHE_DIR", Path(tmp)):
                from pipeline_cache import get_cached, set_cached, make_cache_key

                key = make_cache_key(theme="test", preset="devotional", tier="free")

                # Miss
                assert get_cached(key, "scripts") is None

                # Set and hit
                payload = {"script": "hello world", "titles": ["Title 1"]}
                set_cached(key, payload, "scripts")
                retrieved = get_cached(key, "scripts")
                assert retrieved == payload

                # Different kwargs → different key
                key2 = make_cache_key(theme="other", preset="devotional", tier="free")
                assert key != key2
                assert get_cached(key2, "scripts") is None

        print("✓ Pipeline cache: set/get/miss working correctly")
        return True
    except Exception as e:
        print(f"✗ Pipeline cache error: {e}")
        return False


def test_cost_controls():
    """Test that cost control constants are present in Config."""
    print("\nTesting cost controls in Config...")
    try:
        from config import Config

        assert hasattr(Config, "MAX_TOKENS_PER_CALL"), "MAX_TOKENS_PER_CALL missing"
        assert hasattr(Config, "MAX_RETRIES"), "MAX_RETRIES missing"
        assert hasattr(Config, "MAX_SCENES_PER_RUN"), "MAX_SCENES_PER_RUN missing"
        assert hasattr(Config, "MAX_TTS_CHARS"), "MAX_TTS_CHARS missing"
        assert hasattr(Config, "CACHE_DIR"), "CACHE_DIR missing"
        assert hasattr(Config, "API_KEY"), "API_KEY missing"
        assert hasattr(Config, "RATE_LIMIT_PER_MINUTE"), "RATE_LIMIT_PER_MINUTE missing"

        assert Config.MAX_TOKENS_PER_CALL > 0
        assert Config.MAX_RETRIES >= 1
        assert Config.MAX_SCENES_PER_RUN > 0
        assert Config.MAX_TTS_CHARS > 0
        assert Config.RATE_LIMIT_PER_MINUTE > 0

        print("✓ All cost control constants present and valid")
        return True
    except Exception as e:
        print(f"✗ Cost controls error: {e}")
        return False


def test_cli_dry_run():
    """Test the quick_start CLI --dry-run flag (no paid API calls)."""
    print("\nTesting CLI --dry-run...")
    try:
        from quick_start import main as cli_main

        # Should succeed without any API keys
        exit_code = cli_main(
            ["--preset", "finance_ai_saas", "--output", "both", "--dry-run"]
        )
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"

        exit_code2 = cli_main(
            ["--preset", "devotional", "--output", "long", "--dry-run"]
        )
        assert exit_code2 == 0

        print("✓ CLI --dry-run works for both presets")
        return True
    except Exception as e:
        print(f"✗ CLI dry-run error: {e}")
        return False


def test_api_server_imports():
    """Test that the FastAPI server module can be imported."""
    print("\nTesting API server imports...")
    try:
        import importlib.util
        spec = importlib.util.find_spec("fastapi")
        if spec is None:
            print("⚠ Skipped (fastapi not installed)")
            return True

        from api_server import app, check_api_key, check_rate_limit
        assert app is not None
        print("✓ API server module imported successfully")
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
        ("Content Presets", test_content_presets),
        ("Shorts Extractor", test_shorts_extractor),
        ("Pipeline Cache", test_pipeline_cache),
        ("Cost Controls", test_cost_controls),
        ("CLI Dry-Run", test_cli_dry_run),
        ("API Server Imports", test_api_server_imports),
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
        print("  3. Run: python devotional_pipeline.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running pipeline.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
