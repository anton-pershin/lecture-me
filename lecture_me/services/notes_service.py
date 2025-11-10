import random
import re
from pathlib import Path
from typing import List, Optional, Tuple

from lecture_me.models.data_models import Paragraph, Subject, Topic


class NotesService:
    def __init__(self, notes_directory: str):
        self.notes_directory = Path(notes_directory)

    def get_subjects(self) -> List[Subject]:
        """Get all subjects from the notes directory."""
        subjects: list[Subject] = []

        if not self.notes_directory.exists():
            return subjects

        for subject_dir in self.notes_directory.iterdir():
            if subject_dir.is_dir() and not subject_dir.name.startswith("."):
                topics = self._get_topics_for_subject(subject_dir)
                if topics:  # Only include subjects that have topics with markdown files
                    subject = Subject(
                        name=subject_dir.name, path=subject_dir, topics=topics
                    )
                    subjects.append(subject)

        return subjects

    def _get_topics_for_subject(self, subject_dir: Path) -> List[Topic]:
        """Get all topics for a given subject."""
        topics = []

        for topic_dir in subject_dir.iterdir():
            if topic_dir.is_dir() and not topic_dir.name.startswith("."):
                markdown_files = self._get_markdown_files(topic_dir)
                if markdown_files:  # Only include topics that have markdown files
                    topic = Topic(
                        name=topic_dir.name,
                        subject=subject_dir.name,
                        path=topic_dir,
                        markdown_files=markdown_files,
                    )
                    topics.append(topic)

        return topics

    def _get_markdown_files(self, topic_dir: Path) -> List[Path]:
        """Get all markdown files in a topic directory."""
        markdown_files = []

        for file_path in topic_dir.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower() in [".md", ".markdown"]
                and file_path.name != "state.md"
            ):
                markdown_files.append(file_path)

        return markdown_files

    def get_topics_for_subject(self, subject_name: str) -> List[Topic]:
        """Get all topics for a specific subject."""
        subjects = self.get_subjects()
        for subject in subjects:
            if subject.name == subject_name:
                return subject.topics
        return []

    def get_random_paragraph(
        self, subject_name: str, topic_name: str
    ) -> Optional[Paragraph]:
        """Get a random paragraph from a random markdown file in the specified topic."""
        topics = self.get_topics_for_subject(subject_name)

        # Find the specified topic
        target_topic = None
        for topic in topics:
            if topic.name == topic_name:
                target_topic = topic
                break

        if not target_topic or not target_topic.markdown_files:
            return None

        # Select a random markdown file
        random_file = random.choice(target_topic.markdown_files)

        # Extract paragraphs from the file
        paragraphs = self._extract_paragraphs(random_file)

        if not paragraphs:
            return None

        # Select a random paragraph
        random_paragraph_content, paragraph_index = random.choice(paragraphs)

        return Paragraph(
            content=random_paragraph_content,
            file_path=random_file,
            paragraph_index=paragraph_index,
        )

    def _extract_paragraphs(self, file_path: Path) -> List[Tuple[str, int]]:
        """Extract paragraphs from a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

        # Split content into paragraphs (separated by double newlines)
        paragraphs = []
        raw_paragraphs = content.split("\n\n")

        for i, paragraph in enumerate(raw_paragraphs):
            # Clean up the paragraph
            cleaned = paragraph.strip()

            # Skip empty paragraphs, headers, and very short paragraphs
            if (
                len(cleaned) > 50
                and not cleaned.startswith("#")
                and not cleaned.startswith("```")
                and not cleaned.startswith("---")
            ):

                # Remove markdown formatting for cleaner text
                cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)  # Bold
                cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)  # Italic
                cleaned = re.sub(r"`(.*?)`", r"\1", cleaned)  # Inline code
                cleaned = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cleaned)  # Links

                paragraphs.append((cleaned, i))

        return paragraphs
