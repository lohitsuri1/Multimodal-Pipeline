"""Text-to-speech module for generating voice narration."""
import os
from pathlib import Path
from gtts import gTTS
from config import Config

try:
    from elevenlabs import generate, save, set_api_key
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

class VoiceNarrator:
    """Generate voice narration for devotional scripts."""
    
    def __init__(self, use_elevenlabs: bool = False):
        """
        Initialize the voice narrator.
        
        Args:
            use_elevenlabs: If True, use ElevenLabs for higher quality (requires API key)
        """
        self.use_elevenlabs = use_elevenlabs and ELEVENLABS_AVAILABLE
        
        if self.use_elevenlabs:
            if not Config.ELEVENLABS_API_KEY:
                print("ElevenLabs API key not found, falling back to gTTS")
                self.use_elevenlabs = False
            else:
                set_api_key(Config.ELEVENLABS_API_KEY)
    
    def generate_narration(self, script: str, output_path: Path) -> Path:
        """
        Generate audio narration from script.
        
        Args:
            script: The text script to narrate
            output_path: Where to save the audio file
            
        Returns:
            Path to the generated audio file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.use_elevenlabs:
            return self._generate_with_elevenlabs(script, output_path)
        else:
            return self._generate_with_gtts(script, output_path)
    
    def _generate_with_gtts(self, script: str, output_path: Path) -> Path:
        """
        Generate narration using Google Text-to-Speech (free).
        
        Args:
            script: The text to convert to speech
            output_path: Where to save the audio
            
        Returns:
            Path to generated audio file
        """
        try:
            # Use slow=True for more deliberate, meditative pace
            tts = gTTS(
                text=script,
                lang=Config.VOICE_LANGUAGE,
                slow=False  # We'll adjust speed in post-processing if needed
            )
            
            tts.save(str(output_path))
            print(f"Generated narration using gTTS: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error generating narration with gTTS: {str(e)}")
    
    def _generate_with_elevenlabs(self, script: str, output_path: Path) -> Path:
        """
        Generate narration using ElevenLabs (premium quality).
        
        Args:
            script: The text to convert to speech
            output_path: Where to save the audio
            
        Returns:
            Path to generated audio file
        """
        try:
            # Use a calm, soothing voice for devotional content
            audio = generate(
                text=script,
                voice="Bella",  # Calm, clear voice - good for meditation
                model="eleven_monolingual_v1"
            )
            
            save(audio, str(output_path))
            print(f"Generated narration using ElevenLabs: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Error generating narration with ElevenLabs: {str(e)}")
    
    def generate_segment_narrations(
        self, 
        segments: list, 
        output_dir: Path
    ) -> list:
        """
        Generate narration for each script segment.
        
        Args:
            segments: List of script segments with 'content' field
            output_dir: Directory to save audio files
            
        Returns:
            List of paths to generated audio files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        
        for i, segment in enumerate(segments):
            output_file = output_dir / f"segment_{i+1:02d}.mp3"
            
            print(f"Generating narration for segment {i+1}/{len(segments)}...")
            audio_path = self.generate_narration(
                segment['content'],
                output_file
            )
            audio_files.append(audio_path)
        
        return audio_files
