from hydra.utils import instantiate
from omegaconf import DictConfig

import hydra
from lecture_me.bot.telegram_bot import TelegramBot
from lecture_me.services.llm_service import LLMService
from lecture_me.services.notes_service import NotesService
from lecture_me.utils.common import get_config_path

CONFIG_NAME = "config_main"


def main(cfg: DictConfig) -> None:
    """Main entry point for the telegram bot."""
    print("Starting Telegram Bot for Self-Education...")
    print(f"Notes directory: {cfg.notes_directory}")

    # Initialize services
    notes_service = NotesService(cfg.notes_directory)
    llm = instantiate(cfg.llm)
    llm_service = LLMService(
        llm=llm,
        question_generation_prompt=cfg.question_generation_prompt,
        answer_scoring_prompt=cfg.answer_scoring_prompt,
    )

    # Initialize and run the bot (this will handle its own event loop)
    bot = TelegramBot(cfg.telegram_bot_token, notes_service, llm_service)
    bot.run_sync()


if __name__ == "__main__":
    hydra.main(
        config_path=str(get_config_path()),
        config_name=CONFIG_NAME,
        version_base="1.3",
    )(main)()
