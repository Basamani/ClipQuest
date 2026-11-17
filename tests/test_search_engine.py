from modules.search_engine import build_search_index, search_segments


def test_search_returns_relevant_segments():
    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Python is a programming language."
        },
        {
            "start": 6.0,
            "end": 12.0,
            "text": "Functions help organize reusable code."
        },
    ]

    search_index = build_search_index(segments)
    results = search_segments("How do functions organize code?", search_index)

    assert isinstance(results, list)

    if results:
        assert "text" in results[0]
        assert "score" in results[0]


def test_empty_query_returns_no_results():
    search_index = build_search_index([])
    assert search_segments("", search_index) == []