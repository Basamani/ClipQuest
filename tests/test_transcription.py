import pytest

from modules.transcription import transcribe_media


def test_missing_media_file_raises_error():
    with pytest.raises(FileNotFoundError):
        transcribe_media("data/uploads/file_that_does_not_exist.mp4")


def test_empty_media_file_raises_error(tmp_path):
    empty_file = tmp_path / "empty.mp4"
    empty_file.write_bytes(b"")

    with pytest.raises(ValueError, match="empty"):
        transcribe_media(str(empty_file))