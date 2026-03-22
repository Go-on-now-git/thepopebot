Job Description: Core Performance Remediation

1.  Objective: Immediately fix the identified performance regressions, specifically the failure to follow up on tasks, provide status updates, and reliably report job outcomes.

2.  Action Plan:
    *   Task 1: Enforce Conversational Follow-up. I will modify my core chat prompt (operating_system/CHATBOT.md) to include a strict, non-negotiable rule: After stating an action (e.g., "I will check the logs") or using a tool, my very next response must provide the result of that action. This will be framed as a primary directive to prevent dropped context.
    *   Task 2: Reinforce Job Completion Reporting. I will analyze and strengthen the job completion notification pipeline (.github/workflows/update-event-handler.yml and event_handler/server.js). I will ensure that even if a job summary fails, a basic completion status (success/failure) is always reported to you, preventing silent failures.
    *   Task 3: Investigate and Report on Project Chimera. As the first test of this new protocol, this job will include a final step: to find the session logs for the Chimera job (58a75fdc-e8c0-4872-94d8-a766c436f510), determine its outcome, and report the findings directly to you upon completion of this remediation job.