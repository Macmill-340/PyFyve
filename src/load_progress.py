import json
import os
from console import console

DEFAULT_PROGRESS_FILE = "user_progress.json"


def load_progress(filename=DEFAULT_PROGRESS_FILE):
    if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
        save_progress(0, filename)
        return 0

    try:
        with open(filename, "r") as f:
            return json.load(f).get("finished_lesson_index", 0)
    except Exception as e:
        console.print(f"Error loading progress: {e} — resetting file.", style="warning")
        save_progress(0, filename)
        return 0


def save_progress(progress, filename=DEFAULT_PROGRESS_FILE):
    try:
        with open(filename, "w") as f:
            json.dump({"finished_lesson_index": progress}, f, indent=4)
    except Exception as e:
        console.print(f"Error saving progress: {e}", style="warning")