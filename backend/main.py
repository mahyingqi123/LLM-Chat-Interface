import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from starlette.responses import StreamingResponse
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

# Configuration 
# Set up the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)

# FastAPI App Initialization
app = FastAPI(
    title="Streaming LLM Chat API",
    description="An API to stream responses from Google's Gemini Pro model.",
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows our React frontend (running on localhost:3000) to communicate with our backend.
# Configure allowed origins for CORS
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternative local port
]

# Add CloudFront domain if available
cloudfront_domain = os.getenv("CLOUDFRONT_DOMAIN")
if cloudfront_domain:
    allowed_origins.extend([
        f"https://{cloudfront_domain}",
        f"http://{cloudfront_domain}"
    ])

# Add custom domain if available
custom_domain = os.getenv("CUSTOM_DOMAIN")
if custom_domain:
    allowed_origins.extend([
        f"https://{custom_domain}",
        f"http://{custom_domain}"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for Data Validation
class Message(BaseModel):
    """Defines the structure of a single message in the chat history."""
    role: str = Field(..., description="Role of the message sender ('user' or 'model').")
    parts: List[Dict[str, Any]] = Field(..., description="Content parts of the message.")

class ChatRequest(BaseModel):
    """Defines the structure of the request body for the /chat endpoint."""
    message: str
    history: List[Message]

# LLM Streaming Logic
async def stream_gemini_response(chat_request: ChatRequest):
    """
    A generator function that calls the Gemini API and yields response chunks.
    """
    try:
        # Reformat history for the Gemini API
        # Gemini expects roles 'user' and 'model'. Our frontend uses 'user' and 'assistant'.
        formatted_history = []
        for msg in chat_request.history:
            # The API expects the 'model' role for assistant messages
            role = "model" if msg.role == "assistant" else msg.role
            formatted_history.append({'role': role, 'parts': msg.parts})
            
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        chat = model.start_chat(history=formatted_history)
        
        # Get the streaming response
        response_stream = chat.send_message(chat_request.message, stream=True)
        
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                await asyncio.sleep(0.01) # Small delay to simulate natural typing
                
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        yield "Error: Could not get response from the model."


# POST request to /api/chat
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Receives a chat message and history, and streams back the LLM's response.
    """
    generator = stream_gemini_response(request)
    return StreamingResponse(generator, media_type="text/plain")
