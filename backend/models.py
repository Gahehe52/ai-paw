from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register
from datetime import datetime

DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    review_text = Column(Text, nullable=False)
    sentiment = Column(String(20)) # POSITIVE, NEGATIVE
    confidence = Column(Float)
    key_points = Column(Text) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)