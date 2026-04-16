import os
import time
import sys
import glob
import urllib.parse
from console import console, apply_terminal_theme, reset_terminal_theme, pyinput
from validator_test import validate
from ai_response import get_response
from user_code import exec_code, user_input
from load_lessons import load_lessons
from load_progress import load_progress, save_progress

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LESSON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "lessons"))


def clear_screen():
    """Clear terminal and reapply PyFyve background theme."""
    apply_terminal_theme()


def main():
    clear_screen()

    lesson_files = sorted(glob.glob(os.path.join(LESSON_DIR, "*.json")))

    if not lesson_files:
        console.print(f"No lessons found in '{LESSON_DIR}/'. Check your installation.", style="warning")
        pyinput("Press Enter to exit...")
        sys.exit(1)

    reset_file = True
    progress   = load_progress()

    console.print("\n Welcome to PyFyve\n", style="accent")
    console.print('''
██████╗ ██╗   ██╗███████╗██╗   ██╗██╗   ██╗███████╗
██╔══██╗╚██╗ ██╔╝██╔════╝╚██╗ ██╔╝██║   ██║██╔════╝
██████╔╝ ╚████╔╝ █████╗   ╚████╔╝ ██║   ██║█████╗
██╔═══╝   ╚██╔╝  ██╔══╝    ╚██╔╝  ╚██╗ ██╔╝██╔══╝
██║        ██║   ██║        ██║    ╚████╔╝ ███████╗
╚═╝        ╚═╝   ╚═╝        ╚═╝     ╚═══╝  ╚══════╝
    ''', style="accent")

    console.print("=" * 60, style="separator")
    console.print("  ⚠  BEFORE YOU START", style="warning")
    console.print("=" * 60, style="separator")
    console.print("  - Windows only — Linux/Mac not yet supported.", style="info")
    console.print("  - Infinite loops will freeze the app. Avoid while True.", style="info")
    console.print("  - input() is not supported in lessons.", style="info")
    console.print("  - AI handles common syntax and runtime errors best.", style="info")
    console.print("  - No hints when code runs but gives the wrong result.", style="info")
    console.print("=" * 60, style="separator")
    pyinput("\nPress Enter to continue to lessons...")

    while True:
        if progress >= len(lesson_files):
            console.print("\n" + "=" * 60, style="separator")
            console.print("  🎉 You've completed all lessons! Great work. HIGH FIVE!", style="success")
            console.print("=" * 60, style="separator")
            console.print("\nDo you want to start over?")
            choice = pyinput("y(yes) or n(no)?: ")
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
            console.print(f"Skipping corrupted lesson file: {lesson_files[progress]}", style="warning")
            progress += 1
            save_progress(progress)
            continue

        while True:
            if "task" in lesson:
                mode = pyinput("\n[1] Write Code  [2] Quit\nChoose: ").strip()

                if mode == "1":
                    task      = lesson["task"]
                    user_code = user_input(task, reset_file)
                    result    = exec_code(user_code)

                    console.print("=" * 150, style="separator")
                    console.print("\nYour code:", style="info")
                    console.print(user_code, markup=False)
                    time.sleep(1)
                    console.print("\nOutput:", style="info")
                    console.print(result['output'], markup=False)
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
                        pyinput("\nPress Enter to continue to the next lesson...")
                        break

                    if not result["is_standard"] and result.get("raw_err_str"):
                        query      = f"python code: {user_code.strip()} error: {result['raw_err_str']} "
                        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                        console.print("\nThis is an uncommon error. Try searching for it:", style="info")
                        console.print(search_url)

                        if result["status"] != "sec_error":
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
                    console.print("\nGoodbye!", style="accent")
                    time.sleep(2)
                    sys.exit(0)
                else:
                    console.print("Please enter 1 or 2.", style="warning")

            else:
                progress  += 1
                reset_file = True
                save_progress(progress)
                pyinput("\nPress Enter to continue to the next lesson...")
                break


if __name__ == "__main__":
    try:
        main()
    finally:
        reset_terminal_theme()
