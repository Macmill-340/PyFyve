import json
from console import console, print_separator


def load_lessons(lesson_files, progress):
    """Load and display lesson at lesson_files[progress]."""
    try:
        with open(lesson_files[progress], encoding="utf-8") as f:
            loaded_lesson = json.load(f)
    except Exception as e:
        console.print(f"Error loading lesson file '{lesson_files[progress]}': {e}", style="error")
        return None

    print_separator()
    console.print(f"LESSON {loaded_lesson['id']}: {loaded_lesson['topic']}", style="accent")
    print_separator()
    console.print(loaded_lesson["text"].strip(), markup=False)
    # print_separator()
    print("")

    if "common_errors" in loaded_lesson:
        console.print(f"WATCH OUT FOR: {loaded_lesson['common_errors']}", style="warning", markup=False)
        # print_separator()
        print("")

    if "task" in loaded_lesson:
        console.print(f"YOUR TASK: {loaded_lesson['task']}", style="task", markup=False)
        print_separator()
        console.print("Try to solve the given task...I will try to help if you run into any errors.", style="accent")

    return loaded_lesson