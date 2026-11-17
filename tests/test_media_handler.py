from modules.media_handler import validate_media_url


def test_valid_http_url():
    assert validate_media_url("https://example.com/video.mp4")


def test_valid_youtube_url():
    assert validate_media_url("https://www.youtube.com/watch?v=example")


def test_invalid_urls():
    assert not validate_media_url("")
    assert not validate_media_url("not-a-url")
    assert not validate_media_url("ftp://example.com/video.mp4")
    assert not validate_media_url(None)