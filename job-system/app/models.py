from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime ,UUID

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)
    user_id = Column(String)
    status = Column(String)
    payload = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer,default =3)
    error_message = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    idempotency_key = Column(String, unique=True)


