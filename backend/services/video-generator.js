/**
 * Video Generator — Creates prospect signal videos using HTML + embedded audio
 * HTML template + Handlebars data injection + ElevenLabs audio as base64 data URI
 * No external tools (Hyperframes, FFmpeg). Pure browser-playable HTML.
 */

const fs = require('fs');
const path = require('path');
const Handlebars = require('handlebars');

class VideoGenerator {
  constructor(options = {}) {
    this.outputDir = options.outputDir || process.env.OUTPUT_VIDEO_DIR || '/tmp/pluggedin-videos';
    this.templatePath = options.templatePath || path.join(
      __dirname,
      '../video-templates/prospect-signal-video.html'
    );

    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  /**
   * Generate personalized video for a prospect
   * Input: prospect + analysis + voiceover audio buffer
   * Output: HTML file with embedded audio (data URI) + shareable URL
   */
  async generateProspectVideo(prospect, analysis, voiceoverBuffer) {
    const videoId = `v_${Date.now()}_${(prospect.name || 'prospect')
      .replace(/\s+/g, '-')
      .toLowerCase()
      .slice(0, 20)}`;

    try {
      console.log(`[VideoGenerator] Starting: ${prospect.name}`);

      // Compile template + inject data
      const html = this._injectTemplateData(prospect, analysis);
      let outputHtml = html;

      // Embed ElevenLabs audio as base64 data URI
      if (voiceoverBuffer) {
        const b64 = Buffer.isBuffer(voiceoverBuffer)
          ? voiceoverBuffer.toString('base64')
          : voiceoverBuffer;

        outputHtml = outputHtml.replace(
          '</body>',
          `<audio id="pluggedin-vo" autoplay style="display:none;">
             <source src="data:audio/mpeg;base64,${b64}" type="audio/mpeg">
           </audio>
           <script>
             document.addEventListener('DOMContentLoaded', () => {
               const audio = document.getElementById('pluggedin-vo');
               if (audio) {
                 audio.play().catch(err => {
                   console.log('[Audio] Autoplay blocked or failed:', err.message);
                 });
               }
             });
           </script>
          </body>`
        );
      }

      // Write HTML file
      const outputPath = path.join(this.outputDir, `${videoId}.html`);
      fs.writeFileSync(outputPath, outputHtml, 'utf8');
      console.log(`  ✓ Video rendered: ${outputPath}`);

      const stats = fs.statSync(outputPath);
      return {
        success: true,
        videoId,
        htmlPath: outputPath,
        videoUrl: `/api/videos/${videoId}`,
        fileSizeKB: Math.round(stats.size / 1024),
        fileSizeBytes: stats.size,
        durationSeconds: 60,
      };
    } catch (error) {
      console.error(`[VideoGenerator] Error for ${prospect.name}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Inject prospect data into HTML template using Handlebars
   */
  _injectTemplateData(prospect, analysis) {
    const templateContent = fs.readFileSync(this.templatePath, 'utf8');
    const compiled = Handlebars.compile(templateContent);

    const data = {
      prospect: {
        name: prospect.name || 'Prospect',
        title: prospect.title || '',
        company: prospect.company || '',
        location: prospect.location || '',
      },
      analysis: {
        interests: analysis.interests || [],
        pain_points: analysis.pain_points || [],
        engagement_angle: analysis.engagement_angle || 'Strategic Partnership',
        competitor_opportunities: analysis.competitor_opportunities || [],
        value_promise: analysis.value_promise || 'Measurable business impact',
        personalization_tactics: analysis.personalization_tactics || [],
        confidence_score: analysis.confidence_score || 7,
      },
    };

    return compiled(data);
  }


  /**
   * Batch generate videos for multiple prospects
   */
  async generateBatch(prospects, analyses, voiceovers) {
    console.log(`[VideoGenerator] Batch processing ${prospects.length} videos...`);

    const results = [];
    const errors = [];

    for (let i = 0; i < prospects.length; i++) {
      try {
        const video = await this.generateProspectVideo(
          prospects[i],
          analyses[i],
          voiceovers[i]
        );
        results.push({
          prospect: prospects[i].name,
          video,
        });
      } catch (error) {
        errors.push({
          prospect: prospects[i].name,
          error: error.message,
        });
      }
    }

    console.log(`[VideoGenerator] Batch complete: ${results.length} success, ${errors.length} errors`);

    return {
      success: errors.length === 0,
      results,
      errors,
      summary: {
        total: prospects.length,
        successful: results.length,
        failed: errors.length,
        outputDir: this.outputDir,
      },
    };
  }

  /**
   * Upload video to cloud storage (placeholder)
   */
  async uploadToCloud(videoPath) {
    console.log(`[Cloud] Would upload: ${videoPath}`);
    return {
      url: `https://videos.pluggedin.io/${path.basename(videoPath)}`,
      uploaded: false,
    };
  }

  /**
   * Cleanup generated files
   */
  cleanup(videoIds = []) {
    console.log(`[VideoGenerator] Cleanup: removing ${videoIds.length} files...`);
    videoIds.forEach(id => {
      const patterns = [
        path.join(this.outputDir, `${id}.html`),
      ];
      patterns.forEach(f => {
        if (fs.existsSync(f)) fs.unlinkSync(f);
      });
    });
  }
}

module.exports = VideoGenerator;
