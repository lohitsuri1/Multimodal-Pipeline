# 🕉️ Quick Start Guide - Multimodal Pipeline

Generate **2 long videos + 8 shorts per week** across two channels automatically!

- **Channel A** – Finance / AI Tools / SaaS / Passive Income
- **Channel B** – Devotion / Spirituality (Radha Krishna)

---

## ⚡ 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt

# Install FFmpeg (required for video assembly)
# Ubuntu/Debian:
sudo apt-get install ffmpeg
# macOS:
brew install ffmpeg
```

### 2. Get Free API Keys

| Key | Required | Where |
|-----|----------|-------|
| OpenAI | ✅ Yes | https://platform.openai.com/api-keys |
| Pexels **or** Pixabay | ✅ Yes (pick one) | https://www.pexels.com/api/ or https://pixabay.com/api/docs/ |
| ElevenLabs | ❌ Optional | https://elevenlabs.io/ |

### 3. Configure

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 4. Run!

```bash
# Channel B (devotion) – long video + 4 shorts, current week's theme
python cli.py --channel B --output both

# Channel A (finance) – long video + 4 shorts, current week's theme
python cli.py --channel A --output both

# Custom theme
python cli.py --channel A --output both --theme "5 AI tools for passive income"

# Dry-run cost estimate (no API calls)
python cli.py --channel A --output both --dry-run
```

---

## 🎬 Weekly Production Workflow

To hit the **2 long videos + 8 shorts per week** target, run once per channel:

```bash
# Monday – Channel A (Finance)
python cli.py --channel A --output both --num-shorts 4

# Thursday – Channel B (Devotion)
python cli.py --channel B --output both --num-shorts 4
```

**Output per run:**
- 1 long-form video script (7–10 min)
- 4 short segments (60 s each, 9:16 format)
- 3 title options + 3 thumbnail text options
- Hook + caption + hashtags for every short

---

## 🖥️ CLI Reference

```
python cli.py [OPTIONS]

  --channel / -c    A|B|finance|devotion   (default: B)
  --output  / -o    long|shorts|both       (default: both)
  --cost-tier / -t  free|low|high          (default: free)
  --dry-run / -n    Estimate costs only, no API calls
  --theme           Override topic for this run
  --week / -w       ISO week number (default: current week)
  --num-shorts N    1–8 shorts per run     (default: 4)
  --no-cache        Bypass the output cache for this run
```

### Examples

```bash
# Cost estimate before spending anything
python cli.py --channel A --output both --dry-run --cost-tier high

# Generate only shorts for Channel B with a custom theme
python cli.py --channel B --output shorts --theme "Krishna's teachings on inner peace"

# Generate 8 shorts this week (Channel A, high quality)
python cli.py --channel A --output shorts --num-shorts 8 --cost-tier high
```

---

## 🌐 API Server (Optional)

Start the REST API:

```bash
# Set a secret key in .env first:
# PIPELINE_API_KEY=your_long_random_secret

uvicorn api_server:app --reload
# Docs at: http://localhost:8000/docs
```

Call the API:

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Generate title/thumbnail options
curl -X POST http://localhost:8000/api/generate/titles \
  -H "X-API-Key: your_long_random_secret" \
  -H "Content-Type: application/json" \
  -d '{"channel":"A","theme":"Best passive income ideas 2024"}'

# Extract shorts from a script
curl -X POST http://localhost:8000/api/generate/shorts \
  -H "X-API-Key: your_long_random_secret" \
  -H "Content-Type: application/json" \
  -d '{"script":"Your long script here...","num_shorts":4}'

# Dry-run cost estimate
curl -X POST http://localhost:8000/api/estimate \
  -H "X-API-Key: your_long_random_secret" \
  -H "Content-Type: application/json" \
  -d '{"channel":"A","output_type":"both","num_shorts":4}'
```

---

## 💰 Cost Decision Table

Use this table to choose the right tier for your budget:

