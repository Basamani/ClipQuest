import json
from pathlib import Path

import streamlit as st

from modules.database import (
    initialize_database,
    save_media,
    get_all_media,
    delete_media,
)
from modules.media_handler import save_uploaded_file, validate_media_url
from modules.transcription import transcribe_media
from modules.chaptering import create_chapters, format_timestamp
from modules.search_engine import build_search_index, search_segments
from modules.study_tools import (
    generate_summary,
    generate_notes,
    generate_quiz,
    generate_flashcards,
)

st.set_page_config(page_title="ClipQuest", page_icon="🎬", layout="wide")
initialize_database()


def load_saved_media():
    library = []

    for item in get_all_media():
        try:
            chapters = json.loads(item.get("chapters") or "[]")
        except (json.JSONDecodeError, TypeError):
            chapters = []

        segments = [
            {
                "start": chapter.get("start", 0),
                "end": chapter.get("end", 0),
                "text": chapter.get("text", ""),
            }
            for chapter in chapters
            if isinstance(chapter, dict)
        ]

        library.append({
            "id": item["id"],
            "name": item["name"],
            "path": item["file_path"],
            "language": item.get("language") or "Unknown",
            "text": item.get("transcript") or "",
            "segments": segments,
            "chapters": chapters,
            "search_index": build_search_index(segments),
        })

    return library


def refresh_library():
    st.session_state.library = load_saved_media()


if "library" not in st.session_state:
    st.session_state.library = load_saved_media()

st.title("🎬 ClipQuest")
st.caption("Every video has the answer.")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Add Media",
        "Deep Search",
        "Video Library",
        "Study Tools",
        "Settings",
    ],
    key="navigation_page",
)

if page == "Home":
    st.header("Welcome to ClipQuest")
    st.write("Turn long videos into searchable chapters and study material.")

    st.markdown("""
    - 🎬 Upload video and audio files
    - 🌐 Choose the spoken language
    - 📑 Create timestamped chapters
    - 🔍 Search across processed media
    - 📝 Generate summaries and notes
    - 🧠 Create flashcards and quizzes
    """)

    st.info("Choose Add Media from the sidebar to get started.")

elif page == "Add Media":
    st.header("Add Media")

    uploaded_file = st.file_uploader(
        "Upload a video or audio file",
        type=[
            "mp4", "mov", "mkv", "webm",
            "mp3", "wav", "m4a", "aac", "flac", "ogg",
        ],
    )

    language_choice = st.selectbox(
        "Spoken language",
        [
            "Auto-detect", "English", "Kannada",
            "Hindi", "Telugu", "Tamil", "Other",
        ],
    )

    language_codes = {
        "English": "en",
        "Kannada": "kn",
        "Hindi": "hi",
        "Telugu": "te",
        "Tamil": "ta",
    }
    language = language_codes.get(language_choice)

    if uploaded_file and st.button("Upload and Process"):
        saved_path = None
        saved_to_database = False

        try:
            with st.spinner("Saving your file..."):
                saved_path = save_uploaded_file(uploaded_file)

            with st.spinner(
                "Transcribing speech. The first run may take longer..."
            ):
                result = transcribe_media(saved_path, language=language)

            segments = result.get("segments", [])
            chapters = create_chapters(segments)

            save_media(
                name=uploaded_file.name,
                file_path=str(saved_path),
                language=result.get("language", "Unknown"),
                transcript=result.get("text", ""),
                chapters=chapters,
            )
            saved_to_database = True

            refresh_library()

            st.success("Processing complete!")
            st.write(f"Detected language: {result.get('language', 'Unknown')}")
            st.write(
                f"Transcript length: {len(result.get('text', ''))} characters"
            )
            st.write(f"Chapters created: {len(chapters)}")

            with st.expander("View transcript"):
                st.write(result.get("text", "") or "No speech detected.")

            st.subheader("Automatic Chapters")

            if chapters:
                for chapter in chapters:
                    st.markdown(
                        f"**{format_timestamp(chapter['start'])} — "
                        f"{chapter['title']}**"
                    )
                    st.write(chapter["text"])
            else:
                st.info("No chapters were created for this media.")

        except Exception as error:
            st.error(f"Processing failed: {error}")
            st.caption(
                "Check the VS Code terminal for details and try a short "
                "supported file."
            )

            if saved_path is not None and not saved_to_database:
                try:
                    Path(saved_path).unlink(missing_ok=True)
                except OSError:
                    pass

    st.divider()
    st.subheader("Media Link")
    st.info(
        "URL checking is available, but direct media downloading "
        "has not been implemented yet."
    )

    media_url = st.text_input("Paste a media URL")

    if st.button("Check Link"):
        if validate_media_url(media_url):
            st.success(
                "The URL format looks valid. The media has not been downloaded."
            )
        else:
            st.error("Enter a valid URL beginning with http:// or https://.")

