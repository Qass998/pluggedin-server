---
name: skill-scraper
description: Find, validate and safely install relevant skills from GitHub. Use when a task requires a capability not currently installed. Always validates before installing. Never installs unsafe or low quality skills.
---

# Skill Scraper

## Purpose
Find the best available skill for any task.
Validate it is safe and high quality.
Install it automatically to ~/.claude/skills/
Log what was installed and why.

## When To Use This Skill
- Task requires capability not in installed skills
- Need a specialist skill for a new client vertical
- Research task needs a specific scraping skill
- Marketing task needs a specific creative skill
- Any task where you think "there might be a skill for this"

## Search Order

Always search these sources in this order:

1. github.com/VoltAgent/awesome-agent-skills
   Best curated general skills library
   1000+ skills, well maintained

2. github.com/gooseworks-ai/goose-skills
   Best GTM and sales skills
   Already partially installed

3. github.com/gtmagents/gtm-agents
   Full GTM pipeline skills
   Already partially installed

4. github.com/VoltAgent/awesome-openclaw-skills
   5400+ community skills
   Wide coverage of edge cases

5. github.com/tinyfish-io/skills
   Web browsing and scraping skills
   Best for internet research tasks

6. github.com/coreyhaines31/marketingskills
   Best marketing and copy skills
   Already partially installed

## Validation Checklist

Before installing ANY skill check ALL of these:

QUALITY CHECKS:
→ Stars: minimum 50 GitHub stars
→ Last commit: within last 6 months
→ README: clear description of what it does
→ SKILL.md: properly formatted, clear instructions
→ Maintainer: has other repos or contributions

SAFETY CHECKS:
→ No requests for API keys not in our .env
→ No curl commands to unknown endpoints
→ No requests to install additional packages
→ No file system operations outside workspace
→ No requests for credentials or passwords
→ No obfuscated code or encoded strings

RELEVANCE CHECKS:
→ Does it solve the exact task needed?
→ Is it specific enough to be useful?
→ Does it overlap with already installed skills?
→ Would using it save significant tokens/time?

REJECT if any check fails.
PROCEED only if all checks pass.

## Installation Process

STEP 1: Clone to temp folder
git clone [repo-url] /tmp/skill-check-[name]

STEP 2: Read the SKILL.md fully
cat /tmp/skill-check-[name]/[path]/SKILL.md

STEP 3: Run validation checklist
Check every item above manually.
If anything fails: delete temp folder and stop.

STEP 4: Install if validated
cp /tmp/skill-check-[name]/[path]/SKILL.md
   ~/.claude/skills/[skill-name]/SKILL.md

STEP 5: Clean up temp folder
rm -rf /tmp/skill-check-[name]

STEP 6: Log the installation
Add to ~/.claude/memory/today.md:
"Installed skill: [name] from [repo]
 Reason: [what task it solves]
 Validated: stars=[X], updated=[date]"

## Skill Naming Convention

Save skills with descriptive names:
~/.claude/skills/
├── goose-gtm/           ← Goose GTM library
├── corey-haines/        ← Marketing skills
├── higgsfield/          ← Video and image skills
├── tinyfish/            ← Web browsing skill
└── custom/              ← Skills you write yourself

## Output Format

After finding and validating a skill report:

SKILL FOUND: [name]
SOURCE: [GitHub URL]
STARS: [count]
LAST UPDATED: [date]
PURPOSE: [what it does]
VALIDATION: PASSED / FAILED
REASON TO INSTALL: [specific task it solves]

Install? [yes/no]

Wait for approval before installing.
