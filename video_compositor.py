"""Video compositor for assembling devotional videos."""
from pathlib import Path
from typing import List
import subprocess
from config import Config
from pydub import AudioSegment
from pydub import effects
import math
import re

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
        subtitle_text: str = None,
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
        final_path = self._combine_video_and_audio(
            video_path,
            audio_path,
            output_path,
            subtitle_text=subtitle_text,
        )
        
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
        voice = effects.normalize(voice, headroom=1.0)
        
        if background_music and background_music.exists():
            # Load background music
            music = AudioSegment.from_file(background_music)
            music = effects.normalize(music, headroom=8.0)
            
            # Loop music to match voice duration if needed
            voice_duration = len(voice)
            music_duration = len(music)
            
            if music_duration < voice_duration:
                # Loop the music
                loops_needed = math.ceil(voice_duration / music_duration)
                music = music * loops_needed
            
            # Trim music to match voice duration
            music = music[:voice_duration]
            
            # Smooth music entry/exit to avoid abrupt starts/stops
            fade_ms = max(0, Config.MUSIC_FADE_MS)
            if fade_ms > 0:
                music = music.fade_in(fade_ms).fade_out(fade_ms)

            # Reduce music level relative to voice and add extra ducking headroom.
            if Config.MUSIC_VOLUME <= 0:
                gain_db = -120.0
            else:
                gain_db = 20.0 * math.log10(Config.MUSIC_VOLUME)
            music = music.apply_gain(gain_db - Config.MUSIC_DUCK_DB)
            
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

        if len(images) > 1 and Config.TRANSITION_SECONDS > 0:
            transitioned = self._create_video_with_transitions(images, duration)
            if transitioned:
                return transitioned
        
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
            "-preset", "slow",
            "-crf", "20",
            "-profile:v", "high",
            "-level", "4.2",
            "-movflags", "+faststart",
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
                "-preset", "slow",
                "-crf", "20",
                "-profile:v", "high",
                "-level", "4.2",
                "-movflags", "+faststart",
                "-pix_fmt", "yuv420p",
                "-r", str(Config.VIDEO_FPS),
                "-y",
                str(output_path)
            ]
            
            result = subprocess.run(cmd_simple, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path

    def _create_video_with_transitions(self, images: List[Path], duration: float) -> Path:
        """Create slideshow with gentle crossfade transitions between still images."""
        output_path = self.temp_dir / "slideshow_transitions.mp4"

        image_count = len(images)
        transition = max(0.0, Config.TRANSITION_SECONDS)
        clip_duration = max(2.0, duration / image_count)

        input_args = []
        for img in images:
            input_args.extend(["-loop", "1", "-t", f"{clip_duration}", "-i", str(img)])

        vfilters = []
        for index in range(image_count):
            vfilters.append(
                f"[{index}:v]scale={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={Config.VIDEO_WIDTH}:{Config.VIDEO_HEIGHT},"
                f"format=yuv420p,"
                f"settb=AVTB[v{index}]"
            )

        current = "v0"
        for index in range(1, image_count):
            offset = max(0.0, (clip_duration - transition) * index)
            out_tag = f"xf{index}"
            vfilters.append(
                f"[{current}][v{index}]xfade=transition=fade:duration={transition}:offset={offset}[{out_tag}]"
            )
            current = out_tag

        filter_complex = ";".join(vfilters)

        cmd = [
            "ffmpeg",
            *input_args,
            "-filter_complex", filter_complex,
            "-map", f"[{current}]",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "20",
            "-profile:v", "high",
            "-level", "4.2",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            "-r", str(Config.VIDEO_FPS),
            "-y",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Transitioned slideshow failed, falling back to basic slideshow...")
            return None

        if not output_path.exists() or output_path.stat().st_size == 0:
            print("Transitioned slideshow output was empty, falling back to basic slideshow...")
            return None

        return output_path
    
    def _combine_video_and_audio(
        self, 
        video_path: Path, 
        audio_path: Path, 
        output_path: Path,
        subtitle_text: str = None,
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
        subtitle_file = None
        use_subtitles = bool(subtitle_text and Config.SUBTITLES_ENABLED)

        if use_subtitles:
            duration = self._get_audio_duration(audio_path)
            subtitle_file = self._create_subtitle_file(subtitle_text, duration)

        if subtitle_file and subtitle_file.exists():
            subtitle_path = subtitle_file.resolve().as_posix().replace(":", "\\:")
            subtitle_filter = f"subtitles='{subtitle_path}'"
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-vf", subtitle_filter,
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "20",
                "-profile:v", "high",
                "-level", "4.2",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-shortest",
                "-y",
                str(output_path),
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-shortest",
                "-y",
                str(output_path)
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if subtitle_file and subtitle_file.exists():
                print("Subtitle burn-in failed, retrying without subtitles...")
                fallback_cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    "-shortest",
                    "-y",
                    str(output_path)
                ]
                fallback = subprocess.run(fallback_cmd, capture_output=True, text=True)
                if fallback.returncode == 0:
                    return output_path
            raise Exception(f"FFmpeg error combining video and audio: {result.stderr}")
        
        return output_path

    def _create_subtitle_file(self, script_text: str, duration: float) -> Path:
        """Create simple timed SRT subtitles from script text."""
        output_path = self.temp_dir / "auto_subtitles.srt"
        max_chars = max(20, Config.SUBTITLE_MAX_CHARS)
        min_seconds = max(1.0, Config.SUBTITLE_MIN_SECONDS)

        chunks = self._split_subtitle_chunks(script_text, max_chars)
        if not chunks:
            output_path.write_text("", encoding="utf-8")
            return output_path

        per_chunk = max(min_seconds, duration / len(chunks))
        max_index = max(0, int(duration / per_chunk) - 1)

        lines = []
        for index, chunk in enumerate(chunks[: max_index + 1], start=1):
            start = (index - 1) * per_chunk
            end = min(duration, index * per_chunk)
            lines.append(str(index))
            lines.append(f"{self._to_srt_time(start)} --> {self._to_srt_time(end)}")
            lines.append(chunk)
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def _split_subtitle_chunks(self, text: str, max_chars: int) -> List[str]:
        """Split narration text into subtitle-safe chunks."""
        cleaned = " ".join(text.replace("\n", " ").split())
        if not cleaned:
            return []

        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        chunks = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(sentence) <= max_chars:
                chunks.append(sentence)
                continue

            words = sentence.split()
            current = []
            current_len = 0
            for word in words:
                word_len = len(word) + (1 if current else 0)
                if current_len + word_len > max_chars and current:
                    chunks.append(" ".join(current))
                    current = [word]
                    current_len = len(word)
                else:
                    current.append(word)
                    current_len += word_len
            if current:
                chunks.append(" ".join(current))

        return chunks

    def _to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        total_ms = max(0, int(seconds * 1000))
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        secs = (total_ms % 60000) // 1000
        millis = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
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
