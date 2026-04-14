import os
import re
import time
import sys
import glob
import urllib.parse
from console import console
from console import apply_terminal_theme
from validator_test import validate
from ai_response import get_response
from user_code import exec_code, user_input
from load_lessons import load_lessons
from load_progress import load_progress, save_progress

LESSON_DIR = "lessons"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    apply_terminal_theme()


def get_search_url(raw_err_str, user_code):
    """Build a Google search URL containing the error and the specific offending line."""
    offending_line = ""
    try:
        match = re.search(r'line[:\s]+(\d+)', raw_err_str, re.IGNORECASE)
        if match:
            lineno = int(match.group(1))
            lines = user_code.split('\n')
            if 1 <= lineno <= len(lines):
                offending_line = lines[lineno - 1].strip()
    except Exception:
        pass

    query = f"python {raw_err_str}"
    if offending_line:
        query += f" {offending_line}"
    return f"https://www.google.com/search?q={urllib.parse.quote(query)}"


def main():
    clear_screen()

    lesson_files = sorted(glob.glob(os.path.join(LESSON_DIR, "*.json")))

    if not lesson_files:
        console.print(f"No lessons found in '{LESSON_DIR}/'. Check your installation.", style="warning")
        console.input("Press Enter to exit...")
        sys.exit(1)

    reset_file = True
    progress   = load_progress()

    console.print("\n Welcome to PyFyve\n", style="accent")
    console.input("Press Enter to continue to lessons...")

    while True:
        if progress >= len(lesson_files):
            console.print("\n" + "=" * 60, style="separator")
            console.print("  🎉 You've completed all lessons! Great work. HIGH FIVE!", style="success")
            console.print("=" * 60, style="separator")
            console.print("\nDo you want to start over?")
            choice = console.input("y(yes) or n(no)?: ")
            if choice.lower() in ("y", "yes"):
                progress = 0
                save_progress(progress)
                console.print("\nStarting fresh...\n", style="info")
                time.sleep(2)
                continue
            else:
                console.print("Goodbye!", style="info")
                time.sleep(1)
                break

        clear_screen()
        lesson = load_lessons(lesson_files, progress)
        if lesson is None:
            console.print("Could not load the next lesson. Check your lessons folder.", style="error")
            console.input("Press Enter to exit...")
            sys.exit(1)

        while True:
            if "task" in lesson:
                mode = console.input("\n[1] Write Code  [2] Quit\nChoose: ").strip()

                if mode == "1":
                    task      = lesson["task"]
                    user_code = user_input(task, reset_file)
                    result    = exec_code(user_code)

                    console.print(f"\nYour code:", style="info")
                    console.print(user_code)
                    time.sleep(1)
                    console.print(f"\nOutput:", style="info")
                    console.print(result['output'])
                    time.sleep(1)

                    all_passed = True
                    for rule in lesson["validation"]:
                        passed = validate(result, rules=rule, user_code=user_code)
                        if passed.lower() == "fail":
                            all_passed = False
                            break

                    if all_passed:
                        console.print("✅ Task completed. All checks passed.", style="success")
                        progress  += 1
                        reset_file = True
                        save_progress(progress)
                        console.print("\nHIGH FIVE! Lesson complete.\n", style="success")
                        console.input("\nPress Enter to continue to the next lesson...")
                        break

                    # Show search link only for non-standard (uncommon) errors
                    if not result["is_standard"] and result.get("raw_err_str"):
                        search_url = get_search_url(result["raw_err_str"], user_code)
                        console.print(f"\nThis is an uncommon error. Try searching for it:", style="info")
                        console.print(search_url)

                        # AI hint fires only for non-standard and non-security errors
                        if result["status"] != "sec_error" and result.get("raw_err_str"):
                            console.print("\nFetching AI hint...", style="info")
                            try:
                                get_response(
                                    lesson_task=task,
                                    user_code=user_code,
                                    raw_error=result["raw_err_str"]
                                )
                            except Exception:
                                console.print("[AI hint unavailable — continuing without it.]", style="info")

                    console.print("\nTry again.\n", style="info")
                    reset_file = False

                elif mode == "2":
                    console.print("Goodbye!", style="info")
                    sys.exit(0)

                else:
                    console.print("Please enter 1 or 2.", style="warning")
            else:
                # Lesson has no task (intro/reading lesson) — auto-advance
                progress  += 1
                reset_file = True
                save_progress(progress)
                console.input("\nPress Enter to continue to the next lesson...")
                break


if __name__ == "__main__":
    main()
