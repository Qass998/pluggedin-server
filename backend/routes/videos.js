const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = process.env.OUTPUT_VIDEO_DIR || '/tmp/pluggedin-videos';

/**
 * GET /api/videos/:videoId — serve HTML video
 */
router.get('/:videoId', (req, res) => {
  const filePath = path.join(OUTPUT_DIR, `${req.params.videoId}.html`);

  if (!fs.existsSync(filePath)) {
    return res.status(404).send('<h1>Video not found</h1>');
  }

  res.setHeader('Content-Type', 'text/html');
  res.sendFile(path.resolve(filePath));
});

/**
 * GET /api/videos — list all generated videos
 */
router.get('/', (req, res) => {
  if (!fs.existsSync(OUTPUT_DIR)) {
    return res.json({ total: 0, videos: [] });
  }

  const videos = fs.readdirSync(OUTPUT_DIR)
    .filter(f => f.endsWith('.html'))
    .map(f => {
      const stat = fs.statSync(path.join(OUTPUT_DIR, f));
      return {
        videoId: f.replace('.html', ''),
        url: `/api/videos/${f.replace('.html', '')}`,
        createdAt: stat.mtime.toISOString(),
        fileSizeKB: Math.round(stat.size / 1024),
      };
    })
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  res.json({ total: videos.length, videos });
});

module.exports = router;
