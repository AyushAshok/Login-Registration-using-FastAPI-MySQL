from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import enum

# MySQL database connection string
DATABASE_URL = "mysql+mysqldb://user:password@localhost/databsaename"  #put your mysql user,password and databasename

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Gender Enum
class Gender(enum.Enum):
    M = "M"
    F = "F"

# Define User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    PAN= Column(String(10),unique=True,nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    dob = Column(Date, nullable=True)
    password = Column(String(128), nullable=False) 

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory=".")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

def userexists(db:Session,email:str,PAN:str)->bool:
    return db.query(User).filter((User.email == email) | (User.PAN == PAN)).first() is not None


@app.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: EmailStr = Form(...),
    PAN: str=Form(...),
    password: str = Form(...),
    dob: str = Form(...),
    gender: Gender = Form(...)
):
    db = SessionLocal()
    try:

        if userexists(db,email,PAN):
            return{"message":"User already exists"}

        user = User(name=name, email=email, password=password,PAN=PAN, dob=dob, gender=gender)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
    return {"message": "User registered successfully!"}

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    email: EmailStr = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email, User.password == password).first()
    db.close()
    if user:
        return {"message": "Login successful!"}
    raise HTTPException(status_code=400, detail="Invalid email or password")
