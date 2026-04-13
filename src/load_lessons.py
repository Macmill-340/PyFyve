import json
from console import console, print_separator


def load_lessons(lesson_files, progress):
    try:
        with open(lesson_files[progress], encoding="utf-8") as f:
            loaded_lesson = json.load(f)
    except Exception as e:
        console.print(f"Error loading lesson file '{lesson_files[progress]}': {e}", style="error")
        return None

    print_separator()
    console.print(f"LESSON {loaded_lesson['id']}: {loaded_lesson['topic']}", style="accent")
    print_separator()
    console.print(loaded_lesson["text"].strip())
    print_separator()

    if "common_errors" in loaded_lesson:
        console.print(f"WATCH OUT FOR: {loaded_lesson['common_errors']}", style="warning")
        print_separator()

    if "task" in loaded_lesson:
        console.print(f"YOUR TASK: {loaded_lesson['task']}", style="task")
        print_separator()

    return loaded_lesson
