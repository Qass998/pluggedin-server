/**
 * Signal Analyzer - Analyzes prospect signals to determine best engagement angle
 * Replaces post analysis with deeper signal analysis
 */

const Anthropic = require('@anthropic-ai/sdk');

class SignalAnalyzer {
  constructor(options = {}) {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.model = options.model || 'claude-opus-4-8';
  }

  /**
   * Analyze LinkedIn prospect signals to determine interests, pain points, and best angle
   */
  async analyzeProspectSignals(prospect) {
    const {
      name,
      title,
      company,
      location,
      signals = {},
    } = prospect;

    const prompt = `
You are analyzing a LinkedIn prospect's engagement signals to determine:
1. What they CARE ABOUT (based on companies they follow, content they engage with, articles they share)
2. What PAIN POINTS they likely have (based on topics they engage with)
3. What SOLUTION ANGLE would resonate best

PROSPECT:
Name: ${name}
Title: ${title}
Company: ${company}
Location: ${location}

SIGNALS (What they do on LinkedIn):
Companies they follow: ${(signals.companiesFollowed || []).slice(0, 5).join(', ') || 'Unknown'}
Recent engagement topics: ${(signals.messageTopics || []).slice(0, 3).join(', ') || 'Unknown'}
Articles/posts they shared: ${(signals.articlesShared || []).map(a => a.title).slice(0, 3).join(', ') || 'Unknown'}
Skills: ${(signals.skills || []).slice(0, 5).join(', ') || 'Unknown'}
Groups: ${(signals.groups || []).slice(0, 3).join(', ') || 'Unknown'}

Based on these signals, provide analysis in JSON format:

{
  "interests": ["list top 3 interests based on signals"],
  "pain_points": ["list 2-3 likely pain points they're trying to solve"],
  "engagement_angle": "The BEST angle to reach this person - e.g., 'competitor analysis', 'AI efficiency', 'scale challenges'",
  "why_this_angle": "brief explanation of why this angle works for them",
  "competitor_opportunities": ["if they follow competitors, list 2-3 areas where they're vulnerable"],
  "value_promise": "specific 1-liner about what you offer that solves their pain",
  "examples_to_reference": ["companies or trends they follow that validate your solution"],
  "personalization_tactics": {
    "reference_competitor": "name of competitor to reference if applicable",
    "reference_topic": "topic they care about to reference",
    "reference_skill": "skill/expertise they have that validates solution fit"
  },
  "confidence_score": "1-10: how confident you are in this angle based on signals (8-10 = very strong signals, 5-7 = moderate, below 5 = weak signals)"
}

Be specific and reference their actual signals. This analysis will be used to create a highly personalized video targeting this prospect.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      });

      const content = response.content[0].text;
      const analysis = JSON.parse(content);

      return {
        success: true,
        prospect: { name, title, company },
        analysis,
      };
    } catch (error) {
      console.error('[SignalAnalyzer] Error analyzing signals:', error.message);
      return this._defaultAnalysis(prospect);
    }
  }

  /**
   * Default analysis fallback
   */
  _defaultAnalysis(prospect) {
    return {
      success: false,
      prospect: { name: prospect.name, title: prospect.title, company: prospect.company },
      analysis: {
        interests: ['business efficiency', 'growth', 'technology'],
        pain_points: ['scaling challenges', 'operational efficiency', 'team productivity'],
        engagement_angle: 'operational efficiency and growth',
        why_this_angle: 'Most prospects in this role care about scaling effectively',
        confidence_score: 3,
      },
    };
  }
}

module.exports = SignalAnalyzer;
