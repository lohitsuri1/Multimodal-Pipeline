# 🕉️ Quick Start Guide - Devotional Video Pipeline

Generate 30-minute Radha Krishna devotional videos automatically!

## ⚡ 5-Minute Setup

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg
```

### 2. Get Free API Keys

You'll need these FREE API keys:

1. **OpenAI** (Required): https://platform.openai.com/api-keys
   - Used for generating devotional scripts
   - Free tier with limited credits

2. **Pexels** OR **Pixabay** (Pick one - both free):
   - Pexels: https://www.pexels.com/api/
   - Pixabay: https://pixabay.com/api/docs/
   - Used for royalty-free images
   - No credit card required

3. **ElevenLabs** (Optional): https://elevenlabs.io/
   - Better voice quality
   - Free tier: 10,000 chars/month
   - If skipped, uses Google TTS (also free)

### 3. Configure

#### Option A: Use Setup Wizard (Recommended)
```bash
python setup_wizard.py
```
The wizard will guide you through entering your API keys.

#### Option B: Manual Setup
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Run!

```bash
python devotional_pipeline.py
```

The pipeline will:
1. Generate a devotional script (2-3 minutes)
2. Create voice narration (1-2 minutes)
3. Fetch spiritual images (2-3 minutes)
4. Compose the final video (3-5 minutes)

Total time: ~10 minutes

Output: `output_videos/devotional_video_YYYYMMDD_HHMMSS.mp4`

## 🎵 Adding Background Music (Optional)

1. Download royalty-free devotional music from:
   - [YouTube Audio Library](https://www.youtube.com/audiolibrary)
   - [Chosic Devotional](https://www.chosic.com/free-music/devotional/)

2. Place music file:
   ```bash
   mkdir -p temp_files/music
   # Copy your music file as:
   # temp_files/music/background_music.mp3
   ```

3. **Important**: Add attribution in your video description!

## 🤖 Weekly Automation

Set up GitHub Actions to generate videos automatically every Sunday:

1. Go to your GitHub repository → Settings → Secrets
2. Add these secrets:
   - `OPENAI_API_KEY`
   - `PEXELS_API_KEY` or `PIXABAY_API_KEY`
   - `ELEVENLABS_API_KEY` (optional)

3. The workflow runs every Sunday at 6 AM UTC
4. Download generated videos from the "Actions" tab

## 📊 What You'll Get

- **Duration**: 30 minutes
- **Resolution**: 1920x1080 (Full HD)
- **Content**: Original devotional script about Radha Krishna
- **Visuals**: Rotating spiritual images with Ken Burns effect
- **Audio**: Voice narration + optional background music
- **Format**: MP4 (H.264)

## 🎯 Weekly Themes

The pipeline automatically rotates through 12 themes:
1. The Divine Love of Radha and Krishna
2. Krishna's Teachings on Dharma
3. Radha's Devotion and Surrender
4. The Flute of Krishna - Call to the Soul
5. Rasleela - The Divine Dance
6. Krishna's Childhood - Innocence and Joy
... and 6 more!

## ⚠️ Important Notes

### Copyright Compliance
- ✅ Scripts are AI-generated (original)
- ✅ Voice is synthesized (no copyright)
- ✅ Images are royalty-free (Pexels/Pixabay)
- ⚠️ Music must be royalty-free with attribution

### Always Add Attribution
When using music or images, include credits in your video description:

```
Credits:
• Script: AI-generated original content
• Voice: Text-to-speech synthesis
• Images: Royalty-free from Pexels.com / Pixabay.com
• Music: [Track Name] by [Artist] - [License] - [Source]
```

## 🆘 Troubleshooting

### "OpenAI API key not configured"
→ Make sure you created `.env` and added `OPENAI_API_KEY=your_key`

### "FFmpeg not found"
→ Install FFmpeg: `sudo apt-get install ffmpeg` (Ubuntu)

### "No images available"
→ Add `PEXELS_API_KEY` or `PIXABAY_API_KEY` to `.env`

### "Missing package"
→ Run `pip install -r requirements.txt`

## 📚 Full Documentation

For complete documentation, see:
- **[DEVOTIONAL_PIPELINE_README.md](DEVOTIONAL_PIPELINE_README.md)** - Complete guide
- **[README.md](README.md)** - Project overview

## 💰 Cost Estimate

Using free tiers:
- OpenAI: ~$0-2/month (4-5 videos)
- Pexels/Pixabay: $0 (unlimited)
- gTTS: $0 (unlimited)
- GitHub Actions: $0 (2000 min/month free)

**Total: ~$0-2/month** for weekly videos

## 🎬 Example Usage

```python
# Or use the Python API directly
from devotional_pipeline import DevotionalVideoPipeline

pipeline = DevotionalVideoPipeline()
video_path = pipeline.generate_video(
    theme="The Divine Love of Radha and Krishna",
    week_number=1
)
print(f"Video created: {video_path}")
```

## ✨ You're Ready!

Run your first video generation:
```bash
python devotional_pipeline.py
```

Happy creating! 🙏
