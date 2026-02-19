# 🕉️ Devotional Video Automation Pipeline

Automated pipeline to generate 30-minute devotional videos about Radha Krishna every week using AI and copyright-safe content.

## 📖 Overview

This pipeline automatically creates devotional meditation videos by:
- ✅ Generating original devotional scripts using AI (OpenAI GPT-4)
- ✅ Creating voice narration (Google Text-to-Speech or ElevenLabs)
- ✅ Fetching royalty-free spiritual visuals (Pexels/Pixabay APIs)
- ✅ Combining with devotional background music
- ✅ Composing everything into a professional 30-minute video
- ✅ Running automatically every week via GitHub Actions

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- FFmpeg (for video processing)
- API keys (see Configuration section)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/lohitsuri1/Multimodal-Pipeline.git
cd Multimodal-Pipeline

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### 3. Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
# Required: OpenAI for script generation
OPENAI_API_KEY=your_openai_key_here

# Required: At least one for images
PEXELS_API_KEY=your_pexels_key_here
# OR
PIXABAY_API_KEY=your_pixabay_key_here

# Optional: For better voice quality
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

#### Getting API Keys (All FREE):

1. **OpenAI** (Required): https://platform.openai.com/api-keys
   - Free tier available with limited credits
   - Used for generating devotional scripts

2. **Pexels** (Required - Option 1): https://www.pexels.com/api/
   - Completely free, no credit card required
   - 200 requests/hour, 20,000/month
   - Used for royalty-free images

3. **Pixabay** (Required - Option 2): https://pixabay.com/api/docs/
   - Completely free, no credit card required
   - 5,000 requests/hour
   - Alternative to Pexels

4. **ElevenLabs** (Optional): https://elevenlabs.io/
   - Free tier: 10,000 characters/month
   - Better voice quality than default (gTTS)

### 4. Run the Pipeline

```bash
python devotional_pipeline.py
```

The pipeline will:
1. Generate a devotional script about Radha Krishna
2. Create voice narration
3. Fetch copyright-safe spiritual images
4. Compose the final 30-minute video
5. Save output to `output_videos/`

## 📁 Project Structure

```
Multimodal-Pipeline/
├── devotional_pipeline.py      # Main orchestrator
├── script_generator.py         # AI script generation
├── voice_narrator.py           # Text-to-speech
├── visual_assets.py            # Image fetching
├── music_handler.py            # Background music
├── video_compositor.py         # Video assembly
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example               # Configuration template
├── .github/workflows/         # Automation
│   └── weekly-video.yml       # Weekly scheduler
└── output_videos/             # Generated videos (created)
```

## 🎵 Adding Background Music

The pipeline supports royalty-free devotional background music:

