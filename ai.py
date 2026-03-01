"""
AI Integration Routes
=====================

API endpoints for AI operations:
- Text generation
- Text summarization
- Question answering
- Sentiment analysis
- Code generation

Endpoints:
- POST /api/ai/generate - Generate text
- POST /api/ai/summarize - Summarize text
- POST /api/ai/answer - Answer question
- POST /api/ai/sentiment - Analyze sentiment
- POST /api/ai/code - Generate code

Author: Manus AI
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

# Import from parent modules
import sys
sys.path.append('..')
from database import get_db, User, create_ai_session, update_ai_session, AISessionStatus
from routes.auth import get_current_user
from ai_service import get_ai_service, is_ai_available

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GenerateTextRequest(BaseModel):
    """Text generation request"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="Text prompt")
    max_tokens: int = Field(default=500, ge=10, le=2000, description="Maximum tokens in response")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity level")
    session_name: Optional[str] = Field(None, max_length=100, description="Name for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a short poem about artificial intelligence",
                "max_tokens": 500,
                "temperature": 0.7,
                "session_name": "Poetry Generation"
            }
        }


class SummarizeTextRequest(BaseModel):
    """Text summarization request"""
    text: str = Field(..., min_length=10, max_length=10000, description="Text to summarize")
    max_length: int = Field(default=150, ge=50, le=1000, description="Maximum summary length")
    session_name: Optional[str] = Field(None, max_length=100, description="Name for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Long article text here...",
                "max_length": 150,
                "session_name": "Article Summary"
            }
        }


class AnswerQuestionRequest(BaseModel):
    """Question answering request"""
    context: str = Field(..., min_length=10, max_length=5000, description="Context information")
    question: str = Field(..., min_length=5, max_length=500, description="Question to answer")
    session_name: Optional[str] = Field(None, max_length=100, description="Name for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "context": "Paris is the capital of France",
                "question": "What is the capital of France?",
                "session_name": "Q&A Session"
            }
        }


class SentimentAnalysisRequest(BaseModel):
    """Sentiment analysis request"""
    text: str = Field(..., min_length=5, max_length=2000, description="Text to analyze")
    session_name: Optional[str] = Field(None, max_length=100, description="Name for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I absolutely love this product! It's amazing!",
                "session_name": "Sentiment Analysis"
            }
        }


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    description: str = Field(..., min_length=10, max_length=1000, description="Code description")
    language: str = Field(default="Python", description="Programming language")
    session_name: Optional[str] = Field(None, max_length=100, description="Name for this session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Function to calculate factorial of a number",
                "language": "Python",
                "session_name": "Code Generation"
            }
        }


class AIResponse(BaseModel):
    """AI operation response"""
    session_id: int
    result: str
    status: str
    model_used: str = "gpt-3.5-turbo"
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "result": "Generated text or answer...",
                "status": "completed",
                "model_used": "gpt-3.5-turbo"
            }
        }


class SentimentResponse(BaseModel):
    """Sentiment analysis response"""
    session_id: int
    sentiment: str
    score: float
    explanation: str
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "sentiment": "positive",
                "score": 0.95,
                "explanation": "Text expresses strong positive emotions",
                "status": "completed"
            }
        }


class HealthResponse(BaseModel):
    """AI service health response"""
    available: bool
    message: str
    model: str = "gpt-3.5-turbo"


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def ai_health():
    """
    Check if AI service is available.
    
    Returns:
        HealthResponse: AI service availability status
        
    Example:
        GET /api/ai/health
    """
    available = is_ai_available()
    return {
        "available": available,
        "message": "AI service is operational" if available else "AI service is not available",
        "model": "gpt-3.5-turbo"
    }


@router.post("/generate", response_model=AIResponse)
async def generate_text(
    request: GenerateTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate text using AI.
    
    Args:
        request: Text generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AIResponse: Generated text and session info
        
    Raises:
        HTTPException: If AI service unavailable
        
    Example:
        POST /api/ai/generate
        Headers: Authorization: Bearer <token>
        Body: {
            "prompt": "Write a poem about AI",
            "max_tokens": 500,
            "temperature": 0.7
        }
    """
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available"
        )
    
    try:
        # Create session record
        session_name = request.session_name or "Text Generation"
        db_session = create_ai_session(
            db=db,
            user_id=current_user.id,
            session_name=session_name,
            input_text=request.prompt,
            model_used="gpt-3.5-turbo"
        )
        
        # Generate text
        ai_service = get_ai_service()
        result = ai_service.generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if not result:
            result = "Failed to generate text"
            status_val = AISessionStatus.FAILED
        else:
            status_val = AISessionStatus.COMPLETED
        
        # Update session with result
        update_ai_session(
            db=db,
            session_id=db_session.id,
            output_text=result,
            status=status_val
        )
        
        logger.info(f"✅ Text generated for user {current_user.username}")
        
        return {
            "session_id": db_session.id,
            "result": result,
            "status": status_val.value,
            "model_used": "gpt-3.5-turbo"
        }
    
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate text"
        )


@router.post("/summarize", response_model=AIResponse)
async def summarize_text(
    request: SummarizeTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize text using AI.
    
    Args:
        request: Text summarization request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AIResponse: Summary and session info
        
    Example:
        POST /api/ai/summarize
        Headers: Authorization: Bearer <token>
        Body: {
            "text": "Long article text...",
            "max_length": 150
        }
    """
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available"
        )
    
    try:
        session_name = request.session_name or "Text Summarization"
        db_session = create_ai_session(
            db=db,
            user_id=current_user.id,
            session_name=session_name,
            input_text=request.text[:200],  # Store first 200 chars
            model_used="gpt-3.5-turbo"
        )
        
        ai_service = get_ai_service()
        result = ai_service.summarize_text(
            text=request.text,
            max_length=request.max_length
        )
        
        if not result:
            result = "Failed to summarize text"
            status_val = AISessionStatus.FAILED
        else:
            status_val = AISessionStatus.COMPLETED
        
        update_ai_session(
            db=db,
            session_id=db_session.id,
            output_text=result,
            status=status_val
        )
        
        logger.info(f"✅ Text summarized for user {current_user.username}")
        
        return {
            "session_id": db_session.id,
            "result": result,
            "status": status_val.value,
            "model_used": "gpt-3.5-turbo"
        }
    
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize text"
        )


