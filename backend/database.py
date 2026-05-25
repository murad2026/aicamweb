from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./ai-any-camera.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CameraDB(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    name = Column(String)
    rtsp_url = Column(String)
    brand = Column(String)
    zone = Column(JSON, nullable=True)
    detect_classes = Column(JSON, default=["person"])
    notify_telegram = Column(String, nullable=True)
    notify_whatsapp = Column(String, nullable=True)
    notify_sms = Column(String, nullable=True)
    notify_email = Column(String, nullable=True)
    notify_sms = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import datetime

class EventDB(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer)
    camera_name = Column(String)
    detected = Column(String)
    confidence = Column(String)
    photo_url = Column(String, nullable=True)
    timestamp = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    telegram_message_id = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    telegram_chat_id = Column(String, nullable=True)
    push_token = Column(String, nullable=True)
    is_verified = Column(Integer, default=0)
    verify_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    phone_verified = Column(Integer, default=0)
    plan = Column(String, default="free")
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

Base.metadata.create_all(bind=engine)
