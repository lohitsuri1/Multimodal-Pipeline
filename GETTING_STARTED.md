# 🕉️ Getting Started - Your First Devotional Video

Complete step-by-step guide to generate your first Radha Krishna devotional video in 15 minutes.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.10 or higher installed
- [ ] Git installed
- [ ] Internet connection
- [ ] 15 minutes of time

## 🚀 Step-by-Step Guide

### Step 1: Clone the Repository (1 minute)

```bash
git clone https://github.com/lohitsuri1/Multimodal-Pipeline.git
cd Multimodal-Pipeline
```

### Step 2: Install Dependencies (2-3 minutes)

#### On Ubuntu/Debian:
```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg
```

#### On macOS:
```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg
brew install ffmpeg
```

#### On Windows:
```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg
# Download from: https://ffmpeg.org/download.html
# Add to PATH
```

### Step 3: Get Free API Keys (5-7 minutes)

You need these FREE API keys:

#### 3.1 OpenAI API Key (Required)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **Note**: Free tier includes $5 in credits

#### 3.2 Pexels API Key (Required - Option 1)
1. Go to https://www.pexels.com/api/
2. Click "Get Started"
3. Fill out the form (takes 30 seconds)
4. Receive API key instantly
5. **Note**: Completely free, no credit card needed

**OR**

#### 3.2 Pixabay API Key (Required - Option 2)
1. Go to https://pixabay.com/api/docs/
2. Sign up for free account
3. Find your API key in documentation
4. Copy the key
5. **Note**: Completely free, no credit card needed

#### 3.3 ElevenLabs API Key (Optional)
1. Go to https://elevenlabs.io/
2. Sign up for free account
3. Go to Profile → API Keys
4. Copy your key
5. **Note**: Free tier gives 10,000 characters/month
6. **Skip if you want**: Default voice (gTTS) is also good

### Step 4: Configure Your API Keys (2 minutes)

#### Option A: Use the Setup Wizard (Recommended)
```bash
python setup_wizard.py
```

The wizard will:
- Check your system
- Ask for your API keys
- Create the `.env` file
- Validate everything

Just follow the prompts!

#### Option B: Manual Configuration
```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env
# or
vim .env
# or
code .env
```

Add your keys:
```env
OPENAI_API_KEY=sk-your-actual-key-here
PEXELS_API_KEY=your-pexels-key-here
PIXABAY_API_KEY=your-pixabay-key-here  # if using Pixabay instead
ELEVENLABS_API_KEY=your-elevenlabs-key  # optional
```

Save and close the file.

### Step 5: Generate Your First Video! (10 minutes)

```bash
python devotional_pipeline.py
```

#### What Happens:
1. **Script Generation** (2-3 min): AI creates devotional content
2. **Voice Narration** (1-2 min): Converts script to speech
3. **Image Fetching** (2-3 min): Downloads spiritual images
4. **Video Assembly** (3-5 min): Combines everything

#### Progress Output:
```
======================================================================
🕉️  DEVOTIONAL VIDEO GENERATION PIPELINE
======================================================================

[1/5] Generating devotional script...
✓ Generated script with 6 segments
   Theme: The Divine Love of Radha and Krishna

[2/5] Generating voice narration...
✓ Voice narration created: temp_files/narration/full_narration.mp3

[3/5] Fetching devotional visual assets...
✓ Fetched 30 images

[4/5] Preparing background music...
⚠️  No background music found
(Optional - see instructions below)

[5/5] Composing final video...
✓ Video created successfully: output_videos/devotional_video_20240219_123456.mp4

======================================================================
✓ VIDEO GENERATION COMPLETE!
======================================================================

Output: output_videos/devotional_video_20240219_123456.mp4
Duration: ~30 minutes
Theme: The Divine Love of Radha and Krishna
Script saved: output_videos/devotional_video_20240219_123456_script.txt

✨ Success! Your devotional video is ready.
```

### Step 6: Watch Your Video! (30 minutes)

Your video is in the `output_videos/` directory:
```bash
# List generated videos
ls output_videos/

# Open the video
# On Linux:
xdg-open output_videos/devotional_video_*.mp4

# On macOS:
open output_videos/devotional_video_*.mp4

# On Windows:
start output_videos/devotional_video_*.mp4
```

## 🎵 Optional: Add Background Music

To enhance your video with devotional music:

### 1. Get Royalty-Free Music

Download from these sources:

**Option 1: YouTube Audio Library** (Recommended)
- Go to: https://www.youtube.com/audiolibrary
- Search: "indian", "meditation", "spiritual"
- Download MP3

**Option 2: Chosic**
- Go to: https://www.chosic.com/free-music/devotional/
- Browse devotional tracks
- Download with attribution info

**Option 3: Incompetech**
- Go to: https://incompetech.com/music/royalty-free/
- Search: "indian" or "world"
- Download with license info

### 2. Add Music to Pipeline

