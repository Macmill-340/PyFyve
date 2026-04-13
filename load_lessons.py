import json


def load_lessons(lesson_files, progress):
    try:
        with open(lesson_files[progress], encoding="utf-8") as f:
            loaded_lesson = json.load(f)
    except Exception as e:
        print(f"Error loading lesson file '{lesson_files[progress]}': {e}")
        return None

    print("\n" + "=" * 60)
    print(f"LESSON {loaded_lesson['id']}: {loaded_lesson['topic']}")
    print("=" * 60)
    print(loaded_lesson["text"].strip())
    print("=" * 60)
    if "common_errors" in loaded_lesson:
        print(f"WATCH OUT FOR: {loaded_lesson['common_errors']}")
        print("=" * 60)
    if "task" in loaded_lesson:
        print(f"YOUR TASK: {loaded_lesson['task']}")
        print("=" * 60)

    return loaded_lesson
