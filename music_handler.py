"""Background music handler for devotional videos."""
import subprocess
from pathlib import Path
from typing import List
from config import Config

class BackgroundMusicHandler:
    """Handle royalty-free devotional background music."""
    
    def __init__(self):
        """Initialize the background music handler."""
        self.music_dir = Config.TEMP_DIR / "music"
        self.music_dir.mkdir(parents=True, exist_ok=True)
    
    def get_royalty_free_sources(self) -> List[dict]:
        """
        Get list of royalty-free music sources.
        
        Returns:
            List of dictionaries with music source information
        """
        return [
            {
                "name": "YouTube Audio Library",
                "url": "https://www.youtube.com/audiolibrary",
                "description": "Free music for YouTube videos. Search for 'Indian', 'Meditation', or 'Spiritual'",
                "license": "Free to use with attribution in description"
            },
            {
                "name": "Chosic - Devotional Music",
                "url": "https://www.chosic.com/free-music/devotional/",
                "description": "Royalty-free devotional music tracks",
                "license": "Attribution required"
            },
            {
                "name": "Free Music Archive",
                "url": "https://freemusicarchive.org/",
                "description": "Search for 'devotional', 'meditation', 'indian classical'",
                "license": "Various Creative Commons licenses"
            },
            {
                "name": "Incompetech",
                "url": "https://incompetech.com/music/royalty-free/",
                "description": "Kevin MacLeod's royalty-free music. Search 'Indian' or 'World'",
                "license": "CC BY 4.0 (attribution required)"
            }
        ]
    
    def get_music_requirements(self) -> dict:
        """
        Get music requirements for attribution.
        
        Returns:
            Dictionary with music requirements and guidelines
        """
        return {
            "duration": f"{Config.VIDEO_DURATION_MINUTES} minutes",
            "style": "Calm, devotional, meditative",
            "instruments": "Suggested: Flute, Sitar, Tanpura, Tabla (soft), Bells",
            "tempo": "Slow to medium (60-80 BPM recommended)",
            "volume": f"{Config.MUSIC_VOLUME * 100}% of voice volume",
            "attribution": "Always credit music creator in video description",
            "license_check": "Verify license allows YouTube monetization if needed"
        }

    def _trim_downloaded_audio(self, audio_path: Path) -> Path:
        """Optionally trim downloaded music using configured start and duration."""
        start_sec = max(0, Config.MUSIC_YOUTUBE_START_SEC)
        duration_sec = max(0, Config.MUSIC_YOUTUBE_DURATION_SEC)

        if start_sec == 0 and duration_sec == 0:
            return audio_path

        from pydub import AudioSegment

        audio = AudioSegment.from_file(audio_path)
        start_ms = start_sec * 1000

        if start_ms >= len(audio):
            return audio_path

        if duration_sec > 0:
            end_ms = min(len(audio), start_ms + (duration_sec * 1000))
            trimmed = audio[start_ms:end_ms]
        else:
            trimmed = audio[start_ms:]

        output_path = self.music_dir / "background_music.mp3"
        trimmed.export(output_path, format="mp3")
        return output_path

    def _download_music_from_youtube(self) -> Path:
        """Download royalty-free background music from a configured YouTube URL."""
        youtube_url = Config.MUSIC_YOUTUBE_URL
        if not youtube_url:
            return None

        output_pattern = self.music_dir / "youtube_music.%(ext)s"
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(output_pattern),
            youtube_url,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            print("yt-dlp not found. Install it with: python -m pip install yt-dlp")
            return None

        if result.returncode != 0:
            print(f"YouTube music download failed: {result.stderr.strip()}")
            return None

        candidates = sorted(self.music_dir.glob("youtube_music*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            return None

        downloaded = candidates[0]
        return self._trim_downloaded_audio(downloaded)
    
    def create_music_placeholder(self, output_path: Path = None) -> Path:
        """
        Create a silent audio placeholder as fallback.
        
        Args:
            output_path: Where to save the placeholder
            
        Returns:
            Path to placeholder audio file
        """
        output_path = output_path or self.music_dir / "silence.mp3"
        
        # Create a very short silent audio file
        # This serves as a placeholder when no music is provided
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Generate 1 second of very quiet tone
        duration_ms = 1000
        silent_audio = Sine(20).to_audio_segment(duration=duration_ms, volume=-60)
        
        silent_audio.export(output_path, format="mp3")
        print(f"Created placeholder audio: {output_path}")
        
        return output_path
    
    def setup_music_instructions(self) -> str:
        """
        Provide instructions for adding background music.
        
        Returns:
            Formatted instructions string
        """
        sources = self.get_royalty_free_sources()
        requirements = self.get_music_requirements()
        
        instructions = """
╔════════════════════════════════════════════════════════════════╗
║        BACKGROUND MUSIC SETUP INSTRUCTIONS                      ║
╚════════════════════════════════════════════════════════════════╝

MUSIC REQUIREMENTS:
"""
        for key, value in requirements.items():
            instructions += f"  • {key}: {value}\n"
        
        instructions += "\n\nROYALTY-FREE MUSIC SOURCES:\n"
        for i, source in enumerate(sources, 1):
            instructions += f"\n{i}. {source['name']}\n"
            instructions += f"   URL: {source['url']}\n"
            instructions += f"   Description: {source['description']}\n"
            instructions += f"   License: {source['license']}\n"
        
        instructions += """
\nHOW TO ADD MUSIC:
1. Download a devotional track from one of the sources above
2. Place it in the 'music' directory: """ + str(self.music_dir) + """
3. Name it 'background_music.mp3'
4. The pipeline will automatically use it in the video

IMPORTANT ATTRIBUTION:
When using royalty-free music, you MUST add attribution in your
video description. Example:

  Music: [Track Name] by [Artist Name]
  Source: [Website]
  License: [License Type]

For YouTube Audio Library tracks, follow their specific attribution
requirements shown on the download page.

TIP: For 30-minute videos, you may need to loop shorter tracks.
The video pipeline will handle this automatically.

AUTO-DOWNLOAD (OPTIONAL):
You can set MUSIC_YOUTUBE_URL in your .env file to auto-download
audio with yt-dlp when local music is missing. Use only tracks
you are legally allowed to reuse.
"""
        return instructions
    
    def get_music_file(self) -> Path:
        """
        Get the background music file if it exists.
        
        Returns:
            Path to music file, or None if not found
        """
        # Check for common music file names
        possible_names = [
            "background_music.mp3",
            "devotional_music.mp3",
            "music.mp3",
            "background.mp3"
        ]
        
        for name in possible_names:
            music_path = self.music_dir / name
            if music_path.exists():
                return music_path
        
        # Check if any mp3 file exists in the music directory
        mp3_files = list(self.music_dir.glob("*.mp3"))
        if mp3_files:
            return mp3_files[0]

        # Optional fallback: auto-download from a royalty-free YouTube URL.
        auto_downloaded = self._download_music_from_youtube()
        if auto_downloaded and auto_downloaded.exists():
            print(f"Downloaded music from YouTube: {auto_downloaded.name}")
            return auto_downloaded
        
        return None
    
    def validate_music_file(self, music_path: Path) -> bool:
        """
        Validate that the music file is usable.
        
        Args:
            music_path: Path to music file
            
        Returns:
            True if valid, False otherwise
        """
        if not music_path.exists():
            return False
        
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(music_path)
            
            # Check minimum duration (should be at least 30 seconds)
            if len(audio) < 30000:  # 30 seconds in milliseconds
                print(f"Warning: Music file is very short ({len(audio)/1000}s)")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating music file: {e}")
            return False
