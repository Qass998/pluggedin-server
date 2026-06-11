# LinkedIn Presence Skill
# Content posting, profile optimization, engagement
# Replaces: linkedin-automation (June 2026)

## When to use this skill

**Triggers:**
- "Post on LinkedIn"
- "Build LinkedIn presence"
- "Create LinkedIn content"
- "Optimize LinkedIn profile"
- "Automate LinkedIn posting"

**Input:** Topic, content calendar, posting strategy
**Output:** LinkedIn posts scheduled + profile optimized

---

## LINKEDIN PROFILE OPTIMIZATION

**Headline (120 characters):**
```
❌ Bad:    "VP Sales at Acme Corp"
✓ Good:   "VP Sales @ Acme | Revenue Growth | SaaS Sales → $50M ARR"
✓ Better: "VP Sales @ Acme | Built 3x Pipeline | Expert in SaaS/Enterprise Sales"
```

Your headline should tell the story:
1. Your title + company
2. Your result or claim to fame
3. Your buyer's pain point you solve

**Profile Picture:**
- Professional headshot (smiling, clear face)
- Good lighting, neutral background
- Business casual or formal
- No filters or overshadow

**About Section (2,000 characters):**
```
Use this to:
- Tell your story (your background, why you do this)
- Share your expertise (what you're known for)
- Mention recent wins (built sales team from 0 to 50 people, etc)
- Link to company (credibility)
- Add call-to-action ("Open to advisory roles" or "Let's connect")

Example:
"VP Sales at Acme — I build high-performing sales teams for SaaS companies.

Over the past 10 years, I've:
- Grown sales teams from 0 → 50 people
- Scaled revenue from $2M → $50M ARR
- Led through Series A, B, C fundraising

Currently focused on:
- Enterprise sales strategy
- Hiring + training exceptional sales people
- Revenue predictability at scale

Love talking about: sales culture, hiring, revenue models, SaaS.

Open to advisory + board conversations."
```

**Experience Section:**
- Add timeline for each role
- Add metrics to each role ("Grew team from 5 → 25, +200% revenue")
- Add description of key wins

**Skills Section:**
- Add 20-30 skills (search volume = LinkedIn ranking)
- Endorsed skills appear to buyers

---

## POSTING STRATEGY

### Post Types (and response rates)

```
TYPE 1: Opinion/Hot Take
  "Here's what everyone gets wrong about sales hiring..."
  Engagement: 8-15% (people love to disagree)
  
TYPE 2: Story/Win
  "3 years ago we had $0 in pipeline. Here's what changed..."
  Engagement: 10-20% (emotion + relatability)
  
TYPE 3: Lesson Learned
  "I fired my top salesperson yesterday. Here's why..."
  Engagement: 12-25% (controversy + honesty)
  
TYPE 4: Industry Data
  "SaaS sales cycles are 40% longer than they were 2 years ago..."
  Engagement: 5-10% (educational but less personal)
  
TYPE 5: Question
  "What's the biggest mistake you see in SaaS hiring?"
  Engagement: 8-12% (people answer questions)
  
TYPE 6: Humble Brag
  "Grateful to hit $50M ARR — never thought we'd get here..."
  Engagement: 5-8% (but builds credibility)
```

**Best performing:** Story/Win + Lesson Learned (combine them)

### Posting Frequency

- **If building personal brand:** 3-5 posts per week
- **If supporting team:** 2-3 posts per week
- **If minimal time:** 1 post per week

**Consistency matters more than frequency.**

---

## POST TEMPLATE

```
[HOOK — 1 line, make them stop scrolling]

[STORY — 3-5 lines, what happened?]
  
[INSIGHT — what did you learn?]

[CTA — what should they do? or question?]

[HASHTAGS — 5-10 relevant]
```

**Example:**

```
"I fired my top salesperson yesterday.

Here's why: He was hitting quota, closing big deals. But he was 
teaching the team that closing > relationships. 3 months later, 
half the team wanted to quit. The cost of his individual wins was 
the team's culture.

Learned: You can't scale if your top performer is setting the wrong tone.

The best sales leaders have learned this: Your culture scales or dies by your example.

Who's had to make a similar hard call?

#SalesLeadership #TeamCulture #SalesHiring #Startup"
```

---

## CONTENT CALENDAR

**30-day example:**