@router.post("/answer", response_model=AIResponse)
async def answer_question(
    request: AnswerQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answer a question based on context using AI.
    
    Args:
        request: Question answering request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AIResponse: Answer and session info
        
    Example:
        POST /api/ai/answer
        Headers: Authorization: Bearer <token>
        Body: {
            "context": "Paris is the capital of France",
            "question": "What is the capital of France?"
        }
    """
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available"
        )
    
    try:
        session_name = request.session_name or "Question Answering"
        db_session = create_ai_session(
            db=db,
            user_id=current_user.id,
            session_name=session_name,
            input_text=request.question,
            model_used="gpt-3.5-turbo"
        )
        
        ai_service = get_ai_service()
        result = ai_service.answer_question(
            context=request.context,
            question=request.question
        )
        
        if not result:
            result = "Failed to answer question"
            status_val = AISessionStatus.FAILED
        else:
            status_val = AISessionStatus.COMPLETED
        
        update_ai_session(
            db=db,
            session_id=db_session.id,
            output_text=result,
            status=status_val
        )
        
        logger.info(f"✅ Question answered for user {current_user.username}")
        
        return {
            "session_id": db_session.id,
            "result": result,
            "status": status_val.value,
            "model_used": "gpt-3.5-turbo"
        }
    
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to answer question"
        )


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze sentiment of text using AI.
    
    Args:
        request: Sentiment analysis request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SentimentResponse: Sentiment analysis results
        
    Example:
        POST /api/ai/sentiment
        Headers: Authorization: Bearer <token>
        Body: {
            "text": "I love this product!"
        }
    """
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available"
        )
    
    try:
        session_name = request.session_name or "Sentiment Analysis"
        db_session = create_ai_session(
            db=db,
            user_id=current_user.id,
            session_name=session_name,
            input_text=request.text,
            model_used="gpt-3.5-turbo"
        )
        
        ai_service = get_ai_service()
        result = ai_service.analyze_sentiment(request.text)
        
        if not result:
            result = {
                "sentiment": "unknown",
                "score": 0.0,
                "explanation": "Failed to analyze sentiment"
            }
            status_val = AISessionStatus.FAILED
        else:
            status_val = AISessionStatus.COMPLETED
        
        update_ai_session(
            db=db,
            session_id=db_session.id,
            output_text=str(result),
            status=status_val
        )
        
        logger.info(f"✅ Sentiment analyzed for user {current_user.username}")
        
        return {
            "session_id": db_session.id,
            "sentiment": result.get("sentiment", "unknown"),
            "score": result.get("score", 0.0),
            "explanation": result.get("explanation", ""),
            "status": status_val.value
        }
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze sentiment"
        )


@router.post("/code", response_model=AIResponse)
async def generate_code(
    request: CodeGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate code using AI.
    
    Args:
        request: Code generation request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AIResponse: Generated code and session info
        
    Example:
        POST /api/ai/code
        Headers: Authorization: Bearer <token>
        Body: {
            "description": "Function to calculate factorial",
            "language": "Python"
        }
    """
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available"
        )
    
    try:
        session_name = request.session_name or "Code Generation"
        db_session = create_ai_session(
            db=db,
            user_id=current_user.id,
            session_name=session_name,
            input_text=request.description,
            model_used="gpt-3.5-turbo"
        )
        
        ai_service = get_ai_service()
        result = ai_service.code_generation(
            description=request.description,
            language=request.language
        )
        
        if not result:
            result = "Failed to generate code"
            status_val = AISessionStatus.FAILED
        else:
            status_val = AISessionStatus.COMPLETED
        
        update_ai_session(
            db=db,
            session_id=db_session.id,
            output_text=result,
            status=status_val
        )
        
        logger.info(f"✅ Code generated for user {current_user.username}")
        
        return {
            "session_id": db_session.id,
            "result": result,
            "status": status_val.value,
            "model_used": "gpt-3.5-turbo"
        }
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate code"
        )
