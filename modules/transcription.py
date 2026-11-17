from pathlib import Path
from faster_whisper import WhisperModel


_model = None


def get_model():
    """Load the speech transcription model only when needed."""
    global _model

    if _model is None:
        _model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

    return _model


def transcribe_media(file_path, language=None):
    """
    Transcribe speech from an audio/video file.
    Detect the spoken language when language is None.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Media file not found: {path}"
        )

    if path.stat().st_size == 0:
        raise ValueError("The selected media file is empty.")

    if language is not None:
        language = language.strip().lower()
        if not language:
            language = None

    model = get_model()

    try:
        segments, info = model.transcribe(
            str(path),
            language=language,
            beam_size=1,
            vad_filter=True
        )

        results = []

        for segment in segments:
            text = segment.text.strip()

            if not text:
                continue

            results.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text
            })

        transcript = " ".join(
            item["text"] for item in results
        )

        return {
            "language": info.language,
            "language_probability": round(
                info.language_probability, 3
            ),
            "segments": results,
            "text": transcript
        }

    except Exception as error:
        raise RuntimeError(
            f"Transcription failed: {error}"
        ) from error