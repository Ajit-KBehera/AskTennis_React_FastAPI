"""
Integration tests for AuthDBService using an in-memory database.
"""
import pytest
from app.api.auth_models import User

class TestAuthDBIntegration:
    def test_create_and_get_user(self, auth_db_service_mock, test_db_session):
        """Test user lifecycle: creation and retrieval."""
        service = auth_db_service_mock
        db = test_db_session
        
        # Create user
        user = User(username="testuser", hashed_password="hashed_123")
        service.create_user(db, user)
        
        # Retrieve user
        retrieved = service.get_user_by_username(db, "testuser")
        assert retrieved is not None
        assert retrieved.username == "testuser"
        assert retrieved.hashed_password == "hashed_123"

    def test_query_history_persistence(self, auth_db_service_mock, test_db_session):
        """Test saving and retrieving query history."""
        service = auth_db_service_mock
        db = test_db_session
        
        # Create user first
        user = User(username="history_user", hashed_password="...")
        service.create_user(db, user)
        
        # Save history
        service.save_query_history(
            db=db,
            user_id=user.id,
            query_text="Who is Federer?",
            sql_queries=["SELECT * FROM players"],
            answer="Tennis legend.",
            data=[{"name": "Roger"}],
            conversation_flow=[{"role": "user", "content": "..."}]
        )
        
        # Retrieve
        history = service.get_query_history_for_user(db, user.id)
        assert len(history) == 1
        assert history[0]["query_text"] == "Who is Federer?"
        assert history[0]["answer"] == "Tennis legend."
        assert history[0]["sql_queries"] == ["SELECT * FROM players"]
        assert history[0]["data"] == [{"name": "Roger"}]

    def test_get_user_not_found(self, auth_db_service_mock, test_db_session):
        """Test retrieval of non-existent user."""
        service = auth_db_service_mock
        db = test_db_session
        assert service.get_user_by_username(db, "nonexistent") is None
