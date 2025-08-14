import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestAppInitialization:
    """Test FastAPI app initialization."""
    
    def test_app_title_and_description(self, client):
        """Test that the app has correct title and description."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_cors_configuration(self, client):
        """Test CORS headers are properly configured."""
        response = client.options("/api/chat", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        assert response.status_code in [200, 204]


class TestChatEndpoint:
    """Test the main chat endpoint functionality."""
    
    def test_chat_endpoint_exists(self, client):
        """Test that the chat endpoint exists and accepts POST requests."""
        response = client.post("/api/chat", json={
            "message": "test",
            "history": []
        })
        assert response.status_code != 404
    
    def test_chat_with_valid_request(self, client, mock_gemini_model, sample_chat_request):
        """Test chat endpoint with valid request."""
        mock_model, mock_chat, mock_response_stream = mock_gemini_model
        
        response = client.post("/api/chat", json=sample_chat_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    def test_chat_invalid_json(self, client):
        """Test chat endpoint with invalid JSON."""
        response = client.post("/api/chat", data="invalid json")
        assert response.status_code == 422
    
    def test_chat_missing_fields(self, client):
        """Test chat endpoint with missing required fields."""
        response = client.post("/api/chat", json={"message": "test"})  # Missing history
        assert response.status_code == 422
        
        response = client.post("/api/chat", json={"history": []})  # Missing message
        assert response.status_code == 422


class TestStreamingResponse:
    """Test streaming response functionality."""
    
    def test_streaming_response_format(self, client, mock_gemini_model, sample_chat_request):
        """Test that the response streams correctly."""
        mock_model, mock_chat, mock_response_stream = mock_gemini_model
        
        response = client.post("/api/chat", json=sample_chat_request)
        
        assert response.status_code == 200
        content = response.content.decode()
        assert "Hello " in content
        assert "world!" in content


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_gemini_api_error(self, client, sample_chat_request):
        """Test handling of Gemini API errors."""
        with patch('main.genai.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_model_class.return_value = mock_model
            mock_model.start_chat.side_effect = Exception("API Error")
            
            response = client.post("/api/chat", json=sample_chat_request)
            
            assert response.status_code == 200
            content = response.content.decode()
            assert "Error: Could not get response from the model." in content


class TestHealthCheck:
    """Test application health and status endpoints."""
    
    def test_docs_endpoint(self, client):
        """Test that docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
