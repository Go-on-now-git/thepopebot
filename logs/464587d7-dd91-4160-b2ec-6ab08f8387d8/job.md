Build integrated fail-safe & auto-recovery system for NUB autonomy during sleep/downtime.

MISSION: Create bulletproof automation that handles failures, retries, and alerts without manual intervention.

PHASE 1: GITHUB ACTIONS RETRY LAYER
- Add retry logic to run-job.yml (max 3 attempts, exponential backoff: 30s → 60s → 120s)
- Use nick-fields/retry action for robust step-level retry
- Log all retry attempts with timestamps
- Send final failure notification to Discord if exhausted

PHASE 2: N8N AUTO-RECOVERY WORKFLOW
- Create new n8n workflow: "Job Auto-Retry Engine"
- Scheduled trigger: runs every 15 minutes
- Queries n8n for failed job executions from last 4 hours
- Automatic retry logic with exponential backoff (max 3 retries per job)
- Logs retry attempts to database/sheet for audit trail
- Triggers Discord alert when retry succeeds or final failure occurs
- Filters out jobs already retried to prevent infinite loops

PHASE 3: EVENT HANDLER RESILIENCE
- Add PM2 health check script (event_handler/health-check.js)
- Monitor HTTP /health endpoint every 30 seconds
- Auto-restart event handler if unhealthy (max 5 restarts/hour)
- Log restart attempts for debugging
- Send Discord notification on unexpected restart

PHASE 4: DISCORD ALERT & MANUAL OVERRIDE
- Create Discord alert template with:
  * Job ID, error type, timestamp
  * Auto-recovery status (retrying / exhausted)
  * Manual override button (webhook to manually trigger retry)
- Alert severity levels: warning (1st retry), critical (final failure)
- Archive all alerts for post-mortem analysis

PHASE 5: INTEGRATION & TESTING
- Wire Discord alerts into all three layers (GitHub, n8n, event handler)
- Test failure scenarios:
  * Temporary API timeouts (should auto-recover)
  * Persistent errors (should alert after retries exhausted)
  * Event handler crash (should auto-restart)
- Document fail-safe procedures in operating_system/FAILSAFE.md

IMPLEMENTATION ORDER
1. GitHub Actions: Add retry layer to run-job.yml (5 min setup)
2. n8n: Build auto-retry workflow (10 min build + test)
3. Event Handler: PM2 health check + Discord alerts (10 min setup)
4. Discord: Configure webhooks & alert templates (5 min)
5. Testing: Run failure simulations (15 min)

EFFICIENCY FOCUS
- Minimize manual intervention (fully autonomous)
- Prevent duplicate retries (idempotency checks)
- Smart exponential backoff (don't hammer failing services)
- Central Discord dashboard for all alerts & manual overrides
- Keep setup simple (no complex monitoring infrastructure)

DELIVERABLES
- Updated GitHub workflows with retry logic
- Active n8n auto-retry workflow
- Event handler health check running via PM2
- Discord alerts configured & tested
- FAILSAFE.md documentation
- All systems tested and verified working during sleep/offline periods