#!/usr/bin/env python3
"""Setup wizard for the Devotional Video Pipeline."""
import os
import sys
from pathlib import Path

def print_header():
    """Print welcome header."""
    print("=" * 70)
    print("🕉️  DEVOTIONAL VIDEO PIPELINE - SETUP WIZARD")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    if sys.version_info < (3, 10):
        print("✗ Python 3.10 or higher is required")
        print(f"  Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies():
    """Check if dependencies are installed."""
    print("\nChecking dependencies...")
    try:
        import openai
        import gtts
        import requests
        import PIL
        from pydub import AudioSegment
        print("✓ All Python packages installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e.name}")
        print("\nPlease run: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\nChecking FFmpeg...")
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ FFmpeg installed")
            return True
        else:
            print("✗ FFmpeg check failed")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found")
        print("\nPlease install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False

def create_env_file():
    """Help user create .env file."""
    print("\n" + "=" * 70)
    print("API KEYS SETUP")
    print("=" * 70)
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("\n.env file already exists")
        response = input("Do you want to update it? (y/n): ").lower()
        if response != 'y':
            print("Skipping .env setup")
            return True
    
    print("\nLet's set up your API keys.")
    print("You can press Enter to skip optional keys.\n")
    
    # OpenAI (Required)
    print("1. OpenAI API Key (REQUIRED)")
    print("   Get it from: https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key: ").strip()
    
    if not openai_key:
        print("\n✗ OpenAI API key is required for script generation")
        return False
    
    # Pexels (Required - Option 1)
    print("\n2. Pexels API Key (REQUIRED - Option 1)")
    print("   Get it from: https://www.pexels.com/api/")
    print("   Completely free, no credit card required")
    pexels_key = input("   Enter your Pexels API key (or press Enter to skip): ").strip()
    
    # Pixabay (Required - Option 2)
    pixabay_key = ""
    if not pexels_key:
        print("\n3. Pixabay API Key (REQUIRED - Option 2)")
        print("   Get it from: https://pixabay.com/api/docs/")
        print("   Completely free, no credit card required")
        pixabay_key = input("   Enter your Pixabay API key: ").strip()
        
        if not pixabay_key:
            print("\n✗ Either Pexels or Pixabay API key is required for images")
            return False
    
    # ElevenLabs (Optional)
    print("\n4. ElevenLabs API Key (OPTIONAL - for better voice)")
    print("   Get it from: https://elevenlabs.io/")
    print("   Free tier: 10,000 characters/month")
    elevenlabs_key = input("   Enter your ElevenLabs API key (or press Enter to skip): ").strip()
    
    # Write .env file
    with open(env_path, "w") as f:
        f.write("# Devotional Video Pipeline Configuration\n\n")
        f.write("# OpenAI (Required - for script generation)\n")
        f.write(f"OPENAI_API_KEY={openai_key}\n\n")
        f.write("# Image APIs (At least one required)\n")
        f.write(f"PEXELS_API_KEY={pexels_key}\n")
        f.write(f"PIXABAY_API_KEY={pixabay_key}\n\n")
        f.write("# Voice (Optional - defaults to free gTTS)\n")
        f.write(f"ELEVENLABS_API_KEY={elevenlabs_key}\n\n")
        f.write("# Video Settings\n")
        f.write("VIDEO_DURATION_MINUTES=30\n")
        f.write("OUTPUT_DIR=output_videos\n")
        f.write("TEMP_DIR=temp_files\n")
        f.write("VOICE_LANGUAGE=en\n")
        f.write("VOICE_SPEED=0.9\n")
        f.write("MUSIC_VOLUME=0.2\n")
    
    print("\n✓ .env file created successfully")
    return True

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print("\n📋 Next Steps:\n")
    print("1. (Optional) Add background music:")
    print("   - Create directory: mkdir -p temp_files/music")
    print("   - Download royalty-free devotional music")
    print("   - Save as: temp_files/music/background_music.mp3")
    print("   - See DEVOTIONAL_PIPELINE_README.md for music sources\n")
    print("2. Generate your first video:")
    print("   python devotional_pipeline.py\n")
    print("3. For weekly automation:")
    print("   - See GitHub Actions section in DEVOTIONAL_PIPELINE_README.md")
    print("   - Add secrets to your GitHub repository")
    print("   - Enable the workflow\n")
    print("📖 Full documentation: DEVOTIONAL_PIPELINE_README.md")
    print()

def main():
    """Run setup wizard."""
    print_header()
    
    # Check system requirements
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            break
    
    if not all_passed:
        print("\n❌ Setup failed. Please fix the issues above and run again.")
        return 1
    
    # Set up API keys
    if not create_env_file():
        print("\n❌ API key setup failed.")
        return 1
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
