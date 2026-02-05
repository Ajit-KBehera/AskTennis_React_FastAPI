from sqlalchemy.orm import sessionmaker, Session
from config.database.database_factory import DatabaseFactory
from api.auth_models import User, Base
from typing import Optional

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
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.commit()
