import json
import os

filename = "user_progress.json"

def load_progress():
    if not(os.path.isfile(filename)) or os.path.getsize(filename) == 0:
        save_progress(0)
        return 0

    try:
        with open(filename, "r") as f:
            finished_lesson = json.load(f)
            return finished_lesson.get("finished_lesson_index", 0)
    except Exception as e:
        print(f"Error loading progress: {e}, Resetting file")
        save_progress(0)
        return 0

def save_progress(progress):
    data = {"finished_lesson_index": progress}
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving progress: {e}")