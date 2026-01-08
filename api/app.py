from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rwanda.db")

engine = create_engine(DATABASE_URL, echo=False)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: Optional[str] = None
    user_type: Optional[str] = "buyer"
    phone: Optional[str] = None
    bio: Optional[str] = None


class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    location: Optional[str] = None
    price: Optional[float] = 0.0
    property_type: Optional[str] = None
    listing_type: Optional[str] = "sale"
    description: Optional[str] = None
    owner_id: Optional[int] = None


class AgentRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int
    rater_id: int
    score: int
    comment: Optional[str] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI(title="Rwanda Housing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/api/properties", response_model=List[Property])
def list_properties():
    with Session(engine) as session:
        props = session.exec(select(Property)).all()
        return props


@app.get("/api/properties/{property_id}", response_model=Property)
def get_property(property_id: int):
    with Session(engine) as session:
        prop = session.get(Property, property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        return prop


@app.post("/api/properties", response_model=Property)
def create_property(property: Property):
    with Session(engine) as session:
        session.add(property)
        session.commit()
        session.refresh(property)
        return property


@app.get("/api/users", response_model=List[User])
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@app.post("/api/users", response_model=User)
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Rwanda Housing FastAPI backend is running."}
