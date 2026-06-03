# Plan Mode

Enter plan mode for the current task.

**Step 0 — Skill Discovery:**
Read `skills/registry.md` → match task to skill chain → list skills to load.

**Step 0.5 — Chain-of-Thought (silent):**
Think through: actual goal, simplest approach, 3+ risks, dependencies, can it be done in half the steps, what does "done" look like.

**Format:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗂 PLAN: [Task Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OBJECTIVE: [what and why]
SKILLS DISCOVERED: [from registry scan]
STEPS: [numbered, with files/APIs per step]
FILES AFFECTED: CREATE / MODIFY / DELETE
RISKS: [irreversible actions, costs, blockers]
TIME ESTIMATE: [X minutes]
PROMPTING TECHNIQUE: [zero-shot | CoT | CoT+few-shot+role | full stack]
EXECUTE? → GO / ADJUST [what] / CANCEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wait for GO before touching anything.
