# Hyperframes Video Generation Setup

## Why Hyperframes?

**Remotion** = React-based, more heavyweight, requires Node.js runtime
**Hyperframes** = HTML/CSS-based, deterministic, built for agents, lighter rendering

For generating 100+ personalized videos daily with signal-based targeting, **Hyperframes is optimal**.

---

## Installation

### 1. Install Hyperframes CLI

```bash
npm install -g hyperframes
```

Or locally in the project:

```bash
npm install hyperframes
```

Then reference in code:
```js
const hyperframesPath = './node_modules/.bin/hyperframes';
```

### 2. Verify Installation

```bash
hyperframes --version
hyperframes --help
```

Should output version info and CLI options.

### 3. Verify FFmpeg (for audio merge)

```bash
ffmpeg -version
ffprobe -version
```

If missing:
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows (via Scoop)
scoop install ffmpeg
```

---

## How It Works

### **Pipeline: HTML → MP4 → Audio merge → Final video**

```
1. Prospect data (name, signals, analysis)
           ↓
2. Handlebars template injection
           ↓
3. HTML file with dynamic data
           ↓
4. Hyperframes render (HTML → MP4)
           ↓
5. 60-second silent video
           ↓
6. 11Labs voiceover generation
           ↓
7. FFmpeg merge (video + audio)
           ↓
8. Final personalized MP4 video
```

---

## Configuration

### VideoGenerator Options

```js
const VideoGenerator = require('./services/video-generator');

const gen = new VideoGenerator({
  outputDir: '/tmp/pluggedin-videos',           // Where videos are saved
  templatePath: './video-templates/prospect-signal-video.html', // HTML template
  hyperframesPath: 'hyperframes',               // CLI command
  ffmpegPath: 'ffmpeg',                         // FFmpeg command
});
```

### Environment Variables

```env
# Required
OUTPUT_VIDEO_DIR=/tmp/pluggedin-videos
ELEVENLABS_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Optional (defaults to system PATH)
HYPERFRAMES_PATH=hyperframes
FFMPEG_PATH=ffmpeg
```

---

## Usage Examples

### Single Video Generation

```js
const VideoGenerator = require('./services/video-generator');
const ScriptGenerator = require('./services/script-generator');

const gen = new VideoGenerator();
const scriptGen = new ScriptGenerator();

// Step 1: Prospect data
const prospect = {
  name: 'Sarah Chen',
  title: 'CMO',
  company: 'TechStartup Inc',
  location: 'San Francisco',
};

// Step 2: Signal analysis
const analysis = {
  interests: ['AI marketing', 'scaling', 'efficiency'],
  pain_points: ['manual processes', 'ops bottleneck'],
  engagement_angle: 'AI automation for marketing',
  competitor_opportunities: ['Competitor1'],
  value_promise: '3x faster campaigns with AI',
  confidence_score: 8,
};

// Step 3: Generate script + voiceover
const { script } = await scriptGen.generateLinkedInScript(prospect, analysis);
const { audio } = await scriptGen.generateVoiceover(script);

// Step 4: Generate video
const result = await gen.generateProspectVideo(prospect, analysis, audio);

console.log(`✓ Video ready: ${result.videoPath}`);
```

### Batch Generation (100 videos)

```js
const results = await gen.generateBatch(
  prospects,    // Array of 100 prospect objects
  analyses,     // Array of 100 analysis objects
  voiceovers    // Array of 100 voiceover audio buffers
);

console.log(`✓ Generated ${results.summary.successful} videos`);
console.log(`✗ Failed: ${results.summary.failed}`);
```

---

## HTML Template

The template at `video-templates/prospect-signal-video.html` uses Handlebars syntax:

```html
<!-- Dynamic data injection -->
<h1>Hi {{prospect.name}}</h1>
<p>{{prospect.title}} at {{prospect.company}}</p>

