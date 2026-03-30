import json
def load_lessons(lesson_files, progress):
    try:
        with open(lesson_files[progress]) as f:
            loaded_lesson = json.load(f)
    except Exception as e:
        print(f"Error loading lesson: {e}")

    print("\n" + "=" * 50)
    print(f"LESSON {loaded_lesson["id"]}: {loaded_lesson["topic"]}")
    print("=" * 50)
    print(loaded_lesson["text"].strip())
    print("=" * 50)
    print(f"WATCH OUT FOR: {loaded_lesson["common_errors"]}")
    print("=" * 50)
    print(f"YOUR TASK: {loaded_lesson['task']}")
    return loaded_lesson