# LLM-Chat-Interface

A modern, streaming chat interface for interacting with Google's Gemini AI model. Built with FastAPI backend and React frontend, deployed on AWS for production use.

## Features

- **Real-time Streaming**: Chat responses stream in real-time for natural conversation flow
- **Modern UI**: Clean, responsive React interface with auto-scrolling
- **Production Ready**: Deployed on AWS with Docker containerization

## Architecture

```
Frontend (React) → S3 Static Hosting 
                      
Backend (FastAPI) → Docker Container → EC2 Instance 
                      ↓
                  Gemini AI API
```

## Prerequisites

1. **Python 3.10+** and pip
2. **Docker** and Docker Compose
3. **Node.js 18+** and npm
4. **AWS CLI** configured with appropriate permissions
5. **Google Gemini API key**

## Quick Start (Local Development)

### Backend Setup
```bash
cd backend

# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

The backend will be available at: http://localhost:8000

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at: http://localhost:3000

## Docker Development

Run both services with Docker Compose:

```bash
# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > backend/.env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## AWS Deployment

This project includes complete AWS deployment configurations for production use.

### Architecture Components

- **Frontend**: S3 Static Website + CloudFront CDN
- **Backend**: Docker container on EC2 instance
- **Container Registry**: AWS ECR for Docker images

### Deployment 

1. **Launch EC2 instance** (t2.micro for free tier)
2. **Build and push to ECR**:
   ```bash
   # Build and tag image
   docker build -t llm-chat-backend ./backend
   docker tag llm-chat-backend:latest YOUR_ECR_URI:latest
   
   # Push to ECR
   aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
   docker push YOUR_ECR_URI:latest
   ```

3. **Deploy on EC2**:
   ```bash
   # SSH into EC2 instance
   ssh -i your-key.pem ec2-user@your-ec2-ip
   
   # Pull and run container
   aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
   docker run -d --name llm-chat-backend -p 8000:8000 -e GEMINI_API_KEY=your_key YOUR_ECR_URI:latest
   ```

4. **Deploy frontend to S3**:
   ```bash
   cd frontend
   echo "REACT_APP_API_BASE_URL=http://YOUR_EC2_IP:8000" > .env.production
   npm run build
   aws s3 sync build/ s3://your-bucket-name --delete
   ```

### Security Group Configuration

Ensure your EC2 security group allows:
- **Port 22**: SSH access
- **Port 8000**: Backend API access

## Configuration

### Environment Variables

#### Backend (.env)
```bash
GEMINI_API_KEY=your_gemini_api_key_here
CLOUDFRONT_DOMAIN=your-frontend-domain.com  # Optional: for CORS
CUSTOM_DOMAIN=your-custom-domain.com         # Optional: for CORS
```

#### Frontend (.env.production)
```bash
REACT_APP_API_BASE_URL=http://your-backend-url:8000
```

## Project Structure

```
LLM-Chat-Interface/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Backend container config
│   └── .dockerignore          # Docker ignore patterns
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   └── App.css            # Styling
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── Dockerfile             # Frontend container config
```

### Main Endpoint

**POST** `/api/chat`
```json
{
  "message": "Hello, how are you?",
  "history": [
    {
      "role": "user",
      "parts": [{"text": "Previous message"}]
    },
    {
      "role": "assistant", 
      "parts": [{"text": "Previous response"}]
    }
  ]
}
```

## Development

### Local Development with Hot Reload

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm start
```

### Building for Production

```bash
# Backend
docker build -t llm-chat-backend ./backend

# Frontend
cd frontend
npm run build
```

## Testing

### Running Tests

```bash
# Backend tests
cd backend && pytest -v

# Frontend tests
cd frontend && npm test -- --watchAll=false
```

### Test Coverage

The project includes comprehensive test coverage for:

**Backend Tests:**
- FastAPI app initialization and configuration
- Chat endpoint functionality and validation
- Streaming response handling
- Error handling and edge cases
- CORS configuration
- Environment variable handling
- API integration with Gemini

**Frontend Tests:**
- React component rendering and state management
- User input handling and validation
- API integration and error handling
- Message display and chat functionality
- Loading states and UI interactions
- Form submission and keyboard events
- Auto-scroll behavior
- Edge cases and special characters

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS settings include your frontend domain
2. **Container Health Check Fails**: The health check requires `curl` - this is expected in minimal containers
3. **Port Access Issues**: Verify security group settings allow the required ports
4. **Environment Variables**: Double-check API keys and URLs are correctly set
5. **Test Failures**: Ensure all dependencies are installed and environment variables are set

### Debug Commands

```bash
# Check container status
docker ps
docker logs llm-chat-backend

# Test backend connectivity
curl http://localhost:8000/docs

# Check AWS resources
aws ec2 describe-instances
aws s3 ls

```
## Demo

**Note**: The live demo is not publicly available as it requires rate limiting and additional security features for public use. Contact the repository owner for access to the deployed version.






