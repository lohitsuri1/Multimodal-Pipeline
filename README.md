# 🎬 Multimodal Pipeline - 5-Level AI Roadmap

> **Build autonomous AI systems that generate investment videos weekly - without writing complex code**

![Stars](https://img.shields.io/badge/stars-%E2%AD%90%E2%AD%90%E2%AD%90%E2%AD%90%E2%AD%90-brightgreen)
![Status](https://img.shields.io/badge/status-production--ready-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)

## 🚀 What is This?

This is a **complete implementation of the 5-Level AI Roadmap** that enables you to:

✅ Structure prompts scientifically (PRD Method)
✅ Connect AI to your data (RAG + Vector DB)
✅ Generate multimodal content (Text + Images + Video + Audio)
✅ Deploy autonomous AI agents (24/7 automation)
✅ Build professional REST API (Super App)

**Real-world use case**: Generate a professional 90-second investment video **every week automatically** 📺

---

## 🎯 The 5 Levels

```
Level 1: Foundations & PRD Method
   ↓ Structure prompts systematically
   
Level 2: Context, RAG & MCP
   ↓ Connect to your personal data
   
Level 3: Multimodal (One-Person Agency)
   ↓ Generate video + audio + visuals
   
Level 4: AI Agents
   ↓ Autonomous systems running 24/7
   
Level 5: Vibe Coding (Super App)
   ↓ REST API for easy integration
   
Result: 🎥 Complete video generation pipeline
```

---

## 📦 What's Included

### Core Files (The 5 Levels)
```
level1_prd_framework.py      → Structure prompts as PRDs
level2_rag_pipeline.py       → Query your data intelligently
level3_multimodal_engine.py  → Create video/audio/images
level4_ai_agents.py          → Autonomous agents
level5_super_app.py          → REST API endpoints
```

### Support System
```
orchestrator.py              → Ties all 5 levels together
config.py                    → Configuration management
utils.py                     → Logging & utilities
quick_start.py               → Interactive demo menu
```

### Documentation (📚 Start here!)
```
INDEX.md                     → Navigation guide
IMPLEMENTATION_SUMMARY.md    → Overview & features
SETUP_GUIDE.md               → Installation steps
README_5LEVEL_ROADMAP.md     → Complete technical docs
```

---

## ⚡ Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/lohitsuri1/Multimodal-Pipeline.git
cd Multimodal-Pipeline
```

### 2. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your OpenAI, Replicate, ElevenLabs keys
```

### 4. Run Interactive Demo
```bash
python quick_start.py
```

That's it! You'll see an interactive menu to try everything.

---

## 🎬 Real-World Example

### Generate an Investment Video

```python
from orchestrator import AIRoadmapOrchestrator
from config import Config

# Initialize
orchestrator = AIRoadmapOrchestrator({
    "data_dir": Config.DATA_DIR,
    "api_keys": Config.get_api_keys()
})

# Generate video
result = orchestrator.execute_full_pipeline(
    topic="Indian Stock Market Weekly Insights",
    duration=90
)

print(f"Video created: {result['status']}")
# Output: Video created: ready_for_publishing
```

**What happens automatically:**
1. ✅ Level 1: Creates PRD structure
2. ✅ Level 2: Queries market data with RAG
3. ✅ Level 3: Generates script, visuals, narration
4. ✅ Level 4: Runs AI agent analysis
5. ✅ Level 5: Prepares for publishing

---

## 🌐 Use as REST API

```bash
# Start the API
uvicorn level5_super_app:app --reload

# In another terminal, generate a video
curl -X POST "http://localhost:8000/api/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Indian Tech Sector Performance",
    "duration": 90,
    "target_audience": "investors"
  }'

# Check docs
open http://localhost:8000/docs
```

---

## 📊 Architecture

```
                     User Input
                        ↓
        ┌───────────────────────────────┐
        │  Level 1: PRD Framework       │  Structure prompts
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Level 2: RAG Pipeline        │  Query your data
        │  (Vector Database)            │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Level 3: Multimodal Engine   │  Generate content
        │  (GPT4, Replicate, 11Labs)    │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Level 4: AI Agents           │  Analyze & create
        │  (CrewAI)                     │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  Level 5: Super App (FastAPI) │  REST API
        └───────────────────────────────┘
                        ↓
                 🎥 Output Video
```

---

## 🔑 Key Features

### 🎯 Intelligent Prompting
- Structure prompts like product requirements
- Ensure consistent, high-quality outputs
- Level 1: PRD Framework

### 🧠 Personal Data Integration
- Load your CSV/TXT files
- Smart retrieval with vector embeddings
- Cached for performance
- Level 2: RAG Pipeline

### 🎬 Content Generation
- Text scripts (GPT-4)
- Images (Replicate)
- Audio narration (ElevenLabs)
- Video assembly (FFmpeg)
- Level 3: Multimodal Engine

### 🤖 Automation
- Autonomous AI agents
- Market analysis
- Risk assessment
- Weekly scheduling
- Level 4: AI Agents

### 📡 Easy Integration
- REST API endpoints
- Interactive documentation
- Background task processing
- Level 5: Super App

---

## 📚 Documentation

| Document | Read Time | Content |
|----------|-----------|---------|
| **[INDEX.md](INDEX.md)** | 5 min | Navigation guide for all docs |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | 10 min | Overview, features, quick examples |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | 20 min | Step-by-step setup (recommended) |
| **[README_5LEVEL_ROADMAP.md](README_5LEVEL_ROADMAP.md)** | 30 min | Complete technical documentation |

**👉 Start with INDEX.md for quick navigation!**

---

## 💻 System Requirements

- Python 3.10+
- 2GB RAM minimum
- Internet connection (for APIs)
- 3 API keys:
  - OpenAI (GPT-4)
  - Replicate (Image generation)
  - ElevenLabs (Text-to-speech)

---

## 🚀 Usage Patterns

### Pattern 1: One-Time Video
```bash
python orchestrator.py
```

### Pattern 2: Weekly Automation
```bash
# Edit orchestrator.py, then run:
python orchestrator.py  # Starts scheduler
```

### Pattern 3: REST API
```bash
uvicorn level5_super_app:app --reload
# Now access API at http://localhost:8000
```

### Pattern 4: Interactive Demo
```bash
python quick_start.py
# Try all levels one by one
```

---

## 📊 Performance

Expected metrics:
- **Script Generation**: 30-60 seconds
- **Image Generation**: 2-5 minutes
- **Audio Narration**: 5-10 seconds
- **Video Assembly**: 1-2 minutes
- **Complete Pipeline**: 5-10 minutes

---

## 🔐 Security

- ✅ API keys stored in `.env` (not committed to git)
- ✅ Sensitive data doesn't leave your system
- ✅ Use `.env.example` as template
- ✅ Never commit `.env` to version control

---

## 🆘 Troubleshooting

**API Key Errors?**
```bash
# Check .env file exists and has valid keys
cat .env
```

**RAG not working?**
```bash
# Ensure market_data directory has .txt files
ls market_data/
```

**FFmpeg not found?**
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
choco install ffmpeg  # Windows
```

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for more troubleshooting.

---

## 📈 What You Can Build

With this framework, you can:

✅ **Investment Video Generator** - Weekly market analysis videos
✅ **Educational Content** - Auto-generate tutorials on any topic
✅ **News Aggregator** - Daily news summary videos
✅ **Portfolio Monitor** - Automated investment updates
✅ **Marketing Agency** - One-person video content studio
✅ **Personal Brand** - Consistent weekly content

---

## 🎓 Learning Resources

- **Video**: [Vaibhav Sisinty - 5-Level AI Roadmap](https://www.youtube.com/watch?v=btLZQzynfoA&t=864s)
- **LangChain**: [Python Documentation](https://python.langchain.com/)
- **FastAPI**: [Modern Web Framework](https://fastapi.tiangolo.com/)
- **CrewAI**: [Autonomous Agents](https://docs.crewai.com/)

---

## 📝 Project Structure

```
Multimodal-Pipeline/
├── 📚 Documentation
│   ├── INDEX.md                     ← Start here!
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── SETUP_GUIDE.md
│   └── README_5LEVEL_ROADMAP.md
│
├── 💻 Implementation (5 Levels)
│   ├── level1_prd_framework.py
│   ├── level2_rag_pipeline.py
│   ├── level3_multimodal_engine.py
│   ├── level4_ai_agents.py
│   └── level5_super_app.py
│
├── ⚙️ System Files
│   ├── orchestrator.py              ← Main entry point
│   ├── config.py                    ← Configuration
│   ├── utils.py                     ← Utilities
│   ├── quick_start.py               ← Interactive demo
│   └── requirements.txt              ← Dependencies
│
├── 📂 Data & Config
│   ├── .env.example                 ← Key template
│   ├── .env                         ← Your keys (create this)
│   ├── market_data/                 ← Your data files
│   └── output_videos/               ← Generated videos
│
└── 📊 Generated Files (auto-created)
    └── chroma_db/                   ← Vector database
```

---

## 🎯 Next Steps

1. 📖 **Read**: [INDEX.md](INDEX.md) (5 minutes)
2. 🚀 **Setup**: Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) (20 minutes)
3. 💻 **Run**: Execute `python quick_start.py`
4. 🎬 **Generate**: Create your first video!

---

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - Feel free to use for personal and commercial projects.

---

## 🙏 Credits

Based on **"5-Level AI Roadmap"** framework by Vaibhav Sisinty

Special thanks to:
- OpenAI (GPT-4)
- Replicate (Image generation)
- ElevenLabs (Text-to-speech)
- LangChain (RAG framework)
- FastAPI (API framework)

---

## 📞 Support

- 📖 **Questions?** See [INDEX.md](INDEX.md) for documentation navigation
- 🐛 **Issues?** Check [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting
- 💡 **Ideas?** Open an issue or submit a PR

---

## 🌟 Show Your Support

If you find this helpful, please:
- ⭐ Star the repository
- 🔗 Share with friends
- 📢 Mention in discussions
- 🤝 Contribute improvements

---

## 📊 Status

- ✅ Core implementation complete
- ✅ Documentation complete
- ✅ Setup guide complete
- ✅ Demo system ready
- ✅ Production ready

---

**Happy building! Let's create autonomous AI systems together.** 🚀

👉 **[Start with INDEX.md](INDEX.md)**