Use Claude Code to directly investigate GitHub repository configuration and job failures.

MISSION: Run Claude Code to check:
1. GitHub repository secrets (SECRETS, LLM_SECRETS, ANTHROPIC_API_KEY, GH_TOKEN)
2. GitHub repository variables (GH_WEBHOOK_URL, AUTO_MERGE, ALLOWED_PATHS, IMAGE_URL)
3. Failed job branches and their GitHub Actions logs
4. Check the three specific failed jobs:
   - job/109e8c5b-55bb-4b11-9169-0ba7f34b0a33
   - job/1a8fd4e9-3a65-4719-b62c-f6d942521bb5
   - job/464587d7-dd91-4160-b2ec-6ab08f8387d8
5. Pull full error logs from GitHub Actions workflow runs
6. Identify exact failure reasons
7. Report findings back to user with specific configuration issues

EXECUTION STEPS:
- Use gh CLI to check repository secrets (list names only, no values for security)
- Use gh CLI to check repository variables
- Use gh CLI to list recent workflow runs
- Use gh CLI to get full logs from failed runs
- Parse error messages
- Create detailed report with:
  * What's missing/incorrect
  * What needs to be fixed
  * Step-by-step fix instructions
  * Confirmation steps

TOOLS TO USE:
- GitHub CLI (gh) commands
- Claude Code's bash execution
- File system access to check local .env
- API calls if needed

This is a diagnostic mission. Be thorough and accurate.