---
phase: quick
plan: 1
type: execute
wave: 1
depends_on: []
files_modified:
  - .github/workflows/daily-content.yml
autonomous: true
requirements: [QUICK-01]

must_haves:
  truths:
    - "Content pipeline runs automatically on Monday, Wednesday, and Friday only"
    - "Pipeline triggers at 7 PM WIB (12:00 UTC) on scheduled days"
    - "Manual trigger (workflow_dispatch) still works any day"
  artifacts:
    - path: ".github/workflows/daily-content.yml"
      provides: "Scheduled GitHub Actions workflow for MWF at 7 PM WIB"
      contains: "cron: '0 12 * * 1,3,5'"
  key_links:
    - from: ".github/workflows/daily-content.yml"
      to: "main.py"
      via: "python main.py step"
      pattern: "python main.py"
---

<objective>
Update the GitHub Actions workflow schedule from daily at 07:00 WIB to Monday/Wednesday/Friday at 19:00 WIB.

Purpose: Content only needs to be generated 3 times per week (Mon, Wed, Fri), and the team prefers receiving it at 7 PM WIB for evening review before the next morning's post.
Output: Updated `.github/workflows/daily-content.yml` with new cron schedule.
</objective>

<execution_context>
@/Users/anitawulandari/.claude/get-shit-done/workflows/execute-plan.md
@/Users/anitawulandari/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.github/workflows/daily-content.yml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update workflow cron schedule to MWF 7 PM WIB</name>
  <files>.github/workflows/daily-content.yml</files>
  <action>
Modify `.github/workflows/daily-content.yml`:

1. Update the cron expression from `'0 0 * * *'` to `'0 12 * * 1,3,5'`
   - `0 12` = 12:00 UTC = 19:00 WIB (UTC+7)
   - `1,3,5` = Monday, Wednesday, Friday
   - Note: WIB does not observe daylight saving time, so offset is always +7

2. Update the comment above the cron line to reflect the new schedule:
   - Change from: `# 00:00 UTC = 07:00 WIB`
   - Change to: `# 12:00 UTC = 19:00 WIB (Western Indonesia Time, UTC+7)`
   - Add: `# Runs Monday, Wednesday, Friday only`

3. Update the workflow name from `Daily Content Pipeline` to `Content Pipeline (Mon/Wed/Fri)` to reflect the new cadence.

4. Update the top-of-file comment from `# Daily Content Pipeline` to `# Content Pipeline for PUM Indonesia Instagram (Mon/Wed/Fri at 19:00 WIB)`.

5. Keep `workflow_dispatch` trigger unchanged (manual runs should still work any day).

6. Keep all other configuration (Python version, secrets, timeout, steps) exactly as-is.
  </action>
  <verify>
    <automated>grep -q "0 12 \* \* 1,3,5" .github/workflows/daily-content.yml && grep -q "workflow_dispatch" .github/workflows/daily-content.yml && echo "PASS: Cron schedule updated to MWF 12:00 UTC with manual trigger preserved" || echo "FAIL"</automated>
  </verify>
  <done>Workflow cron runs at 12:00 UTC (19:00 WIB) on Monday, Wednesday, Friday only. Manual dispatch still available. All other workflow config unchanged.</done>
</task>

</tasks>

<verification>
- `grep "cron:" .github/workflows/daily-content.yml` shows `'0 12 * * 1,3,5'`
- `grep "workflow_dispatch" .github/workflows/daily-content.yml` confirms manual trigger still present
- No other changes to steps, secrets, Python version, or timeout
</verification>

<success_criteria>
- GitHub Actions workflow is scheduled for Monday, Wednesday, Friday at 12:00 UTC (19:00 WIB)
- Manual workflow_dispatch trigger is preserved
- All pipeline steps, secrets, and configuration remain unchanged
</success_criteria>

<output>
After completion, create `.planning/quick/1-auto-github-content-creation-schedule-mw/1-SUMMARY.md`
</output>
