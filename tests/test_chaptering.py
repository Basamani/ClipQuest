from modules.chaptering import create_chapters, format_timestamp


def test_create_chapters_from_segments():
    segments = [
        {"start": 0.0, "end": 3.0, "text": "Welcome to this lesson."},
        {"start": 4.0, "end": 7.0, "text": "Today we learn Python basics."},
        {"start": 20.0, "end": 24.0, "text": "Now let us discuss functions."},
    ]

    chapters = create_chapters(segments)

    assert len(chapters) >= 1

    for chapter in chapters:
        assert "start" in chapter
        assert "end" in chapter
        assert "title" in chapter
        assert "text" in chapter
        assert chapter["end"] >= chapter["start"]


def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(65) == "00:01:05"
    assert format_timestamp(3661) == "01:01:01"