elif page == "Deep Search":
    st.header("Deep Search")
    query = st.text_input("What do you want to find?")

    if st.button("Search"):
        if not query.strip():
            st.warning("Enter a question or search phrase first.")

        elif not st.session_state.library:
            st.info("Your library is empty. Process a media file first.")

        else:
            all_results = []

            with st.spinner("Searching your library..."):
                for item in st.session_state.library:
                    results = search_segments(
                        query,
                        item["search_index"],
                        top_k=5,
                    )

                    for result in results:
                        all_results.append((item["name"], result))

            all_results.sort(
                key=lambda pair: pair[1]["score"],
                reverse=True,
            )

            if not all_results:
                st.info("No matching segments found.")
            else:
                for name, result in all_results[:10]:
                    st.markdown(
                        f"**{name} — "
                        f"{format_timestamp(result.get('start', 0))}** "
                        f"(match: {result['score']:.2f})"
                    )
                    st.write(result.get("text", ""))

elif page == "Video Library":
    st.header("Video Library")

    if not st.session_state.library:
        st.info("Your library is empty. Process a media file first.")

    else:
        for item in st.session_state.library:
            with st.expander(item["name"]):
                st.write(f"Language: {item['language']}")
                st.write(f"Chapters: {len(item['chapters'])}")
                st.write(f"Saved file: {item['path']}")

                if st.button(
                    "View transcript",
                    key=f"transcript_{item['id']}",
                ):
                    st.write(item["text"] or "No transcript available.")

                if st.button(
                    "Delete media",
                    key=f"delete_{item['id']}",
                ):
                    try:
                        if delete_media(item["id"]):
                            refresh_library()
                            st.success("Media removed from the saved library.")
                            st.rerun()
                        else:
                            st.warning("Media record was not found.")

                    except Exception as error:
                        st.error(f"Could not delete media: {error}")

elif page == "Study Tools":
    st.header("Study Tools")

    if not st.session_state.library:
        st.info("Process a video or audio file first.")

    else:
        options = {
            f"{item['name']} (ID: {item['id']})": item
            for item in st.session_state.library
        }

        selected_label = st.selectbox(
            "Choose media",
            list(options.keys()),
        )
        selected_item = options[selected_label]
        text = selected_item["text"]

        tool = st.selectbox(
            "Choose a tool",
            ["Summary", "Notes", "Flashcards", "Quiz"],
        )

        if st.button("Generate"):
            if not text.strip():
                st.warning("No transcript is available for this media.")

            elif tool == "Summary":
                st.subheader("Summary")
                st.write(generate_summary(text))

            elif tool == "Notes":
                st.subheader("Notes")
                for note in generate_notes(text):
                    st.write(note)

            elif tool == "Flashcards":
                st.subheader("Flashcards")
                cards = generate_flashcards(text)

                if not cards:
                    st.info("Not enough text to create flashcards.")

                for number, card in enumerate(cards, start=1):
                    with st.expander(
                        f"Card {number}: {card['question']}"
                    ):
                        st.write(card["answer"])

            elif tool == "Quiz":
                st.subheader("Quiz")
                questions = generate_quiz(text)

                if not questions:
                    st.info("Not enough text to create quiz questions.")

                for number, question in enumerate(questions, start=1):
                    st.markdown(
                        f"**Question {number}:** {question['question']}"
                    )
                    with st.expander("Reveal answer"):
                        st.write(question["answer"])

elif page == "Settings":
    st.header("Settings")
    st.write("ClipQuest runs locally in your Python environment.")
    st.write("Uploaded files are stored in the project's data/uploads folder.")
    st.write("Media details are stored in the local SQLite database.")
    st.caption(
        "Deleting a library record does not automatically delete "
        "the original uploaded file."
    )