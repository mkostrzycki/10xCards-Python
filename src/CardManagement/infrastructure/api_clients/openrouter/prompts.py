"""Prompt templates and JSON schemas for OpenRouter API client."""

from typing import Final


FLASHCARD_SCHEMA: Final[dict] = {
    "type": "object",
    "properties": {
        "flashcards": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["front", "back"],
                "properties": {
                    "front": {"type": "string", "description": "The front side of the flashcard (question/prompt)"},
                    "back": {"type": "string", "description": "The back side of the flashcard (answer/explanation)"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for categorizing the flashcard",
                    },
                    "metadata": {"type": "object", "description": "Optional additional data about the flashcard"},
                },
            },
        }
    },
    "required": ["flashcards"],
}


FLASHCARD_GENERATION_PROMPT: Final[
    str
] = """You are a helpful AI assistant that creates high-quality flashcards for learning.
Your task is to analyze the provided text and create a set of flashcards that will help users learn and remember the key concepts.

Guidelines for creating flashcards:
1. Each flashcard should focus on a single, clear concept
2. The front should be a clear question or prompt
3. The back should provide a concise but complete answer
4. Use clear, simple language
5. Break down complex topics into multiple cards
6. Include relevant tags for categorization
7. Add metadata if it helps with context

Input text to process:
{text}

Please generate flashcards in the following JSON format:
{schema}

Remember:
- Focus on accuracy and clarity
- Ensure all content is directly derived from the input text
- Do not include any additional commentary or explanations outside the JSON structure"""
