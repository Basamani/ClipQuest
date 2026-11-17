import re
import math


def create_chapters(segments, max_gap=8.0, max_duration=90.0):
    """
    Group timestamped transcript segments into chapters.
    Start a new chapter after a long pause or when
    the target chapter duration is reached.
    """
    if not segments:
        return []

    if max_gap < 0 or max_duration <= 0:
        raise ValueError(
            "max_gap must be non-negative and max_duration must be positive."
        )

    valid_segments = []

    for segment in segments:
        if not isinstance(segment, dict):
            continue

        try:
            start = float(segment["start"])
            end = float(segment["end"])
            text = str(segment.get("text", "")).strip()
        except (KeyError, TypeError, ValueError):
            continue

        if (
            not math.isfinite(start)
            or not math.isfinite(end)
            or start < 0
            or end < start
            or not text
        ):
            continue

        valid_segments.append({
            "start": start,
            "end": end,
            "text": text
        })

    if not valid_segments:
        return []

    # Ensure segments are processed in timestamp order.
    valid_segments.sort(key=lambda item: item["start"])

    chapters = []
    current_segments = [valid_segments[0]]
    chapter_start = valid_segments[0]["start"]
    previous_end = valid_segments[0]["end"]

    for segment in valid_segments[1:]:
        gap = segment["start"] - previous_end
        duration = segment["end"] - chapter_start

        if gap > max_gap or duration >= max_duration:
            chapters.append(
                _make_chapter(current_segments, len(chapters) + 1)
            )

            current_segments = [segment]
            chapter_start = segment["start"]
        else:
            current_segments.append(segment)

        previous_end = max(previous_end, segment["end"])

    if current_segments:
        chapters.append(
            _make_chapter(current_segments, len(chapters) + 1)
        )

    return chapters


def _make_chapter(segments, number):
    """Create a chapter title and combine its transcript text."""
    text = " ".join(
        segment["text"] for segment in segments
    ).strip()

    words = re.findall(r"\b[\w'-]+\b", text)
    title = " ".join(words[:7]) or f"Chapter {number}"

    if len(words) > 7:
        title += "..."

    return {
        "title": title,
        "start": segments[0]["start"],
        "end": max(segment["end"] for segment in segments),
        "text": text
    }


def format_timestamp(seconds):
    """Convert seconds into HH:MM:SS format."""
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        seconds = 0

    if not math.isfinite(seconds):
        seconds = 0

    seconds = max(0, int(seconds))

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"