import os
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()

class GiftCard(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    brand: str = Field(index=True)
    balance: float | None = Field(default=None, index=True)
    category: str = Field(index=True)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/giftcards/")
def create_giftcard(giftcard: GiftCard, session: SessionDep) -> Hero:
    session.add(giftcard)
    session.commit()
    session.refresh(giftcard)
    return giftcard

@app.get("/giftcards/")
def read_cards(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[GiftCard]:
    giftcards = session.exec(select(GiftCard).offset(offset).limit(limit)).all()
    return giftcards

@app.get("/giftcards/{giftcard_id}")
def get_giftcard(giftcard_id: int, session: SessionDep) -> GiftCard:
    giftcard = session.get(GiftCard, giftcard_id)
    if not giftcard:
        raise HTTPException(status_code=404, detail="Giftcard not found")
    return giftcard

@app.delete("/giftcards/{giftcard_id}")
def delete_giftcard(giftcard_id: int, session: SessionDep):
    giftcard = session.get(GiftCard, giftcard_id)
    if not giftcard:
        raise HTTPException(status_code=404, detail="Giftcard not found")
    session.delete(giftcard)
    session.commit()
    return {"ok": True}
