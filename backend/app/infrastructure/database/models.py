from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)


class QueryHistory(Base):
    """Stores AI query results per user: query text, SQL, answer, and data."""

    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    sql_queries_json = Column(Text, nullable=True)  # JSON array of SQL strings
    answer = Column(Text, nullable=True)
    data_json = Column(Text, nullable=True)  # JSON array of result rows
    conversation_flow_json = Column(Text, nullable=True)  # JSON for conversation_flow
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