```bash
# Create music directory
mkdir -p temp_files/music

# Copy your downloaded music file
cp ~/Downloads/devotional-music.mp3 temp_files/music/background_music.mp3
```

### 3. Run Pipeline Again

```bash
python devotional_pipeline.py
```

Now your video will include background music!

### 4. Important: Add Attribution

When you upload the video, add this to your description:

```
Music: [Track Name] by [Artist Name]
Source: [Website URL]
License: [License Type, e.g., CC BY 4.0]
```

## 🤖 Set Up Weekly Automation (Optional)

To generate videos automatically every Sunday:

### 1. Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

   | Name | Value |
   |------|-------|
   | `OPENAI_API_KEY` | Your OpenAI key |
   | `PEXELS_API_KEY` | Your Pexels key (or Pixabay) |
   | `ELEVENLABS_API_KEY` | Your ElevenLabs key (optional) |

### 2. Enable Workflow

The workflow is already configured in `.github/workflows/weekly-video.yml`

It will automatically:
- Run every Sunday at 6:00 AM UTC
- Generate a new video
- Upload it as an artifact

### 3. Download Generated Videos

1. Go to **Actions** tab in GitHub
2. Click on the latest workflow run
3. Scroll to **Artifacts** section
4. Download `devotional-video-XXX.zip`

## 🎯 What You Get

Your video includes:
- **Duration**: 30 minutes
- **Resolution**: 1920x1080 (Full HD)
- **Content**: Original devotional script about Radha Krishna
- **Visuals**: 30 spiritual images with slow zoom/pan
- **Audio**: Clear voice narration + optional background music
- **Format**: MP4 (works everywhere)

## 📝 Uploading to YouTube

When uploading your video:

### 1. Create an Eye-Catching Title
```
30-Minute Radha Krishna Morning Meditation | Divine Love & Devotion | Peaceful Background Music
```

### 2. Write a Good Description
```
🕉️ Welcome to our weekly devotional meditation series on Radha Krishna.

In this 30-minute meditation, we explore [theme of the week].
Perfect for morning meditation, spiritual reflection, or peaceful listening.

⏰ Chapters:
0:00 - Introduction
5:00 - Segment 1: [Title]
10:00 - Segment 2: [Title]
... etc.

📋 Credits:
• Script: AI-generated original content
• Voice: Text-to-speech synthesis  
• Images: Royalty-free from Pexels.com / Pixabay.com
  (Licensed under Pexels License / Pixabay License)
• Music: [Your music attribution here]

🙏 Like, subscribe, and share for more devotional content!

#RadhaKrishna #Meditation #Devotional #Spiritual #BhaktiYoga
```

### 3. Add Tags
```
radha krishna, meditation, devotional, spiritual, bhakti, hinduism,
morning meditation, krishna bhajan, devotional music, peaceful,
relaxing, spiritual awakening
```

### 4. Choose Category
- **Nonprofits & Activism** or **Education**

### 5. Important Settings
- ✅ Not made for kids (unless specifically designed for children)
- ✅ Add to playlist: "Devotional Meditations" or similar
- ✅ Set thumbnail (create a beautiful Radha Krishna image)

## ❓ Troubleshooting

### "OpenAI API key not configured"
**Solution**: 
```bash
# Check if .env file exists
cat .env

# If not, create it
cp .env.example .env
# Then add your API key
```

### "FFmpeg not found"
**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from ffmpeg.org
```

### "No images fetched"
**Solution**:
1. Check your API key is correct in `.env`
2. Verify internet connection
3. Try the alternative API (Pixabay if using Pexels, or vice versa)

### "Module not found"
**Solution**:
```bash
pip install -r requirements.txt
```

### Video generation is slow
**This is normal!** Generating a 30-minute video takes 10-15 minutes:
- Script generation: 2-3 minutes
- Voice synthesis: 1-2 minutes
- Image downloading: 2-3 minutes
- Video rendering: 3-5 minutes

## 🎉 You Did It!

Congratulations! You've successfully:
- ✅ Set up the devotional video pipeline
- ✅ Generated your first 30-minute video
- ✅ Learned about copyright-safe content
- ✅ Optionally set up weekly automation

## 📚 What's Next?

1. **Generate More Videos**: Run `python devotional_pipeline.py` weekly
2. **Customize Themes**: Edit themes in `devotional_pipeline.py`
3. **Improve Voice**: Add ElevenLabs API key for better voice quality
4. **Add Music**: Download and add devotional background music
5. **Share**: Upload to YouTube and share with your community

## 🆘 Need Help?

- 📖 **Full Documentation**: `DEVOTIONAL_PIPELINE_README.md`
- 🚀 **Quick Reference**: `QUICKSTART.md`
- 📊 **Technical Details**: `IMPLEMENTATION_SUMMARY.md`
- 🐛 **Issues**: Open a GitHub issue

---

**May your devotional videos bring peace and spiritual wisdom to many! 🙏**

*Om Namo Bhagavate Vasudevaya* 🕉️
