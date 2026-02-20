# 🎬 Faceless Content Creation Guide

> Two channels · 2 long videos + 8 shorts per week · YouTube + Instagram

---

## Channels at a Glance

| Channel | Preset | Topics |
|---------|--------|--------|
| Finance & AI/SaaS | `finance_ai_saas` | AI tools, SaaS, passive income, personal finance |
| Devotion & Spirituality | `devotional` | Radha Krishna, meditation, Bhagavad Gita |

---

## Recommended Weekly Workflow (2 long + 8 shorts / week)

```
Mon  → Long video for Finance/AI channel
       python quick_start.py --preset finance_ai_saas --output both --tier free

Wed  → Long video for Devotional channel
       python quick_start.py --preset devotional --output both --tier free

       (Both commands produce 1 long script + 4 shorts each = 2 longs + 8 shorts/week)
```

To customise the theme:
```bash
python quick_start.py \
  --preset finance_ai_saas \
  --output both \
  --theme "5 AI Tools That Replace a Full Marketing Team" \
  --shorts-count 4
```

---

## Quick Start

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env and add OPENAI_API_KEY + at least one of PEXELS_API_KEY / PIXABAY_API_KEY
```

### 3. Estimate usage before spending money
```bash
python quick_start.py --preset finance_ai_saas --output both --dry-run
```

### 4. Generate content
```bash
# Full pipeline: long script + shorts
python quick_start.py --preset finance_ai_saas --output both

# Long script only
python quick_start.py --preset devotional --output long

# Extract shorts from existing script (re-uses cache)
python quick_start.py --preset devotional --output shorts
```

---

## CLI Reference

```
python quick_start.py [OPTIONS]

Options:
  --preset    finance_ai_saas | devotional   Channel preset (default: devotional)
  --output    long | shorts | both           What to generate  (default: both)
  --tier      free | low_cost | hq           Quality tier      (default: free)
  --theme     "Custom topic"                 Override auto-rotation
  --shorts-count N                           1–8 shorts        (default: 4)
  --dry-run                                  Estimate usage, no paid API calls
```

---

## Cost Tiers

| Tier | TTS | Images | LLM model | Approx cost per video |
|------|-----|--------|-----------|-----------------------|
| `free` | gTTS (Google, free) | Pexels / Pixabay (free) | GPT-4 | ~$0.10–0.20 |
| `low_cost` | gTTS | Pexels / Pixabay | GPT-4 | ~$0.10–0.20 |
| `hq` | ElevenLabs | Pexels / Pixabay | GPT-4 | ~$0.30–0.50 + ElevenLabs credits |

**Minimal purchases guidance**

- Start with **`free`** tier — OpenAI GPT-4 is the only paid service needed.
- Upgrade to **`hq`** only when you are satisfied with your content calendar and
  want better-sounding narration.
- ElevenLabs free tier: 10,000 characters/month — enough for ~2 short scripts.
- Upgrade trigger: when your channel reaches >1,000 subscribers or >$50/month revenue.

---

## Caching

The pipeline caches all expensive outputs to `.cache/` so **re-running with the same
inputs costs nothing**.

```
.cache/
  scripts/      — long-form scripts (JSON)
  titles/       — title + thumbnail options
  shorts/       — extracted shorts
  tts/          — audio files (.mp3)
  api_responses/— API server response cache
```

To force regeneration, delete the relevant cache file or the whole `.cache/` directory.

---

## API Server

Start the REST API:
```bash
uvicorn api_server:app --reload
# Docs: http://localhost:8000/docs
```

Protect the API with an API key:
```bash
# .env
API_KEY=my-secret-key

# Request
curl -X POST http://localhost:8000/api/generate \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"preset":"finance_ai_saas","output":"both","tier":"free","dry_run":true}'
```

Rate limiting is enforced per IP (default: 10 requests/minute, configurable via
`RATE_LIMIT_PER_MINUTE` in `.env`).

---

## Platform Packaging

Each preset outputs platform cues for three surfaces:

| Surface | Aspect | Max length | Notes |
|---------|--------|------------|-------|
| YouTube Long | 16:9 | No limit | Chapter markers per section |
| YouTube Shorts | 9:16 | 60 s | Hook text on screen, burned-in captions |
| Instagram Reels | 9:16 | 90 s | Hook in first 2 s, captions at bottom third |

---

## Customising Presets

Edit `content_presets.py` to:
- Add more themes to `default_themes`
- Adjust the `long_form_user_template` structure
- Change b-roll keywords in `default_broll_keywords`
- Add new presets to the `PRESETS` registry

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `OPENAI_API_KEY is not set` | Copy `.env.example` → `.env` and add your key |
| `No images fetched` | Add `PEXELS_API_KEY` or `PIXABAY_API_KEY` to `.env` |
| `FFmpeg not found` | `sudo apt-get install ffmpeg` / `brew install ffmpeg` |
| `Rate limit exceeded` | Increase `RATE_LIMIT_PER_MINUTE` in `.env` |
| Cache stale | Delete `.cache/<subdir>/<key>.json` |
