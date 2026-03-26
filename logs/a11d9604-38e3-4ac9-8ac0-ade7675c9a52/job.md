Create a distinctive voice for NUB. Build voice identity + implement text-to-speech across all systems.

MISSION: Give NUB a cool, memorable voice that matches the brand — autonomous, confident, intelligent, cutting-edge.

PHASE 1: VOICE IDENTITY DESIGN
- Define voice characteristics:
  * Tone: Cool, tech-forward, confident but approachable
  * Accent: Consider options (neutral American, British tech-forward, European tech-savvy, etc.)
  * Personality: Direct, efficient, slightly futuristic (like a premium AI assistant)
  * Speech patterns: Clear, articulate, no filler words, purposeful
- Research best TTS voices available:
  * Google Cloud TTS (natural, multiple languages/accents)
  * Azure Cognitive Services (high quality, diverse voices)
  * ElevenLabs (AI-generated, very natural, customizable)
  * Anthropic Eleven Labs partnership options
- Test 5-10 candidate voices
- Select the one that best matches brand identity

PHASE 2: VOICE IMPLEMENTATION
- Integrate chosen TTS service into NUB systems:
  * Discord alerts/notifications (voice announcements)
  * YouTube video voiceovers (for the business launch videos)
  * Telegram TTS responses (optional, use push_to_tasker for phone)
  * Event handler status updates (voice summaries)
- Create voice configuration:
  * operating_system/VOICE.md with voice parameters (service, voice_id, speed, tone)
  * Store API credentials in SECRETS
- Build TTS utility: event_handler/utils/text-to-speech.js
  * Convert text to audio files
  * Cache generated audio to avoid reprocessing
  * Support multiple output formats (MP3, WAV, OGG)

PHASE 3: VOICE-FIRST CONTENT
- Record voice intro/outro for YouTube videos (using selected voice)
- Create voice-based Discord announcements for major events
- Add voice summaries for job completions (10-15 second audio clips)
- Voice confirmation messages for critical actions
- Create audio brand identity (jingle/signature sound optional)

PHASE 4: TESTING & REFINEMENT
- Test voice across all platforms (Discord, YouTube, Telegram, etc.)
- Get feedback on clarity, tone, professionalism
- Adjust speed/tone if needed
- Ensure voice matches the video/brand aesthetic

PHASE 5: DOCUMENTATION & DEPLOYMENT
- Document voice usage guidelines in operating_system/VOICE.md
- Create voice templates for common announcements
- Train all systems to use NUB voice consistently
- Make voice part of the brand identity

DELIVERABLES
- Selected TTS service + voice ID
- TTS integration across all platforms
- Voice config file (operating_system/VOICE.md)
- YouTube video voiceovers recorded
- Discord voice alerts tested
- Brand voice guidelines documented
- NUB now has a recognizable, cool voice across all channels

STRATEGY
- Choose voice that's distinctive + professional
- Use consistently across all content (YouTube, Discord, notifications)
- Make voice part of the brand recognition
- Keep voice natural but futuristic (not robotic, not overly theatrical)