<b>Job Description: Build Professional Job Monitoring Dashboard</b>

1.  <b>Backend: Simple, Sequential Job IDs</b>
    • Implement a system to assign a simple, sequential ID (e.g., #1, #2) to every new job.
    • This ID will be used for display and in our conversations, while the internal UUID will be maintained for system integrity.

2.  <b>Frontend: Modern Dashboard UI</b>
    • Create a new web endpoint at `/dashboard`.
    • Design a visually appealing, professional dashboard with a modern, minimalist, dark-themed aesthetic.
    • The layout must be responsive and optimized for both desktop and mobile viewing.

3.  <b>Functionality</b>
    • The dashboard will display a real-time list of all jobs.
    • Each entry will show:
        - The simple Job ID (e.g., #1)
        - A concise job description
        - The current status (Running, Completed, or Failed)
        - Creation and completion timestamps.
    • The full UUID should be available but not be the primary identifier.