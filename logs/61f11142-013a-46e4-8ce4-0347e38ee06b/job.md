Diagnose and Repair Job Completion Notification System

Objective:
Restore the automatic Telegram notification functionality that triggers when an autonomous job's pull request is merged.

Plan:
1. Inspect the execution history of the `update-event-handler.yml` GitHub Action to verify if it is running and sending the webhook.
2. Review the event handler logs for the `/github/webhook` endpoint to see if it is receiving requests from GitHub.
3. Examine the notification logic in `event_handler/server.js` and `event_handler/tools/telegram.js` for errors.
4. Verify all related environment variables (`GH_WEBHOOK_URL`, `GH_WEBHOOK_SECRET`, `TELEGRAM_BOT_TOKEN`) are correctly loaded.
5. Implement a fix to restore the notification pipeline.
6. As part of the fix, I will add a new `send_test_notification` tool to my shell so I can verify the system is working at any time.