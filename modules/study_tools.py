import re


STOP_WORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of",
    "in", "on", "for", "it", "this", "that", "are",
    "was", "with", "as", "by", "be", "from", "were",
    "has", "have", "had", "he", "she", "they", "them",
    "we", "you", "your", "their", "our", "but", "not",
    "can", "will", "would", "could", "about", "into"
}


def _clean_text(text):
    """Convert input into clean text safely."""
    if not isinstance(text, str):
        return ""
    return text.strip()


def _sentences(text):
    """Split transcript text into simple sentences."""
    text = _clean_text(text)

    if not text:
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def _keywords(text):
    """Extract useful words for basic study tools."""
    words = re.findall(r"\b\w+\b", text.lower())

    return [
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    ]


def generate_summary(text, max_sentences=5):
    """Create a simple extractive summary from transcript sentences."""
    sentences = _sentences(text)

    if not sentences:
        return "No transcript text available."

    try:
        max_sentences = max(1, int(max_sentences))
    except (TypeError, ValueError):
        max_sentences = 5

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    frequencies = {}

    for word in _keywords(text):
        frequencies[word] = frequencies.get(word, 0) + 1

    scored = []

    for index, sentence in enumerate(sentences):
        words = _keywords(sentence)
        score = sum(frequencies.get(word, 0) for word in words)

        # Prefer informative sentences without favoring long sentences too much.
        if words:
            score /= len(words) ** 0.5

        scored.append((index, score, sentence))

    chosen = sorted(
        sorted(scored, key=lambda item: item[1], reverse=True)[:max_sentences],
        key=lambda item: item[0]
    )

    return " ".join(item[2] for item in chosen)


def generate_notes(text):
    """Create simple bullet-point notes from transcript sentences."""
    sentences = _sentences(text)

    if not sentences:
        return ["No transcript text available."]

    return [f"- {sentence}" for sentence in sentences]


def generate_flashcards(text, max_cards=10):
    """Create basic revision flashcards from transcript sentences."""
    sentences = _sentences(text)
    cards = []

    try:
        max_cards = max(1, int(max_cards))
    except (TypeError, ValueError):
        max_cards = 10

    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", sentence)

        if len(words) < 5:
            continue

        keywords = [
            word for word in words
            if len(word) > 4 and word.lower() not in STOP_WORDS
        ]

        if not keywords:
            continue

        answer = max(keywords, key=len)

        question_text = re.sub(
            rf"\b{re.escape(answer)}\b",
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        cards.append({
            "question": question_text,
            "answer": answer
        })

        if len(cards) >= max_cards:
            break

    return cards


def generate_quiz(text, max_questions=5):
    """Create fill-in-the-blank questions from transcript sentences."""
    sentences = _sentences(text)
    questions = []

    try:
        max_questions = max(1, int(max_questions))
    except (TypeError, ValueError):
        max_questions = 5

    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", sentence)

        if len(words) < 5:
            continue

        keywords = [
            word for word in words
            if len(word) > 4 and word.lower() not in STOP_WORDS
        ]

        if not keywords:
            continue

        answer = max(keywords, key=len)

        question_text = re.sub(
            rf"\b{re.escape(answer)}\b",
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        questions.append({
            "question": question_text,
            "answer": answer
        })

        if len(questions) >= max_questions:
            break

    return questions