| Tier | Script model | TTS | Images | Cost/week | Quality |
|------|-------------|-----|--------|-----------|---------|
| **Free** | GPT-3.5-turbo | gTTS | Pexels/Pixabay | ~$0.05 | Good |
| **Low** | GPT-3.5-turbo | ElevenLabs starter | Pexels/Pixabay | ~$1–3 | Better |
| **High** | GPT-4 | ElevenLabs professional | Pexels/Pixabay | ~$5–15 | Best |

### Recommended Minimal Paid Tiers

| Need | Recommended | Monthly cost |
|------|------------|-------------|
| Get started (test) | Free tier only | $0 |
| Consistent weekly output | OpenAI Pay-as-you-go | ~$2–5/mo |
| Better voice (audience retention) | ElevenLabs Starter ($5/mo) | $5/mo |
| Higher quality scripts | GPT-4 (Pay-as-you-go) | ~$10–20/mo |
| **Recommended sweet spot** | GPT-3.5 + ElevenLabs Starter | ~$7/mo |

### Free vs Paid Decision Guide

- ✅ **Use free** if: testing the pipeline, small audience, cost-sensitive
- ✅ **Use low tier** if: growing channel (1 k+ subscribers), want better voice
- ✅ **Use high tier** if: monetised channel, need GPT-4 script quality

---

## 🎵 Adding Background Music (Optional)

1. Download royalty-free music from:
   - [YouTube Audio Library](https://www.youtube.com/audiolibrary)
   - [Chosic Devotional](https://www.chosic.com/free-music/devotional/)

2. Place music file:
   ```bash
   mkdir -p temp_files/music
   # Rename your file to:
   # temp_files/music/background_music.mp3
   ```

3. **Important**: Add attribution in your video description!

---

## 🤖 Weekly Automation (GitHub Actions)

1. Go to your GitHub repository → Settings → Secrets
2. Add secrets: `OPENAI_API_KEY`, `PEXELS_API_KEY`, `PIPELINE_API_KEY`
3. The workflow runs every Sunday at 6 AM UTC

---

## ⚙️ Caching

Scripts, titles, and extracted shorts are cached automatically in `.cache/`
(excluded from git). Re-running with the same theme reuses cached results at
**zero API cost**.

To disable for one run: `python cli.py --no-cache ...`
To clear all cache: `python -c "from content_cache import ContentCache; print(ContentCache().clear(), 'entries cleared')"`

---

## ⚠️ Important Notes

### Copyright Compliance
- ✅ Scripts are AI-generated (original)
- ✅ Voice is synthesised (no copyright)
- ✅ Images are royalty-free (Pexels/Pixabay)
- ⚠️ Music must be royalty-free with attribution

### Always Add Attribution
```
Credits:
• Script: AI-generated original content
• Voice: Text-to-speech synthesis
• Images: Royalty-free from Pexels.com / Pixabay.com
• Music: [Track Name] by [Artist] - [License] - [Source]
```

---

## 🆘 Troubleshooting

| Error | Fix |
|-------|-----|
| `OpenAI API key not configured` | Add `OPENAI_API_KEY` to `.env` |
| `FFmpeg not found` | `sudo apt-get install ffmpeg` |
| `No images available` | Add `PEXELS_API_KEY` or `PIXABAY_API_KEY` to `.env` |
| `Missing package` | `pip install -r requirements.txt` |
| `Invalid API key` (API server) | Check `PIPELINE_API_KEY` in `.env` matches your request header |
| `Rate limit exceeded` | Wait 1 minute or increase `RATE_LIMIT_PER_MINUTE` in `.env` |

---

## 📚 Full Documentation

- **[DEVOTIONAL_PIPELINE_README.md](DEVOTIONAL_PIPELINE_README.md)** – Devotion pipeline details
- **[README.md](README.md)** – Project overview

---

## ✨ You're Ready!

```bash
# Validate your setup first
python test_pipeline.py

# Then generate your first week of content
python cli.py --channel A --output both --dry-run  # preview costs
python cli.py --channel A --output both             # Channel A
python cli.py --channel B --output both             # Channel B
```

Happy creating! 🙏
