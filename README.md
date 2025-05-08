# Slack Bolt AI Assistant & Agent Template

This project demonstrates how to build Slack assistants and agents using the OpenAI Agents SDK, SQLAlchemy ORM, and a clean, scalable Python architecture.

## Project Structure

```
mooai/
├── app.py                  # Main entrypoint, Slack Bolt app setup
├── requirements.txt
├── README.md
│
├── listeners/              # Slack event/callback listeners ONLY
│   ├── __init__.py
│   └── assistant.py        # Slack assistant thread logic
│
├── agents/                 # Agent logic and OpenAI SDK integration
│   ├── __init__.py
│   └── agent_service.py    # call_agent, call_agent_sync, etc.
│
├── db/                     # Database models and session management
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM models
│   └── session.py          # SessionLocal, init_db
└── ...
```

**Key points:**
- `listeners/` is only for Slack event handlers (no business logic or DB code).
- `agents/` contains all OpenAI agent/LLM logic and agent-to-DB mapping.
- `db/` contains all SQLAlchemy ORM models and session setup.

---
