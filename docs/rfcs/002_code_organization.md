srijan/
├── README.md
│
├── migrations/                    
│   └── v0.1.0_initial_schema.sql
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # pydantic-settings Settings, loaded once
│   ├── logging.py                  # structured logging setup
│   │
│   ├── api/                        # ── FastAPI webhook server
│   │   └── routes/
│   │
│   ├── workers/                    # ── Celery workers
│   │
│   ├── agents/                     # ── Agent Platform integration 
│   │
│   ├── chat/                       # ── Chat Platform integration 
│   │
│   ├── db/                         # ── PostgreSQL 
│   │
│   └── domain/                     # ── pure logic, no I/O
│
└── tests/