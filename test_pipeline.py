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
