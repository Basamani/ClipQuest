from modules.study_tools import (
    generate_summary,
    generate_notes,
    generate_flashcards,
    generate_quiz,
)


SAMPLE_TEXT = """
Python is a programming language.
Functions allow code to be reused.
Variables store values.
"""


def test_generate_summary():
    result = generate_summary(SAMPLE_TEXT)
    assert result is not None


def test_generate_notes():
    result = generate_notes(SAMPLE_TEXT)
    assert result is not None


def test_generate_flashcards():
    result = generate_flashcards(SAMPLE_TEXT)
    assert result is not None


def test_generate_quiz():
    result = generate_quiz(SAMPLE_TEXT)
    assert result is not None