1. Download music from these copyright-safe sources:
   - [YouTube Audio Library](https://www.youtube.com/audiolibrary) - Free for YouTube
   - [Chosic Devotional Music](https://www.chosic.com/free-music/devotional/) - Royalty-free
   - [Incompetech](https://incompetech.com/music/royalty-free/) - CC BY 4.0

2. Create a music directory:
   ```bash
   mkdir -p temp_files/music
   ```

3. Place your music file as:
   ```
   temp_files/music/background_music.mp3
   ```

4. **IMPORTANT**: Always add attribution in your video description!

Example attribution:
```
Music: [Track Name] by [Artist]
Source: [Website]
License: [License Type]
```

## 🤖 Weekly Automation

The pipeline can run automatically every week using GitHub Actions.

### Setup:

1. **Add Secrets to GitHub Repository**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `OPENAI_API_KEY`
     - `PEXELS_API_KEY` or `PIXABAY_API_KEY`
     - `ELEVENLABS_API_KEY` (optional)

2. **The workflow will run**:
   - Automatically every Sunday at 6:00 AM UTC
   - Or manually via "Actions" tab → "Run workflow"

3. **Access generated videos**:
   - Go to "Actions" tab
   - Click on the latest workflow run
   - Download artifacts (video + script)

### Manual Trigger:

1. Go to repository "Actions" tab
2. Select "Weekly Devotional Video Generation"
3. Click "Run workflow"

## 📝 Weekly Themes

The pipeline automatically rotates through 12 devotional themes:

1. The Divine Love of Radha and Krishna
2. Krishna's Teachings on Dharma
3. Radha's Devotion and Surrender
4. The Flute of Krishna - Call to the Soul
5. Rasleela - The Divine Dance
6. Krishna's Childhood - Innocence and Joy
7. Radha's Separation - Deepening Devotion
8. Krishna as the Supreme Friend
9. The Gopis' Love - Pure Devotion
10. Krishna's Message in the Bhagavad Gita
11. Radha's Grace and Compassion
12. The Yamuna River - Sacred Waters

Each week automatically selects the next theme in rotation.

## ⚖️ Copyright Compliance

This pipeline is designed to be 100% copyright-safe:

### Content Sources:
- **Scripts**: Generated by AI (original content)
- **Voice**: Synthesized (no copyright issues)
- **Images**: Royalty-free from Pexels/Pixabay (proper attribution)
- **Music**: User-provided royalty-free tracks (attribution required)

### Important Notes:
1. ✅ All generated content is original
2. ✅ Images are from verified royalty-free sources
3. ✅ Music must be from royalty-free sources
4. ⚠️ **Always add proper attribution** for images and music
5. ⚠️ Review license terms for each resource used

### Attribution Template:

```
Video Description:
═══════════════════════════════════════

🕉️ 30-Minute Radha Krishna Devotional Meditation

This is a peaceful meditation video featuring teachings about
the divine love of Radha and Krishna.

Credits:
--------
• Script: AI-generated original content
• Voice: Text-to-speech synthesis
• Images: Royalty-free from Pexels/Pixabay
• Music: [Track Name] by [Artist] - [License] - [Source URL]

Image Attribution:
• Photos by various photographers on Pexels.com
• Licensed under Pexels License (Free for personal and commercial use)

All content is used in accordance with the respective licenses.
```

## 🎬 Output Format

**Video Specifications**:
- Duration: 30 minutes
- Resolution: 1920x1080 (Full HD)
- Format: MP4 (H.264 video, AAC audio)
- Frame Rate: 30 fps
- Visual Style: Slow pan/zoom on devotional images
- Audio: Voice narration with soft background music

**Additional Files**:
- Script text file (for reference)
- Timestamps for segments

## 🔧 Customization

### Change Video Duration:

Edit `.env`:
```env
VIDEO_DURATION_MINUTES=45  # For 45-minute videos
```

### Change Voice Settings:

Edit `.env`:
```env
VOICE_LANGUAGE=hi          # For Hindi
VOICE_SPEED=0.8           # Slower pace
MUSIC_VOLUME=0.15         # Quieter music
```

### Custom Themes:

Edit `devotional_pipeline.py` and modify the themes list in `generate_video()`.

## 🐛 Troubleshooting

### FFmpeg not found:
```bash
# Install FFmpeg for your system
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### API Key Errors:
- Verify keys in `.env` file
- Check that `.env` is in the project root
- Ensure no quotes around keys

### No Images Fetched:
1. Check API keys are valid
2. Verify internet connection
3. Try alternative API (Pixabay if Pexels fails)
4. Manual option: Download images to `temp_files/images/`

### Low Voice Quality:
- Add ElevenLabs API key for better quality
- Or use the free tier (10,000 chars/month)

### Video Too Long/Short:
- Adjust `VIDEO_DURATION_MINUTES` in `.env`
- Check that images duration matches audio

## 📊 Cost Estimate

Using maximum free tiers:

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| OpenAI | $5 credits | ~$0-2 (4-5 videos) |
| Pexels | Unlimited | $0 |
| gTTS | Unlimited | $0 |
| GitHub Actions | 2,000 min/month | $0 |
| **Total** | | **~$0-2/month** |

Optional upgrades:
- ElevenLabs: $0 (10K chars free) or $5/month for more

## 🎯 Use Cases

- Daily devotional content creators
- Meditation channels
- Spiritual education
- Temple social media
- Personal spiritual practice
- YouTube devotional channels

## 📜 License

MIT License - Free for personal and commercial use.

## 🙏 Credits

**Technology Stack**:
- OpenAI GPT-4 (Script generation)
- Google TTS / ElevenLabs (Voice)
- Pexels / Pixabay (Images)
- FFmpeg (Video processing)
- Python ecosystem

**Inspiration**:
Based on copyright guidelines from the Devotion file in this repository.

## 📞 Support

- 📖 Documentation: This README
- 🐛 Issues: GitHub Issues
- 💡 Ideas: Pull Requests welcome

## ⚠️ Disclaimer

This tool helps create devotional content for spiritual purposes. Users are responsible for:
- Verifying all licenses and attributions
- Complying with platform policies (YouTube, etc.)
- Respecting copyright and intellectual property laws
- Using content appropriately and respectfully

---

**Made with 🙏 for the devotional community**

Happy creating! May your content bring peace and devotion to viewers. 🕉️