<!-- Looping through arrays -->
{{#each analysis.interests}}
  <div>{{this}}</div>
{{/each}}

<!-- CSS animations -->
<style>
  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
  }
  h1 { animation: slideDown 1s ease-out; }
</style>
```

Hyperframes supports:
- **GSAP animations** — JavaScript-driven motion
- **CSS animations** — Keyframes, transitions
- **Lottie files** — Lightweight JSON animations
- **Three.js** — 3D visualizations
- **Anime.js** — Advanced animations

---

## Scene Timing

Each scene has a `data-scene-duration` attribute (in milliseconds):

```html
<!-- [0-5s] Opening -->
<div class="scene" data-scene-duration="5000">
  <h1>Hi {{prospect.name}}</h1>
</div>

<!-- [5-15s] Interests -->
<div class="scene" data-scene-duration="10000">
  <h2>Your interests:</h2>
  {{#each analysis.interests}}...{{/each}}
</div>

<!-- [15-25s] Pain points -->
<div class="scene" data-scene-duration="10000">
  <h2>What you're solving for:</h2>
  {{#each analysis.pain_points}}...{{/each}}
</div>
```

Total = 5 + 10 + 10 + 20 + 10 + 5 = **60 seconds**

---

## Hyperframes CLI Reference

```bash
# Render HTML to MP4
hyperframes render input.html --output output.mp4 --fps 30 --duration 60

# Options
--fps 30              # Frames per second (default 30)
--duration 60         # Video duration in seconds
--width 1280          # Output width (default 1280)
--height 720          # Output height (default 720)
--quality high        # Render quality: low|medium|high
--headless            # Run headless (default true)
--parallel 4          # Parallel rendering instances
--output output.mp4   # Output file path
```

---

## Performance Tips

### For Batch Processing (100+ videos daily)

1. **Parallel rendering:** Render multiple videos in parallel
   ```js
   // Use Promise.all() to batch render
   const videos = await Promise.all(
     prospects.map(p => gen.generateProspectVideo(p, ...))
   );
   ```

2. **Template caching:** Compile Handlebars template once
   ```js
   const template = Handlebars.compile(fs.readFileSync(templatePath));
   // Reuse `template` for all prospects
   ```

3. **Voiceover pre-generation:** Generate all voiceovers before video rendering
   ```js
   const voiceovers = await Promise.all(
     scripts.map(s => scriptGen.generateVoiceover(s))
   );
   // Then render videos with voiceovers
   ```

4. **Cleanup regularly:** Don't let temp files accumulate
   ```js
   gen.cleanup(completedVideoIds);
   ```

---

## Troubleshooting

### "Command not found: hyperframes"

**Solution:** Install globally or use full path
```bash
npm install -g hyperframes
# OR use local path
node_modules/.bin/hyperframes render ...
```

### "FFmpeg not found"

**Solution:** Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg  # or scoop install ffmpeg
```

### Video renders but no audio

**Solution:** Check 11Labs API key and voiceover generation
```js
try {
  const voiceover = await scriptGen.generateVoiceover(script);
  console.log(`Voiceover size: ${voiceover.audio.length} bytes`);
} catch (error) {
  console.error('Voiceover failed:', error);
}
```

### Hyperframes render hangs

**Solution:** Add timeout and check HTML validity
```bash
# Test HTML locally
hyperframes render test.html --output test.mp4 --duration 60 --quality low

# Add debugging
hyperframes render test.html --output test.mp4 --verbose
```

---

## Cost Comparison

| Tool | Model | Per-video cost | Speed (60s video) | Best for |
|------|-------|---|---|---|
| **Hyperframes** | HTML-based | ~$0.01 | 5-15s | Batch (100+/day) |
| **Remotion** | React-based | ~$0.02 | 10-20s | High-quality single videos |
| **HeyGen** | Avatar video | $0.50-2.00 | 30-60s | Talking-head videos |

For 100 videos/day: **Hyperframes = $1/day, Remotion = $2/day, HeyGen = $50-200/day**

---

## Next Steps

1. ✓ Install Hyperframes: `npm install -g hyperframes`
2. ✓ Verify HTML template renders: `hyperframes render prospect-signal-video.html --output test.mp4`
3. ✓ Test full pipeline with 5 prospects
4. ✓ Measure video generation speed and file sizes
5. ✓ Deploy batch processing for 100+ daily videos

---

## API Endpoint

See `/backend/routes/content.js` for the full pipeline:

```bash
POST /api/content/create-signal-based-outreach
```

Request:
```json
{
  "jobTitles": ["CMO", "VP Marketing"],
  "industries": ["SaaS"],
  "companySizes": [100, 5000],
  "locations": ["UK"],
  "limit": 50
}
```

Response:
```json
{
  "success": true,
  "summary": {
    "total_processed": 48,
    "total_errors": 2
  },
  "results": [
    {
      "prospect": { "name": "Sarah Chen", "title": "CMO", "company": "TechStartup" },
      "signals": { "companiesFollowed": [...], "interests": [...] },
      "analysis": { "engagement_angle": "AI marketing", "confidence_score": 8 },
      "video": { "url": "https://videos.pluggedin.io/sarah-chen.mp4", "duration": 60 },
      "outreach": { "linkedin": {...}, "email": {...}, "instagram": {...} }
    }
  ]
}
```

---

## Resources

- **Hyperframes Docs:** https://github.com/heygen-com/hyperframes
- **Handlebars Guide:** https://handlebarsjs.com/
- **FFmpeg Guide:** https://ffmpeg.org/documentation.html
- **11Labs API:** https://elevenlabs.io/docs
