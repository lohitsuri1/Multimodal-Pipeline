# 🎬 Multimodal Pipeline

> **Build autonomous AI systems that generate videos weekly - without writing complex code**

![Stars](https://img.shields.io/badge/stars-%E2%AD%90%E2%AD%90%E2%AD%90%E2%AD%90%E2%AD%90-brightgreen)
![Status](https://img.shields.io/badge/status-production--ready-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)

---

## ⚡ Generate Videos in 4 Steps

### 1. Install

```bash
git clone https://github.com/lohitsuri1/Multimodal-Pipeline.git
cd Multimodal-Pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Open .env and fill in your API keys (see Next Steps below)
```

### 3. Run

```bash
# Estimate cost before spending anything
python cli.py --niche finance --dry-run

# Generate a video (replace "finance" with your chosen niche)
python cli.py --niche finance --output-type both
```

Available niches: `finance`, `ai_saas`, `passive_income`, `devotion`

### 4. Find Your Output

Generated scripts and video assets are saved to the `output_videos/` directory created in the project root.

---

## 🔜 Next Steps

### 🔑 How to Fetch API Details

| Service | Sign-up / Dashboard | What to copy |
|---------|---------------------|--------------|
| **OpenAI** | https://platform.openai.com/api-keys | API key, model name (e.g. `gpt-4o-mini`) |
| **ElevenLabs** (optional TTS) | https://elevenlabs.io/ | API key |
| **Replicate** (optional images) | https://replicate.com/ | API token |
| **Pexels** (free stock images) | https://www.pexels.com/api/ | API key |
| **Pixabay** (free stock images) | https://pixabay.com/api/docs/ | API key |

Add each value to your `.env` file:

```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
ELEVENLABS_API_KEY=...   # optional
REPLICATE_API_TOKEN=...  # optional
PEXELS_API_KEY=...
PIXABAY_API_KEY=...
```

### 💰 How to Purchase at Minimum Cost

- **Start free** — OpenAI gives new accounts free trial credits; use them first.
- **Pick the cheapest model** — `gpt-3.5-turbo` costs ~$0.00/run; upgrade to `gpt-4o-mini` (~$0.02/run) only when needed.
- **Use free image sources** — Pexels and Pixabay are free for commercial use; no image-generation costs required.
- **Skip paid TTS** — the default voice (gTTS) is completely free; upgrade to ElevenLabs only for a more natural voice.
- **Set a usage limit** — in the OpenAI dashboard, set a monthly budget alert so you never get a surprise bill.
- **Use `--dry-run`** — always estimate cost before running: `python cli.py --niche finance --dry-run`
- **Enable caching** — re-running the same niche + theme reuses cached results and skips paid API calls (`ENABLE_CACHE=true` in `.env`).
