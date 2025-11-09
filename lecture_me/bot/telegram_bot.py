import logging
import random
from typing import Dict, Optional

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from lecture_me.models.data_models import UserSession, Question
from lecture_me.services.notes_service import NotesService
from lecture_me.services.llm_service import LLMService

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, notes_service: NotesService, llm_service: LLMService):
        self.token = token
        self.notes_service = notes_service
        self.llm_service = llm_service
        self.user_sessions: Dict[int, UserSession] = {}
        
    def get_user_session(self, user_id: int) -> UserSession:
        """Get or create a user session."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id=user_id)
        return self.user_sessions[user_id]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Reset session
        session.current_question = None
        session.selected_topic = None
        session.selected_subject = None
        
        await update.message.reply_text(
            "Welcome to the Self-Education Bot! 🎓\n\n"
            "I'll help you learn by asking questions based on your notes.\n"
            "Use /study to start a study session or /stats to see your progress."
        )
    
    async def study_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /study command."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Get available subjects
        subjects = self.notes_service.get_subjects()
        
        if not subjects:
            await update.message.reply_text(
                "No study materials found! Please make sure your notes directory contains "
                "subjects with topics and markdown files."
            )
            return
        
        # Create keyboard with subject options
        keyboard = [[subject.name] for subject in subjects]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        session.selected_subject = None
        session.selected_topic = None
        
        await update.message.reply_text(
            "Choose a subject to study:",
            reply_markup=reply_markup
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /stats command."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if session.questions_answered == 0:
            await update.message.reply_text("You haven't answered any questions yet! Use /study to start learning.")
        else:
            average_score = session.score / session.questions_answered
            await update.message.reply_text(
                f"📊 Your Study Statistics:\n"
                f"Questions answered: {session.questions_answered}\n"
                f"Total score: {session.score}\n"
                f"Average score: {average_score:.1f}/3"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        message_text = update.message.text
        
        # If user is answering a question
        if session.current_question:
            await self.handle_answer(update, context, message_text)
            return
        
        # If no subject is selected, treat message as subject selection
        if not session.selected_subject:
            await self.handle_subject_selection(update, context, message_text)
            return
        
        # If subject is selected but no topic, treat message as topic selection
        if session.selected_subject and not session.selected_topic:
            await self.handle_topic_selection(update, context, message_text)
            return
    
    async def handle_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subject_name: str) -> None:
        """Handle subject selection."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Verify subject exists
        subjects = self.notes_service.get_subjects()
        subject_names = [s.name for s in subjects]
        
        if subject_name not in subject_names:
            await update.message.reply_text(
                f"Subject '{subject_name}' not found. Please choose from: {', '.join(subject_names)}"
            )
            return
        
        session.selected_subject = subject_name
        
        # Get topics for this subject
        topics = self.notes_service.get_topics_for_subject(subject_name)
        
        if not topics:
            await update.message.reply_text(
                f"No topics found for subject '{subject_name}'. Please check your notes directory."
            )
            return
        
        # Create keyboard with topic options
        keyboard = [[topic.name] for topic in topics]
        keyboard.append(["🎲 Random Topic"])  # Add random option
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            f"Great! You selected '{subject_name}'. Now choose a topic:",
            reply_markup=reply_markup
        )
    
    async def handle_topic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic_name: str) -> None:
        """Handle topic selection and generate a question."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Handle random topic selection
        if topic_name == "🎲 Random Topic":
            topics = self.notes_service.get_topics_for_subject(session.selected_subject)
            if topics:
                topic_name = random.choice(topics).name
        
        # Verify topic exists
        topics = self.notes_service.get_topics_for_subject(session.selected_subject)
        topic_names = [t.name for t in topics]
        
        if topic_name not in topic_names:
            await update.message.reply_text(
                f"Topic '{topic_name}' not found. Please choose from: {', '.join(topic_names)}"
            )
            return
        
        session.selected_topic = topic_name
        
        # Generate a question
        await self.generate_question(update, context)
    
    async def generate_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Generate and send a question to the user."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Get a random paragraph from the selected topic
        paragraph = self.notes_service.get_random_paragraph(
            session.selected_subject, 
            session.selected_topic
        )
        
        if not paragraph:
            await update.message.reply_text(
                f"No content found for topic '{session.selected_topic}' in subject '{session.selected_subject}'. "
                "Please check your notes directory."
            )
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate question using LLM
        try:
            question_text = await self.llm_service.generate_question(paragraph)
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error while generating a question. Please try again."
            )
            return
        
        # Create question object
        question = Question(
            text=question_text,
            source_paragraph=paragraph,
            topic=session.selected_topic,
            subject=session.selected_subject
        )
        
        session.current_question = question
        
        # Send question to user
        await update.message.reply_text(
            f"📚 Subject: {session.selected_subject}\n"
            f"📖 Topic: {session.selected_topic}\n\n"
            f"❓ Question:\n{question_text}\n\n"
            "Please provide your answer:",
            reply_markup=ReplyKeyboardRemove()
        )
    
    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_answer: str) -> None:
        """Handle user's answer to a question."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if not session.current_question:
            await update.message.reply_text("No active question. Use /study to start a new session.")
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Score the answer using LLM
        try:
            score, feedback = await self.llm_service.score_answer(
                session.current_question.text,
                user_answer,
                session.current_question.source_paragraph
            )
        except Exception as e:
            logger.error(f"Error scoring answer: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error while scoring your answer. Please try again."
            )
            return
        
        # Update session statistics
        session.score += score
        session.questions_answered += 1
        
        # Determine score emoji
        score_emoji = {0: "❌", 1: "🔶", 2: "✅", 3: "🌟"}
        
        # Send feedback
        await update.message.reply_text(
            f"{score_emoji.get(score, '❓')} Score: {score}/3\n\n"
            f"📝 Feedback:\n{feedback}\n\n"
            f"📊 Your stats: {session.questions_answered} questions, "
            f"average score: {session.score/session.questions_answered:.1f}/3"
        )
        
        # Clear current question
        session.current_question = None
        
        # Offer options for next action
        keyboard = [
            ["📚 Another Question", "🔄 Change Topic"],
            ["📊 View Stats", "🏠 Main Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=reply_markup
        )
    
    async def handle_next_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle user's choice for next action."""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        action = update.message.text
        
        if action == "📚 Another Question":
            if session.selected_subject and session.selected_topic:
                await self.generate_question(update, context)
            else:
                await self.study_command(update, context)
        elif action == "🔄 Change Topic":
            if session.selected_subject:
                # Reset topic selection
                session.selected_topic = None
                topics = self.notes_service.get_topics_for_subject(session.selected_subject)
                keyboard = [[topic.name] for topic in topics]
                keyboard.append(["🎲 Random Topic"])
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text(
                    f"Choose a new topic from '{session.selected_subject}':",
                    reply_markup=reply_markup
                )
            else:
                await self.study_command(update, context)
        elif action == "📊 View Stats":
            await self.stats_command(update, context)
        elif action == "🏠 Main Menu":
            await self.start_command(update, context)
        else:
            # Handle as regular message
            await self.handle_message(update, context)
    
    async def run(self) -> None:
        """Run the telegram bot."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("study", self.study_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Add message handler that routes to appropriate method
        async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            message_text = update.message.text
            user_id = update.effective_user.id
            session = self.get_user_session(user_id)
            
            # Check if it's a next action button
            if message_text in ["📚 Another Question", "🔄 Change Topic", "📊 View Stats", "🏠 Main Menu"]:
                await self.handle_next_action(update, context)
            else:
                await self.handle_message(update, context)
        
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
        
        # Start the bot
        logger.info("Starting telegram bot...")
        
        # Run the bot with polling
        await application.run_polling(drop_pending_updates=True)
