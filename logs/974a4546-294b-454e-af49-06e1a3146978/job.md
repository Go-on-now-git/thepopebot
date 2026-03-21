<b>Job Description: Implement Token-Efficient Memory Management</b>

1.  <b>Objective</b>: Modify the conversation history and system prompt handling to drastically reduce input token count, preventing future 429 rate limit errors.
2.  <b>Key Tasks</b>:
    •   <b>System Prompt Condensation</b>: Analyze `operating_system/CHATBOT.md` and create a summarized version, `operating_system/CHATBOT_SUMMARY.md`. This new file will contain only the most critical operational instructions, reducing the static token load of every call.
    •   <b>History Windowing</b>: Modify `event_handler/claude/conversation.js` to implement a fixed-size conversation window. Instead of sending the entire chat history, it will only send the system prompt and the 10 most recent messages.
    •   <b>Code Update</b>: Update the Claude integration in `event_handler/claude/index.js` to use the new `CHATBOT_SUMMARY.md` file for the system prompt.