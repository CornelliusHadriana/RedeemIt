import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import create_db_and_tables
from api.routes import auth, giftcards, transactions, users

app = FastAPI(
    title="RedeemIt API",
    description="Gift card management API",
    version="1.0.0"
)

# Get CORS origins from environment or use defaults
# Handle both JSON array format and comma-separated format
origins_env = os.getenv("ALLOWED_ORIGINS", "")
use_wildcard = False

if origins_env == "*" or not origins_env:
    # Allow all origins - use regex to support credentials
    allowed_origins = []
    use_wildcard = True
elif origins_env.startswith("["):
    # JSON array format
    try:
        allowed_origins = json.loads(origins_env)
    except json.JSONDecodeError:
        allowed_origins = []
        use_wildcard = True
else:
    # Comma-separated format
    allowed_origins = [o.strip() for o in origins_env.split(",")]

if use_wildcard:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(giftcards.router)
app.include_router(transactions.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "RedeemIt API", "docs": "/docs"}