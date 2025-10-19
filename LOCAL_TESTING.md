# Local Testing Guide

This project supports an OFFLINE_MODE for local testing without external APIs.

1) Server login
- Superuser: admin / admin1234
- Tester: tester / test1234

2) Offline mode (default)
- .env contains OFFLINE_MODE=True and DEBUG=True
- Humanizer uses a local rewriter, Paystack calls are mocked, emails go to console.

3) Test with real OpenAI key locally
- Edit .env:
  - OFFLINE_MODE=False
  - OPENAI_API_KEY=sk-...your key...
    - GEMINI_API_KEY=AIza...your key...
  - Optionally set:
      - OPENAI_MODEL=gpt-4.1 (or your preferred model)
      - GEMINI_MODEL=gemini-2.5-flash (or gemini-2.5-pro)
    - HUMANIZER_SYSTEM_PROMPT=...override system prompt...
    - HUMANIZER_USER_PREFIX=...text prefixed to the user message...
      - HUMANIZER_ENGINE=openai|gemini (default openai if not specified; UI selection overrides on submit)

4) Switch back to production
- Turn OFFLINE_MODE off in production and configure DATABASE_URL, SMTP, and Paystack keys.

5) Notes
- Pricing page geolocation fetch may fail if totally offline; it’s not required for humanizer testing.
- When OFFLINE_MODE=True, Paystack init/verify are simulated and update your profile quotas locally.