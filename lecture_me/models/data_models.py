from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class Subject:
    name: str
    path: Path
    topics: List['Topic']


@dataclass
class Topic:
    name: str
    subject: str
    path: Path
    markdown_files: List[Path]


@dataclass
class Paragraph:
    content: str
    file_path: Path
    paragraph_index: int


@dataclass
class Question:
    text: str
    source_paragraph: Paragraph
    topic: str
    subject: str


@dataclass
class UserSession:
    user_id: int
    current_question: Optional[Question] = None
    selected_topic: Optional[str] = None
    selected_subject: Optional[str] = None
    score: int = 0
    questions_answered: int = 0
