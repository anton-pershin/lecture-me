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
        """Score the user's answer against the reference paragraph using LLM."""
        # Simulate API call delay
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # Mock LLM prompt for scoring
        prompt = f"""
        You are an educational assessment AI. Score the student's answer on a scale of 0-3 where:
        - 0: Completely incorrect or irrelevant
        - 1: Partially correct but missing key concepts
        - 2: Mostly correct with minor gaps
        - 3: Excellent, comprehensive answer
        
        Question: {question}
        
        Reference material: {reference_paragraph.content}
        
        Student's answer: {user_answer}
        
        Provide a score (0-3) and brief feedback explaining the score.
        """
        
        # Mock LLM response - in real implementation, this would call the actual LLM API
        score = await self._mock_llm_scoring(user_answer, reference_paragraph.content)
        feedback = self._generate_feedback(score, user_answer, reference_paragraph.content)
        
        return score, feedback
    
    async def _mock_llm_scoring(self, user_answer: str, reference_content: str) -> int:
        """Mock LLM scoring logic that simulates intelligent assessment."""
        user_answer_lower = user_answer.lower()
        reference_lower = reference_content.lower()
        
        # Extract key terms and concepts
        reference_words = set(reference_lower.split())
        user_words = set(user_answer_lower.split())
        
        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'it', 'they', 'them', 'their', 'there', 'where', 'when', 'how', 'why'
        }
        
        reference_words -= common_words
        user_words -= common_words
        
        if not reference_words:
            return 1  # Default score if no meaningful words in reference
        
        # Calculate semantic overlap
        overlap = len(user_words.intersection(reference_words))
        overlap_ratio = overlap / len(reference_words) if reference_words else 0
        
        # Consider answer length (too short might be incomplete)
        answer_length_factor = min(1.0, len(user_answer.split()) / 20)  # Normalize around 20 words
        
        # Mock "semantic understanding" - look for key patterns
        understanding_bonus = 0
        if any(word in user_answer_lower for word in ['because', 'therefore', 'however', 'although', 'since']):
            understanding_bonus += 0.1  # Bonus for explanatory language
        
        if any(word in user_answer_lower for word in ['example', 'instance', 'such as', 'like']):
            understanding_bonus += 0.1  # Bonus for examples
        
        # Calculate final score
        base_score = overlap_ratio + understanding_bonus + (answer_length_factor * 0.2)
        
        # Map to 0-3 scale with some randomness for realism
        if base_score >= 0.8:
            score = 3
        elif base_score >= 0.6:
            score = 2
        elif base_score >= 0.3:
            score = 1
        else:
            score = 0
        
        # Add slight randomness to make it more realistic
        if random.random() < 0.2:  # 20% chance to adjust score by ±1
            adjustment = random.choice([-1, 1])
            score = max(0, min(3, score + adjustment))
        
        return score
    
    def _generate_feedback(self, score: int, user_answer: str, reference_content: str) -> str:
        """Generate feedback based on the score."""
        feedback_templates = {
            3: [
                "Excellent answer! You demonstrated a comprehensive understanding of the topic.",
                "Outstanding! Your answer covers all the key concepts thoroughly.",
                "Perfect! You've shown deep understanding and provided a complete response."
            ],
            2: [
                "Good answer! You covered most of the important points with solid understanding.",
                "Well done! Your response shows good grasp of the material with minor gaps.",
                "Nice work! You've captured the main ideas effectively."
            ],
            1: [
                "Fair answer. You touched on some relevant points but could expand on key concepts.",
                "Partially correct. Try to include more specific details and explanations.",
                "You're on the right track, but your answer needs more depth and detail."
            ],
            0: [
                "Your answer needs significant improvement. Please review the material more carefully.",
                "This answer doesn't address the question adequately. Consider the key concepts more thoroughly.",
                "Please try again with more focus on the specific topic and its main ideas."
            ]
        }
        
        base_feedback = random.choice(feedback_templates[score])
        
        # Add specific suggestions based on the content
        if score < 2 and len(user_answer.split()) < 10:
            base_feedback += " Try to provide more detailed explanations."
        
        if score < 3:
            # Extract a key concept from reference that might be missing
            reference_words = reference_content.split()
            if len(reference_words) > 10:
                key_phrase = ' '.join(reference_words[len(reference_words)//3:len(reference_words)//3+3])
                base_feedback += f" Consider discussing concepts like '{key_phrase}'."
        
        return base_feedback
