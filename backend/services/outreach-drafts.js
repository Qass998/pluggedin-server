/**
 * Outreach Drafts - Generate multi-channel copy (LinkedIn, Email, Instagram)
 */

const Anthropic = require('@anthropic-ai/sdk');

class OutreachDrafts {
  constructor(options = {}) {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.model = options.model || 'claude-opus-4-8';
  }

  /**
   * Generate all three channel drafts
   */
  async generateAllDrafts(prospect, analysis, videoUrl, type = 'linkedin') {
    console.log(`[OutreachDrafts] Generating ${type} outreach for ${prospect.author}...`);

    const [linkedinDraft, emailDraft, instagramDraft] = await Promise.all([
      this.generateLinkedInDraft(prospect, analysis, videoUrl, type),
      this.generateEmailDraft(prospect, analysis, videoUrl, type),
      this.generateInstagramDraft(prospect, analysis, videoUrl, type),
    ]);

    return {
      linkedin: linkedinDraft,
      email: emailDraft,
      instagram: instagramDraft,
      ready: true,
    };
  }

  /**
   * LinkedIn DM draft
   */
  async generateLinkedInDraft(prospect, analysis, videoUrl, type) {
    const prompt = `
Generate a LinkedIn direct message to ${prospect.author} at ${prospect.company}.

Context:
- You analyzed their post/content
- You created a video showing improvements
- Goal: Get them to watch the video + book a call

Requirements:
- Under 150 words
- Professional but warm tone
- Reference their specific post (1 detail)
- Strong hook that makes them want to click the video
- Include: [Watch video](${videoUrl})
- Soft CTA: "Worth 15 minutes to see this?"
- No sales pitch, just value

${type === 'linkedin' ? `- Their post: "${prospect.content}"` : ''}
${type === 'instagram' ? `- Their caption: "${prospect.caption}"` : ''}

Return the complete DM message. Start directly with the greeting, no labels.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 200,
        messages: [{ role: 'user', content: prompt }],
      });

      const draft = response.content[0].text.trim();

      return {
        channel: 'LinkedIn',
        draft,
        wordCount: draft.split(/\s+/).length,
        ready: true,
      };
    } catch (error) {
      console.error('[OutreachDrafts] LinkedIn draft error:', error.message);
      return this._defaultLinkedInDraft(prospect, videoUrl);
    }
  }

  /**
   * Email draft
   */
  async generateEmailDraft(prospect, analysis, videoUrl, type) {
    const prompt = `
Generate a professional email to ${prospect.author} at ${prospect.company}.

Goal: Get them to watch the video + book a call
Structure:
1. Subject line (compelling, not clickbait)
2. Brief greeting
3. What you found (2 strengths, 1 gap)
4. The improvement (show how you'd fix it)
5. Video link with CTA
6. Calendar link
7. Professional sign-off

Requirements:
- Email body under 250 words
- Data-driven, not emotional
- Specific to their content
- Include: [Watch this 60-second video](${videoUrl})
- Include: [Book a 15-min call](https://calendly.com/pluggedin)
- Sign as "PluggedIN Content Strategy Team"

${type === 'linkedin' ? `- Post: "${prospect.content}"` : ''}
- Company: ${prospect.company}
- Strengths: ${analysis.strengths?.join(', ')}
- Gaps: ${analysis.gaps?.join(', ')}

Return ONLY the email (subject + body). Format clearly.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 400,
        messages: [{ role: 'user', content: prompt }],
      });

      const draft = response.content[0].text.trim();
      const [subject, ...bodyParts] = draft.split('\n\n');

      return {
        channel: 'Email',
        subject: subject.replace('Subject: ', '').trim(),
        body: bodyParts.join('\n\n'),
        full: draft,
        wordCount: draft.split(/\s+/).length,
        ready: true,
      };
    } catch (error) {
      console.error('[OutreachDrafts] Email draft error:', error.message);
      return this._defaultEmailDraft(prospect, videoUrl);
    }
  }

  /**
   * Instagram DM draft
   */
  async generateInstagramDraft(prospect, analysis, videoUrl, type) {
    const prompt = `
Generate a casual Instagram direct message to @${prospect.authorUsername || 'creator'}.

Goal: Show you analyzed their content + offer improvement video
Tone: Creator-to-creator, enthusiastic, casual
Requirements:
- Under 100 words
- Compliment their specific content (reference 1 detail)
- Mention the improvement idea (1 gap)
- Video link: [Watch this](${videoUrl})
- Soft CTA: Book a call? Just casual interest
- Use relevant emojis (not excessive)
- Conversational, like friend recommending something

${type === 'instagram' ? `- Their caption: "${prospect.caption}"` : ''}

Return ONLY the DM message. No labels, just the text.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 150,
        messages: [{ role: 'user', content: prompt }],
      });

      const draft = response.content[0].text.trim();

      return {
        channel: 'Instagram',
        draft,
        wordCount: draft.split(/\s+/).length,
        ready: true,
      };
    } catch (error) {
      console.error('[OutreachDrafts] Instagram draft error:', error.message);
      return this._defaultInstagramDraft(prospect, videoUrl);
    }
  }

  // Fallback drafts

  _defaultLinkedInDraft(prospect, videoUrl) {
    return {
      channel: 'LinkedIn',
      draft: `Hi ${prospect.author},\n\nI analyzed your recent post and found something interesting. I created a quick video showing what's working and where we could improve it.\n\n[Watch the video](${videoUrl})\n\nWorth 15 minutes to see this?\n\nCheers`,
      ready: true,
    };
  }

  _defaultEmailDraft(prospect, videoUrl) {
    return {
      channel: 'Email',
      subject: `Quick analysis of your ${prospect.company} content`,
      body: `Hi ${prospect.author},\n\nI spent 15 minutes analyzing your recent content and found some actionable improvements.\n\n[Watch the video](${videoUrl})\n\nIf you're open to it, I'd love to show you exactly how we'd help ${prospect.company} get 3x more engagement.\n\n[Book a 15-min call](https://calendly.com/pluggedin)\n\nBest,\nPluggedIN`,
      ready: true,
    };
  }

  _defaultInstagramDraft(prospect, videoUrl) {
    return {
      channel: 'Instagram',
      draft: `Hey! 👋 I noticed your recent post and had some ideas on how to get even more engagement. Made you a quick video 👇\n\n[Watch](${videoUrl})\n\nLet me know what you think!`,
      ready: true,
    };
  }
}

module.exports = OutreachDrafts;
