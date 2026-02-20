"""Video compositor for assembling devotional videos."""
from pathlib import Path
from typing import List
import subprocess
from config import Config
from pydub import AudioSegment
import math

class VideoCompositor:
    """Compose final devotional video from visuals, voice, and music."""
    
    def __init__(self):
        """Initialize the video compositor."""
        self.output_dir = Config.OUTPUT_DIR
        self.temp_dir = Config.TEMP_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def create_video(
        self,
        images: List[Path],
        voice_audio: Path,
        background_music: Path = None,
        output_filename: str = "devotional_video.mp4"
    ) -> Path:
        """
        Create the final devotional video.
        
        Args:
            images: List of image paths to use as visuals
            voice_audio: Path to voice narration audio
            background_music: Optional path to background music
            output_filename: Name for output video file
            
        Returns:
            Path to the generated video file
        """
        output_path = self.output_dir / output_filename
        
        print("Starting video composition...")
        
        # Step 1: Prepare audio track (voice + music)
        print("Preparing audio track...")
        audio_path = self._prepare_audio(voice_audio, background_music)
        
        # Step 2: Get audio duration to match video length
        audio_duration = self._get_audio_duration(audio_path)
        
        # Step 3: Create video from images with slow zoom/pan effects
        print("Creating video from images...")
        video_path = self._create_video_from_images(images, audio_duration)
        
        # Step 4: Combine video and audio
        print("Combining video and audio...")
        final_path = self._combine_video_and_audio(video_path, audio_path, output_path)
        
        print(f"✓ Video created successfully: {final_path}")
        return final_path
    
    def _prepare_audio(
        self, 
        voice_audio: Path, 
        background_music: Path = None
    ) -> Path:
        """
        Combine voice narration with background music.
        
        Args:
            voice_audio: Path to voice narration
            background_music: Optional path to background music
            
        Returns:
            Path to combined audio file
        """
        output_path = self.temp_dir / "combined_audio.mp3"
        
        # Load voice audio
        voice = AudioSegment.from_file(voice_audio)
        
        if background_music and background_music.exists():
            # Load background music
            music = AudioSegment.from_file(background_music)
            
            # Loop music to match voice duration if needed
            voice_duration = len(voice)
            music_duration = len(music)
            
            if music_duration < voice_duration:
                # Loop the music
                loops_needed = math.ceil(voice_duration / music_duration)
                music = music * loops_needed
            
            # Trim music to match voice duration
            music = music[:voice_duration]
            
            # Reduce music volume relative to voice
            # Calculate dB reduction: 0.2 volume -> -14dB, 0.5 volume -> -6dB, 0.8 volume -> -2dB
            volume_reduction_db = 20 * (1 - Config.MUSIC_VOLUME)
            music = music - volume_reduction_db
            
            # Overlay music under voice
            combined = voice.overlay(music)
        else:
            combined = voice
        
        # Export combined audio
        combined.export(output_path, format="mp3")
        return output_path
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert ms to seconds
    
    def _create_video_from_images(
        self, 
        images: List[Path], 
        duration: float
    ) -> Path:
        """
        Create video slideshow from images with Ken Burns effect.
        
        Args:
            images: List of image paths
            duration: Total duration in seconds
            
        Returns:
            Path to created video file
        """
        output_path = self.temp_dir / "slideshow.mp4"
        
        if not images:
            raise ValueError("No images provided for video creation")
        
        # Calculate duration per image
        duration_per_image = duration / len(images)
        
        # Create input file list for FFmpeg
        concat_file = self.temp_dir / "concat_list.txt"
        with open(concat_file, "w") as f:
            for img in images:
                f.write(f"file '{img.absolute()}'\n")
                f.write(f"duration {duration_per_image}\n")
            # Add last image again (FFmpeg concat requirement)
            f.write(f"file '{images[-1].absolute()}'\n")
        
        # Build FFmpeg video filter for Ken Burns effect
        # 1. Scale and crop to target resolution
        scale_filter = f"scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:force_original_aspect_ratio=increase"
        crop_filter = f"crop={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}"
        
        # 2. Ken Burns effect (slow zoom)
        zoom_duration_frames = int(duration_per_image * Config.VIDEO_FPS)
        zoom_filter = (
            f"zoompan=z='min(zoom+0.0015,1.1)'"
            f":d={zoom_duration_frames}"
            f":x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)'"
            f":s={Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}"
            f":fps={Config.VIDEO_FPS}"
        )
        
        # Combine filters
        video_filter = f"{scale_filter},{crop_filter},{zoom_filter}"
        
        # FFmpeg command to create video with effects
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-vf", video_filter,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_path)
        ]
        
        print("Running FFmpeg to create video slideshow...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Fallback to simpler method without zoom effect
            print("Trying simpler slideshow method...")
            simple_filter = f"{scale_filter},{crop_filter}"
            
            cmd_simple = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-vf", simple_filter,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-r", str(Config.VIDEO_FPS),
                "-y",
                str(output_path)
            ]
            
            result = subprocess.run(cmd_simple, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path
    
    def _combine_video_and_audio(
        self, 
        video_path: Path, 
        audio_path: Path, 
        output_path: Path
    ) -> Path:
        """
        Combine video and audio into final output.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path for final output
            
        Returns:
            Path to final video
        """
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error combining video and audio: {result.stderr}")
        
        return output_path
    
    def check_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is installed.
        
        Returns:
            True if FFmpeg is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
