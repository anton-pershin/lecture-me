import json
from typing import Tuple

from rally.interaction import LlmMessage, request_based_on_message_history
from rally.llm import Llm

from lecture_me.models.data_models import Paragraph


class LLMService:
    def __init__(
        self, llm: Llm, question_generation_prompt: str, answer_scoring_prompt: str
    ):
        self.llm = llm
        self.question_generation_prompt = question_generation_prompt
        self.answer_scoring_prompt = answer_scoring_prompt

    async def generate_question(self, paragraph: Paragraph) -> str:
        messages: list[LlmMessage] = [
            {
                "role": "user",
                "content": self.question_generation_prompt.format(
                    paragraph=paragraph.content
                ),
            }
        ]

        assistant_message = request_based_on_message_history(
            llm_server_url=self.llm.url,
            message_history=messages,
            authorization=self.llm.authorization,
            model=self.llm.model,
        )

        return assistant_message["content"]

    async def score_answer(
        self, question: str, user_answer: str, reference_paragraph: Paragraph
    ) -> Tuple[int, str]:
        messages: list[LlmMessage] = [
            {
                "role": "user",
                "content": self.answer_scoring_prompt.format(
                    paragraph=reference_paragraph.content,
                    question=question,
                    user_answer=user_answer,
                ),
            }
        ]

        assistant_message = request_based_on_message_history(
            llm_server_url=self.llm.url,
            message_history=messages,
            authorization=self.llm.authorization,
            model=self.llm.model,
        )

        resp_dict = json.loads(assistant_message["content"])
        score = int(resp_dict["score"])
        feedback = resp_dict["explanation"]
        feedback += "\n\n"
        feedback += (
            f"Original paragraph from note {reference_paragraph.file_path.name}:\n"
            f"{reference_paragraph.content}"
        )

        return score, feedback
