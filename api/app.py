from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rwanda.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

engine = create_engine(DATABASE_URL, echo=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: Optional[str] = None
    hashed_password: Optional[str] = None
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
    image_path: Optional[str] = None


class AgentRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int
    rater_id: int
    score: int
    comment: Optional[str] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI(title="Rwanda Housing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static and uploaded media
os.makedirs("static", exist_ok=True)
os.makedirs("media/property_images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")


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
def create_property(property: Property, current_user: User = Depends(get_current_user_from_token)):
    property.owner_id = current_user.id
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


@app.post("/api/register")
def register(username: str, email: Optional[str] = None, password: str = None):
    if not password:
        raise HTTPException(status_code=400, detail="Password required")
    hashed = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/login")
def login(username: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}


@app.post("/api/properties/{property_id}/upload-image")
def upload_property_image(property_id: int, file: UploadFile = File(...)):
    # Save uploaded file to media/property_images
    upload_dir = os.path.join("media", "property_images")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{property_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    with Session(engine) as session:
        prop = session.get(Property, property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        prop.image_path = f"/media/property_images/{filename}"
        session.add(prop)
        session.commit()
        session.refresh(prop)
        return {"image_url": prop.image_path}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Rwanda Housing FastAPI backend is running."}
