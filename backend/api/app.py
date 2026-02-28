import os
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
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

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