from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

from api.routes import auth, giftcards, transactions, users
from api.database import create_db_and_tables


app = FastAPI(
    title="RedeemIt API",
    description="Backend API for RedeemIt application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(giftcards.router)
app.include_router(transactions.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to RedeemIt API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