```
Week 1:
  Mon: Opinion/take (controversial)
  Wed: Question (engagement)
  Fri: Story (personal win)

Week 2:
  Mon: Lesson learned (from failure)
  Wed: Data/insight (education)
  Fri: Humble brag (team win)

Week 3:
  Mon: Opinion/take (timely)
  Wed: Story (customer success)
  Fri: Question (poll followers)

Week 4:
  Mon: Lesson learned (new learning)
  Wed: Opinion (bold stance)
  Fri: Story (long-form narrative)
```

---

## HASHTAG STRATEGY

**Use 5-10 hashtags, mix of:**
- Broad (1M+ posts): #SalesLeadership
- Medium (100k-1M): #SaaSSales
- Niche (10k-100k): #SalesHiring
- Hyper-local: #[YourCity]Tech

**Example hashtag mix:**
```
#SalesLeadership (broad, reach)
#SaaSSales (medium, relevant)
#SalesHiring (niche, specific)
#RevenueGrowth (medium, relevant)
#StartupLife (broad, reach)
#SFBay (hyper-local)
```

---

## ENGAGEMENT RULES

**After posting, engage (15-30 min):**
1. Like first 20 comments
2. Reply to first 3 comments with genuine value
3. Don't be salesy ("DM me" is bad)
4. Ask follow-up questions to responders

**Why:** LinkedIn algorithm rewards engagement. If your post gets comments quickly, it shows in more feeds.

---

## AUTOMATION VIA RUBE MCP

**Scheduled posting (set it and forget it):**

```
Post {
  title: "Your post title"
  content: "Your content text"
  scheduled_time: "2026-06-14T09:00:00Z"
  media: ["image.jpg"] (optional)
}
```

Rube MCP handles:
- Scheduling to exact time
- Publishing on LinkedIn
- Tracking engagement (likes, comments, impressions)

**Note:** LinkedIn blocks third-party posting APIs, so Rube uses browser automation. Works reliably, takes ~2-5 seconds per post.

---

## PROFILE URL OPTIMIZATION

Your LinkedIn URL should be:
```
linkedin.com/in/yourname

NOT: linkedin.com/in/john-doe-12345a67890
```

Go to Settings → Public Profile & URL → Edit your URL

---

## ANALYTICS (What to track)

**After 10-15 posts, analyze:**

| Metric | Target | What it means |
|--------|--------|---------------|
| Impressions | 500-2000 | How many people saw it |
| Engagement rate | 5-10% | Percentage who liked/commented/shared |
| Comments | 10-30 | Discussion quality (better than likes) |
| Shares | 2-5 | How many forwarded to their network |
| Click-through | 1-3% | If you linked to something |

**Analysis:**
- Posts with 15+ comments = repost that topic (people care)
- Posts with 3-5 shares = extremely valuable (reshare)
- Posts with <3% engagement = wrong audience or bad hook

---

## PERSONAL BRAND BUILD (6-month plan)

**Month 1-2:**
- Optimize profile (headline, about, photo)
- Post 2x per week
- Engage with 5-10 posts daily
- Goal: Establish baseline (200-500 impressions/post)

**Month 3-4:**
- Post 3x per week
- Mix: story + opinion + question
- Engage deeply (meaningful comments)
- Goal: 1000+ impressions, 5%+ engagement

**Month 5-6:**
- Post 4x per week
- Build on winning topics
- Start commenting on industry leaders' posts (get visibility)
- Goal: 2000+ impressions, 8%+ engagement

**Result after 6 months:**
- 5-10k followers
- Known in your niche
- Inbound DMs from prospects
- Speaking invites, partnerships

---

## ANTI-PATTERNS

❌ **Don't use LinkedIn as a sales channel.**
"DM me" on every post = people unfollow.

❌ **Don't go silent for 3 months then post daily.**
Consistency. Post regularly or don't bother.

❌ **Don't copy other people's posts.**
Create original takes. Your perspective = your value.

❌ **Don't ignore comments.**
If someone takes time to comment, reply within 24 hours.

❌ **Don't post spam or engagement-bait.**
"Like if you agree!" gets you shadow-banned.

---

## TOOLS REQUIRED

- ✅ **LinkedIn account** (free)
- ✅ **Rube MCP** (for scheduling)
- ✅ **Canva** (free, design post images)
- ✅ **Buffer or Later** (free tier, cross-platform scheduling)

---

## VARIABLES

```
POSTING_FREQUENCY = "3-5 times per week"
ENGAGEMENT_TARGET = "5-10%"
RESPONSE_TIME = "within 24 hours"
HASHTAG_COUNT = "5-10 per post"
MONTHLY_GOAL = "12-20 posts"
```

---

Last updated: June 7, 2026
