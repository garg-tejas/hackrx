# HackRx 6.0 - Simplified LLM-Powered Query-Retrieval System

A streamlined document query system that uses Google Gemini AI to answer questions from PDF documents with direct text processing.

## 🎯 Features

- **Direct PDF Processing**: Uses Google Gemini AI for native PDF understanding
- **Simplified Architecture**: No complex chunking or embedding required
- **Rate Limiting**: Built-in rate limiting for API quota management
- **Explainable AI**: Detailed reasoning and confidence scores for all answers
- **Structured Output**: JSON responses with answers, explanations, and confidence scores
- **High Performance**: Optimized for accuracy and low latency
- **RESTful API**: FastAPI-based API with comprehensive documentation

## 🏗️ System Architecture

```
PDF URL → Download → Gemini AI Processing → Structured Response
```

The system uses a simplified approach with direct PDF processing via Google Gemini AI.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google API key (for Gemini)
- Pinecone API key (optional, for cloud vector storage)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd hackrx-system
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

The API will be available at `http://localhost:8000`

## 📋 API Documentation

### Main Endpoint

**POST** `/api/v1/hackrx/run`

Process document queries and return structured answers.

**Request Body:**

```json
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?"
  ]
}
```

**Response:**

```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payments...",
    "Yes, the policy covers maternity expenses..."
  ],
  "explanations": [
    "The document states that a 30-day grace period is allowed...",
    "Maternity coverage is explicitly mentioned in section 3.2..."
  ]
}
```

### Additional Endpoints

- **GET** `/api/v1/health` - Health check
- **GET** `/api/v1/stats` - Processing statistics
- **POST** `/api/v1/clear` - Clear processing session
- **POST** `/api/v1/test` - Test single query

## 🔧 Configuration

Key configuration options in `.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# External APIs
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_LENGTH=4000
EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Configuration
LLM_MODEL=gemini-2.0-flash-exp
MAX_TOKENS=1500
TEMPERATURE=0.1
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/test_services.py -v
```

### Run API Tests

```bash
pytest tests/test_api.py -v
```

### Run All Tests

```bash
pytest tests/ -v
```

## 📊 Performance Metrics

The system is optimized for:

- **Accuracy**: >85% correct clause identification
- **Latency**: <3 seconds per query response
- **Token Efficiency**: <2000 tokens per complex query
- **API Compatibility**: 100% match with provided specification
- **Explainability**: Clear reasoning for every answer

## 🏗️ Project Structure

```
hackrx-system/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Environment configuration
│   ├── models/
│   │   ├── schemas.py         # Pydantic models for API
│   │   └── database.py        # SQLAlchemy models
│   ├── services/
│   │   ├── document_processor.py    # PDF/DOCX/Email parsing
│   │   ├── embedding_service.py     # Vector embeddings
│   │   ├── llm_service.py          # OpenAI GPT-4 integration
│   │   ├── retrieval_service.py    # FAISS/Pinecone search
│   │   └── query_processor.py      # Main business logic
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   └── utils/
│       ├── helpers.py         # Utility functions
│       └── exceptions.py      # Custom exceptions
├── tests/
│   ├── test_services.py
│   └── test_api.py
├── requirements.txt
├── env.example
└── README.md
```

## 🔍 Key Components

### Document Processor

- Downloads documents from blob URLs
- Extracts text from PDF, DOCX, and email formats
- Implements smart text chunking with overlap
- Extracts metadata and document structure

### Embedding Service

- Uses Sentence Transformers for text embeddings
- FAISS integration for fast vector search
- Configurable similarity thresholds
- Index persistence and management

### LLM Service

- Google Gemini 2.5 Flash integration
- Query understanding and intent extraction
- Context-aware answer generation
- Explainable reasoning generation

### Query Processor

- Main orchestrator for the complete pipeline
- Manages context windows and token limits
- Provides structured responses
- Implements error recovery mechanisms

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t hackrx-system .

# Run the container
docker run -p 8000:8000 --env-file .env hackrx-system
```

### Production Deployment

1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables for production
3. Use a production ASGI server (Gunicorn + Uvicorn)
4. Set up monitoring and logging
5. Configure reverse proxy (Nginx)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` when running the server

---

**Built for HackRx 6.0 - LLM-Powered Intelligent Query-Retrieval System**
