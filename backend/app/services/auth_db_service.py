import json
from sqlalchemy.orm import sessionmaker, Session
from app.core.config.database.database_factory import DatabaseFactory
from app.api.auth_models import User, QueryHistory, Base
from typing import Optional, List, Dict, Any, cast

class AuthDBService:
    def __init__(self):
        self.db_config = DatabaseFactory.create_auth_config()
        self.engine = self.db_config.get_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Ensure tables are created
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            # Prevent startup crash if DB doesn't exist yet
            import logging
            logging.error(f"Failed to initialize auth tables: {e}")
            logging.warning("Ensure the database 'asktennis_auth' exists in your SQL instance.")

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, user_obj: User) -> User:
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj

    def update_last_login(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from datetime import datetime, timezone
            user.last_login = cast(Any, datetime.now(timezone.utc))
            db.commit()

    def save_query_history(
        self,
        db: Session,
        user_id: int,
        query_text: str,
        sql_queries: List[str],
        answer: str,
        data: List[Dict[str, Any]],
        conversation_flow: Optional[List[Any]] = None,
    ) -> QueryHistory:
        """Save a single AI query result for the given user."""
        record = QueryHistory(
            user_id=user_id,
            query_text=query_text,
            sql_queries_json=json.dumps(sql_queries) if sql_queries else None,
            answer=answer or None,
            data_json=json.dumps(data) if data else None,
            conversation_flow_json=json.dumps(conversation_flow) if conversation_flow else None,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_query_history_for_user(
        self, db: Session, user_id: int, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Return recent query history for a user, with JSON fields parsed."""
        rows = (
            db.query(QueryHistory)
            .filter(QueryHistory.user_id == user_id)
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "query_text": r.query_text,
                "sql_queries": json.loads(cast(str, r.sql_queries_json)) if r.sql_queries_json else [],
                "answer": r.answer or "",
                "data": json.loads(cast(str, r.data_json)) if r.data_json else [],
                "conversation_flow": json.loads(cast(str, r.conversation_flow_json)) if r.conversation_flow_json else [],
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return result
