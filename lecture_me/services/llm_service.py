import asyncio
import random
from typing import Tuple

from lecture_me.models.data_models import Paragraph


class LLMService:
    """Mock LLM service for generating questions and scoring answers."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = ""):
        self.model = model
        self.api_key = api_key
        
    async def generate_question(self, paragraph: Paragraph) -> str:
        """Generate a question based on the given paragraph."""
        # Simulate API call delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Mock question generation based on paragraph content
        question_templates = [
            f"Based on the following information, explain the main concept: {paragraph.content[:100]}...",
            f"What are the key points mentioned in this text: {paragraph.content[:100]}...",
            f"Summarize and explain the following: {paragraph.content[:100]}...",
            f"What is the significance of the ideas presented in: {paragraph.content[:100]}...",
            f"Analyze and discuss the following content: {paragraph.content[:100]}...",
        ]
        
        return random.choice(question_templates)
    
    async def score_answer(self, question: str, user_answer: str, reference_paragraph: Paragraph) -> Tuple[int, str]:
        """Score the user's answer against the reference paragraph."""
        # Simulate API call delay
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # Mock scoring logic
        user_answer_lower = user_answer.lower()
        reference_lower = reference_paragraph.content.lower()
        
        # Simple keyword matching for mock scoring
        reference_words = set(reference_lower.split())
        user_words = set(user_answer_lower.split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        reference_words -= common_words
        user_words -= common_words
        
        if not reference_words:
            score = 50  # Default score if no meaningful words in reference
        else:
            # Calculate overlap
            overlap = len(user_words.intersection(reference_words))
            score = min(100, max(0, int((overlap / len(reference_words)) * 100)))
        
        # Add some randomness to make it more realistic
        score += random.randint(-10, 10)
        score = max(0, min(100, score))
        
        # Generate feedback based on score
        if score >= 80:
            feedback = "Excellent answer! You demonstrated a strong understanding of the topic."
        elif score >= 60:
            feedback = "Good answer! You covered most of the key points."
        elif score >= 40:
            feedback = "Fair answer. You touched on some important aspects but could elaborate more."
        else:
            feedback = "Your answer could be improved. Try to include more specific details from the topic."
        
        return score, feedback
