import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import main
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Set test environment variables before importing the app
os.environ["GEMINI_API_KEY"] = "test_api_key"

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_genai():
    """Mock the Google Generative AI module."""
    with patch('main.genai') as mock:
        yield mock


@pytest.fixture
def mock_gemini_model():
    """Mock the Gemini model and chat functionality."""
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_response_stream = MagicMock()
    
    # Configure the mock chain
    mock_model.start_chat.return_value = mock_chat
    mock_chat.send_message.return_value = mock_response_stream
    
    # Mock streaming chunks
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Hello "
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "world!"
    mock_response_stream.__iter__ = lambda self: iter([mock_chunk1, mock_chunk2])
    
    with patch('main.genai.GenerativeModel', return_value=mock_model):
        yield mock_model, mock_chat, mock_response_stream


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "message": "Hello, how are you?",
        "history": [
            {
                "role": "user",
                "parts": [{"text": "Hi"}]
            },
            {
                "role": "assistant",
                "parts": [{"text": "Hello! How can I help you?"}]
            }
        ]
    }


@pytest.fixture
def empty_chat_request():
    """Empty chat request for testing edge cases."""
    return {
        "message": "Hello",
        "history": []
    }
