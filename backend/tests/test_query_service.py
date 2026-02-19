"""
Unit tests for QueryProcessor logic.
"""
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from services.query_service import QueryProcessor

class TestQueryProcessor:
    @pytest.fixture
    def processor(self):
        return QueryProcessor()

    def test_serialize_messages_basic(self, processor):
        """Test serialization of standard messages."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        serialized = processor._serialize_messages(messages)
        
        assert len(serialized) == 2
        assert serialized[0]["type"] == "HumanMessage"
        assert serialized[0]["content"] == "Hello"
        assert serialized[1]["type"] == "AIMessage"
        assert serialized[1]["content"] == "Hi there!"

    def test_serialize_messages_with_tool_calls(self, processor):
        """Test serialization of AI messages with tool calls."""
        ai_msg = AIMessage(
            content="",
            tool_calls=[{"name": "test_tool", "args": {"a": 1}, "id": "1"}]
        )
        serialized = processor._serialize_messages([ai_msg])
        
        assert len(serialized) == 1
        assert "tool_calls" in serialized[0]
        assert serialized[0]["tool_calls"][0]["name"] == "test_tool"
        assert serialized[0]["tool_calls"][0]["args"] == {"a": 1}

    def test_process_agent_response_string(self, processor):
        """Test final answer extraction from string content."""
        msg = AIMessage(content="The final answer")
        answer = processor.process_agent_response([msg])
        assert answer == "The final answer"

    def test_process_agent_response_list(self, processor):
        """Test final answer extraction from list-style content (common in some LLM types)."""
        msg = MagicMock()
        msg.content = [{"text": "Extracted answer"}]
        answer = processor.process_agent_response([msg])
        assert answer == "Extracted answer"

    @pytest.mark.asyncio
    async def test_handle_user_query_success(self, processor):
        """Test handle_user_query orchestration."""
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "messages": [AIMessage(content="Agent response")],
            "sql_queries": ["SELECT * FROM table"],
            "data_list": [{"col": "val"}]
        }
        
        result = processor.handle_user_query("test question", mock_graph)
        
        assert result["answer"] == "Agent response"
        assert result["sql_queries"] == ["SELECT * FROM table"]
        assert result["data"] == [{"col": "val"}]
        assert "conversation_flow" in result
        assert "session_id" in result
