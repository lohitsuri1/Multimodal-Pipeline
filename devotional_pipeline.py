"""Main orchestrator for devotional video generation pipeline."""
import sys
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment
from config import Config
from script_generator import DevotionalScriptGenerator
from voice_narrator import VoiceNarrator
from visual_assets import VisualAssetFetcher
from music_handler import BackgroundMusicHandler
from video_compositor import VideoCompositor


def _configure_console_encoding() -> None:
    """Ensure Unicode console output works on Windows terminals."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

class DevotionalVideoPipeline:
    """Orchestrate the complete devotional video generation process."""
    
    def __init__(self):
        """Initialize the pipeline."""
        Config.ensure_directories()
        
        self.script_generator = DevotionalScriptGenerator()
        self.voice_narrator = VoiceNarrator()
        self.visual_fetcher = VisualAssetFetcher()
        self.music_handler = BackgroundMusicHandler()
        self.compositor = VideoCompositor()
    
    def generate_video(self, theme: str = None, week_number: int = None) -> Path:
        """
        Generate a complete devotional video.
        
        Args:
            theme: Optional theme for the video
            week_number: Optional week number for tracking
            
        Returns:
            Path to the generated video file
        """
        print("=" * 70)
        print("🕉️  DEVOTIONAL VIDEO GENERATION PIPELINE")
        print("=" * 70)
        
        # Step 1: Generate script
        print("\n[1/5] Generating devotional script...")
        script_data = self.script_generator.generate_script(theme)
        print(f"✓ Generated script with {len(script_data['segments'])} segments")
        print(f"   Theme: {script_data['theme']}")
        
        # Step 2: Generate voice narration
        print("\n[2/5] Generating voice narration...")
        voice_file = Config.TEMP_DIR / "narration" / "full_narration.mp3"
        voice_path = self.voice_narrator.generate_narration(
            script_data['full_script'],
            voice_file
        )
        print(f"✓ Voice narration created: {voice_path}")

        voice_duration_sec = len(AudioSegment.from_file(voice_path)) / 1000.0
        if voice_duration_sec < 300:
            print(
                f"⚠️  Narration is short ({voice_duration_sec:.1f}s). "
                "Use a more detailed theme/prompt for longer, more cinematic output."
            )
        
        # Step 3: Fetch visual assets
        print("\n[3/5] Fetching devotional visual assets...")
        images = self.visual_fetcher.fetch_diverse_images(
            num_total=30,
            output_dir=Config.TEMP_DIR / "images"
        )
        
        if not images:
            print("\n⚠️  No images were fetched automatically.")
            print(self._get_manual_image_instructions())
            
            # Check if user has manually added images
            manual_images = list((Config.TEMP_DIR / "images").glob("*.jpg")) + \
                           list((Config.TEMP_DIR / "images").glob("*.png"))
            
            if manual_images:
                print(f"✓ Found {len(manual_images)} manually added images")
                images = manual_images
            else:
                raise Exception("No images available. Please add images manually or configure API keys.")
        else:
            print(f"✓ Fetched {len(images)} images")
        
        # Step 4: Get background music
        print("\n[4/5] Preparing background music...")
        music_file = self.music_handler.get_music_file()
        
        if music_file:
            if self.music_handler.validate_music_file(music_file):
                print(f"✓ Using background music: {music_file.name}")
            else:
                print("⚠️  Music file validation failed")
                music_file = None
        else:
            print("⚠️  No background music found")
            if Config.MUSIC_YOUTUBE_URL:
                print("   Auto-download was configured but did not succeed.")
                print("   Verify MUSIC_YOUTUBE_URL and install yt-dlp.")
            else:
                print("   Tip: set MUSIC_YOUTUBE_URL in .env for automatic royalty-free music download.")
            print(self.music_handler.setup_music_instructions())
            music_file = None
        
        # Step 5: Compose final video
        print("\n[5/5] Composing final video...")
        
        # Check FFmpeg availability
        if not self.compositor.check_ffmpeg():
            raise Exception(
                "FFmpeg is not installed. Please install FFmpeg:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: Download from https://ffmpeg.org/download.html"
            )
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        week_str = f"_week{week_number}" if week_number else ""
        output_filename = f"devotional_video{week_str}_{timestamp}.mp4"
        
        video_path = self.compositor.create_video(
            images=images,
            voice_audio=voice_path,
            background_music=music_file,
            subtitle_text=script_data['full_script'],
            output_filename=output_filename
        )
        
        print("\n" + "=" * 70)
        print("✓ VIDEO GENERATION COMPLETE!")
        print("=" * 70)
        print(f"\nOutput: {video_path}")
        print(f"Duration: ~{Config.VIDEO_DURATION_MINUTES} minutes")
        print(f"Theme: {script_data['theme']}")
        
        # Save script for reference
        script_file = video_path.parent / f"{video_path.stem}_script.txt"
        with open(script_file, "w") as f:
            f.write(f"Theme: {script_data['theme']}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(script_data['full_script'])
        print(f"Script saved: {script_file}")
        
        # Attribution reminder
        if music_file:
            print("\n⚠️  IMPORTANT: Add music attribution to your video description!")
            print("   Check music source for required credits.")
        
        return video_path
    
    def _get_manual_image_instructions(self) -> str:
        """Get instructions for manually adding images."""
        images_dir = Config.TEMP_DIR / "images"
        
        return f"""
╔════════════════════════════════════════════════════════════════╗
║             MANUAL IMAGE SETUP REQUIRED                         ║
╚════════════════════════════════════════════════════════════════╝

To use images, either:

OPTION 1: Configure API Keys (Recommended)
  1. Add Google AI Studio key (for generated visuals):
      GOOGLE_API_KEY=your_key_here
      Optional:
      VISUAL_PROVIDER_ORDER=google,pexels,pixabay
      GOOGLE_IMAGE_MODEL=gemini-2.0-flash-preview-image-generation
  2. Or use free stock APIs:
      - https://www.pexels.com/api/
      - https://pixabay.com/api/docs/
  3. Add to .env file:
      PEXELS_API_KEY=your_key_here
      OR
      PIXABAY_API_KEY=your_key_here

OPTION 2: Add Images Manually
  1. Download 20-30 copyright-safe images from:
     - https://www.pexels.com (search: temple, lotus, spiritual, meditation)
     - https://pixabay.com (search: hindu, spiritual, nature, diya)
     - Your own photos
  2. Place images in: {images_dir}
  3. Supported formats: .jpg, .png
  4. Landscape orientation recommended (1920x1080)

IMPORTANT: Only use royalty-free or public domain images!
"""

def main():
    """Main entry point for the pipeline."""
    try:
        _configure_console_encoding()

        # Validate configuration
        Config.validate_config()
        
        # Initialize pipeline
        pipeline = DevotionalVideoPipeline()
        
        # Get weekly theme (rotate through themes)
        themes = pipeline.script_generator.get_weekly_themes()
        week_number = datetime.now().isocalendar()[1]  # ISO week number
        theme = themes[week_number % len(themes)]
        
        print(f"\n📅 Week {week_number}")
        print(f"🎯 Theme: {theme}\n")
        
        # Generate video
        video_path = pipeline.generate_video(theme=theme, week_number=week_number)
        
        print("\n✨ Success! Your devotional video is ready.")
        print(f"\n📹 Video location: {video_path}")
        print("\nNext steps:")
        print("  1. Review the video")
        print("  2. Add proper attribution in video description")
        print("  3. Upload to your platform")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
