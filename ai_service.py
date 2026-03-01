"""
AI Service Module
=================

This module provides AI/LLM integration capabilities:
- Text generation and completion
- Natural language processing
- Sentiment analysis
- Text summarization
- Question answering

Uses OpenAI API or can be extended with other LLM providers.

Author: Manus AI
Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# OpenAI API Key - set via environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2048
TEMPERATURE = 0.7


# ============================================================================
# AI SERVICE CLASS
# ============================================================================

class AIService:
    """
    Main AI service class for LLM operations.
    
    This class handles all interactions with AI models.
    Can be extended to support multiple providers (OpenAI, Hugging Face, etc.)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize AI Service.
        
        Args:
            api_key: API key for the LLM provider
            model: Model name to use
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model
        
        # Initialize OpenAI client if available
        if self.api_key:
            try:
                import openai
                openai.api_key = self.api_key
                self.client = openai
                logger.info(f"✅ AI Service initialized with model: {model}")
            except ImportError:
                logger.warning("⚠️ OpenAI library not installed. Install with: pip install openai")
                self.client = None
        else:
            logger.warning("⚠️ No API key provided. AI features will be limited.")
            self.client = None
    
    
    def generate_text(self, prompt: str, max_tokens: int = MAX_TOKENS, 
                     temperature: float = TEMPERATURE) -> Optional[str]:
        """
        Generate text using the AI model.
        
        Args:
            prompt: Input prompt for text generation
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0-1.0, higher = more creative)
            
        Returns:
            str or None: Generated text if successful, None otherwise
            
        Example:
            ai = AIService()
            response = ai.generate_text("Write a poem about AI")
        """
        if not self.client:
            logger.error("AI client not initialized")
            return None
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return None
    
    
    def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """
        Summarize a given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            str or None: Summary if successful
            
        Example:
            ai = AIService()
            summary = ai.summarize_text(long_article)
        """
        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
        return self.generate_text(prompt, max_tokens=max_length)
    
    
    def answer_question(self, context: str, question: str) -> Optional[str]:
        """
        Answer a question based on provided context.
        
        Args:
            context: Background information/context
            question: Question to answer
            
        Returns:
            str or None: Answer if successful
            
        Example:
            ai = AIService()
            answer = ai.answer_question(
                context="Paris is the capital of France",
                question="What is the capital of France?"
            )
        """
        prompt = f"""Based on the following context, answer the question.

Context: {context}

Question: {question}

Answer:"""
        
        return self.generate_text(prompt)
    
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze the sentiment of a given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict or None: Sentiment analysis results
            
        Example:
            ai = AIService()
            sentiment = ai.analyze_sentiment("I love this product!")
            # Returns: {"sentiment": "positive", "score": 0.95}
        """
        prompt = f"""Analyze the sentiment of the following text and respond with JSON format:
{{"sentiment": "positive/negative/neutral", "score": 0.0-1.0, "explanation": "brief explanation"}}

Text: {text}

Response:"""
        
        try:
            response = self.generate_text(prompt)
            if response:
                import json
                # Try to parse JSON from response
                # Response might have markdown code blocks, so we extract JSON
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response
                
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
        
        return None
    
    
    def translate_text(self, text: str, target_language: str) -> Optional[str]:
        """
        Translate text to a target language.
        
        Args:
            text: Text to translate
            target_language: Target language (e.g., "Spanish", "French")
            
        Returns:
            str or None: Translated text if successful
            
        Example:
            ai = AIService()
            spanish = ai.translate_text("Hello, how are you?", "Spanish")
        """
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        return self.generate_text(prompt)
    
    
    def code_generation(self, description: str, language: str = "Python") -> Optional[str]:
        """
        Generate code based on a description.
        
        Args:
            description: Description of what code to generate
            language: Programming language
            
        Returns:
            str or None: Generated code if successful
            
        Example:
            ai = AIService()
            code = ai.code_generation(
                "Function to calculate factorial",
                "Python"
            )
        """
        prompt = f"""Generate {language} code for the following:

{description}

Provide clean, well-commented code:"""
        
        return self.generate_text(prompt, max_tokens=2048)


# ============================================================================
# MOCK AI SERVICE (for testing without API key)
# ============================================================================

class MockAIService(AIService):
    """
    Mock AI Service for testing without an actual API key.
    
    Returns predefined responses for testing purposes.
    """
    
    def generate_text(self, prompt: str, max_tokens: int = MAX_TOKENS, 
                     temperature: float = TEMPERATURE) -> Optional[str]:
        """Return mock response"""
        return f"Mock response to: {prompt[:50]}..."
    
    def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """Return mock summary"""
        return f"Mock summary of text (length: {len(text)} chars)"
    
    def answer_question(self, context: str, question: str) -> Optional[str]:
        """Return mock answer"""
        return f"Mock answer to: {question}"
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Return mock sentiment"""
        return {
            "sentiment": "positive",
            "score": 0.85,
            "explanation": "Mock analysis"
        }
    
    def translate_text(self, text: str, target_language: str) -> Optional[str]:
        """Return mock translation"""
        return f"Mock translation to {target_language}: {text}"
    
    def code_generation(self, description: str, language: str = "Python") -> Optional[str]:
        """Return mock code"""
        return f"# Mock {language} code\n# {description}\nprint('Hello, World!')"


# ============================================================================
# GLOBAL AI SERVICE INSTANCE
# ============================================================================

# Initialize AI service
# If no API key, use mock service
if OPENAI_API_KEY:
    ai_service = AIService(api_key=OPENAI_API_KEY)
else:
    logger.warning("No OpenAI API key found. Using mock AI service.")
    ai_service = MockAIService()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_ai_service() -> AIService:
    """
    Get the global AI service instance.
    
    Returns:
        AIService: The AI service instance
        
    Example:
        ai = get_ai_service()
        response = ai.generate_text("Hello, AI!")
    """
    return ai_service


def is_ai_available() -> bool:
    """
    Check if AI service is available and functional.
    
    Returns:
        bool: True if AI service is available
    """
    return ai_service.client is not None
