from pathlib import Path
from urllib.parse import urlparse
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "data" / "uploads"

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".webm",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"
}

MAX_UPLOAD_SIZE_MB = 500


def save_uploaded_file(uploaded_file):
    """Validate and save an uploaded video or audio file."""
    if uploaded_file is None:
        raise ValueError("Please choose a video or audio file.")

    original_name = getattr(uploaded_file, "name", "")
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format. Please choose a supported video or audio file."
        )

    file_size = getattr(uploaded_file, "size", None)
    max_size = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if file_size is not None and file_size > max_size:
        raise ValueError(
            f"File is too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB."
        )

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    destination = UPLOAD_FOLDER / f"{uuid.uuid4().hex}{extension}"

    try:
        with destination.open("wb") as output_file:
            while True:
                chunk = uploaded_file.read(1024 * 1024)
                if not chunk:
                    break
                output_file.write(chunk)

        if destination.stat().st_size == 0:
            destination.unlink(missing_ok=True)
            raise ValueError("The selected file is empty.")

        if destination.stat().st_size > max_size:
            destination.unlink(missing_ok=True)
            raise ValueError(
                f"File is too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB} MB."
            )

        return destination

    except Exception:
        destination.unlink(missing_ok=True)
        raise


def validate_media_url(url):
    """
    Check basic URL structure only.
    This function does not download or verify the media.
    """
    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url:
        return False

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
            and not any(character.isspace() for character in url)
        )
    except ValueError:
        return False