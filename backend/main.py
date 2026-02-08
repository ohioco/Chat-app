
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Message
from auth import hash_password, verify_password, create_token
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "User exists")
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return {"status": "registered"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_token(username)}

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            for conn in connections:
                await conn.send_text(data)
    except:
        connections.remove(ws)
