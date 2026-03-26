EMERGENCY DIAGNOSTICS & RECOVERY

Mission: Investigate why the three jobs failed and fix it.

PHASE 1: DIAGNOSIS
- Check GitHub repository for the three failed jobs:
  * 109e8c5b-55bb-4b11-9169-0ba7f34b0a33 (NUB Business Launch)
  * 1a8fd4e9-3a65-4719-b62c-f6d942521bb5 (Discord Setup + Business Launch)
  * 464587d7-dd91-4160-b2ec-6ab08f8387d8 (Fail-Safe System)
- Pull logs from GitHub Actions workflow runs for these job branches
- Identify error messages and failure points
- Check:
  * Secrets configured (SECRETS base64 JSON set in GitHub)
  * Variables configured (GH_WEBHOOK_URL, AUTO_MERGE, ALLOWED_PATHS, IMAGE_URL)
  * Docker image availability
  * ANTHROPIC_API_KEY in SECRETS
  * GH_TOKEN in SECRETS

PHASE 2: ROOT CAUSE ANALYSIS
- Parse error logs from each failed job
- Identify if failure is:
  * Configuration issue (missing secrets/vars)
  * Code issue (job description syntax error)
  * Infrastructure issue (Docker, GitHub Actions, API unavailable)
  * Timeout (job took too long)
  * Permissions issue (GH_TOKEN lacks required scopes)
- Document findings clearly

PHASE 3: FIX & RECOVERY
- Based on root cause, fix the issue:
  * If secrets missing: Add SECRETS & LLM_SECRETS to GitHub Secrets
  * If variables missing: Configure required GitHub Variables
  * If Docker issue: Verify IMAGE_URL or use default stephengpope/thepopebot:latest
  * If code issue: Fix job descriptions and retry
  * If timeout: Extend job timeout limits
  * If API issue: Check rate limits, wait if needed
- Verify all configuration is correct before retry

PHASE 4: RETRY JOBS
- Once root cause is fixed, manually retry the three failed job branches
- Monitor each for success
- If retries fail, escalate to user with detailed findings

DELIVERABLES
- Detailed diagnostic report (root cause identified)
- Configuration checklist (what's missing/broken)
- Recovery steps executed
- Retry status for all three jobs
- If successful: All three jobs now running
- If failed: Complete analysis for manual intervention

CRITICAL: This is a rescue mission. Be thorough in diagnosis and fix the root cause properly before retry.