import pytest

import modules.database as database


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_clipquest.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)
    database.initialize_database()
    return database


def test_database_operations(temporary_database):
    db = temporary_database

    media_id = db.save_media(
        name="Test Video",
        file_path="data/uploads/test.mp4",
        language="en",
        transcript="This is a test transcript.",
        chapters=[
            {
                "start": 0.0,
                "end": 10.0,
                "title": "Introduction",
                "text": "This is a test transcript."
            }
        ],
    )

    media = db.get_media_by_id(media_id)
    assert media["name"] == "Test Video"

    assert db.update_media_name(media_id, "Updated Test Video")
    assert db.get_media_by_id(media_id)["name"] == "Updated Test Video"

    assert any(item["id"] == media_id for item in db.get_all_media())

    assert db.delete_media(media_id)
    assert db.get_media_by_id(media_id) is None


def test_empty_media_name_is_rejected(temporary_database):
    with pytest.raises(ValueError):
        temporary_database.save_media(
            name="",
            file_path="test.mp4",
            language="en",
            transcript="",
            chapters=[],
        )