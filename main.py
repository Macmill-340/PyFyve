import os
import time
import sys
import glob
import urllib.parse
from console import console
from validator_test import validate
from ai_response import get_response
from user_code import exec_code, user_input
from load_lessons import load_lessons
from load_progress import load_progress, save_progress

LESSON_DIR = "placeholder_lessons"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    clear_screen()

    lesson_files = sorted(glob.glob(os.path.join(LESSON_DIR, "*.json")))

    if not lesson_files:
        console.print(f"No lessons found in '{LESSON_DIR}/'.", style = "warning")
        console.print("Please make sure the lessons folder exists and contains lesson JSON files.")
        input("Press Enter to exit...")
        sys.exit(1)

    reset_file = True
    progress   = load_progress()

    print(f"""\n Welcome to PyFyve
""")
    input("Press Enter to continue to lessons...")

    while True:
        if progress >= len(lesson_files):
            print("=" * 60)
            print("  🎉 You've completed all lessons! Great work. HIGH FIVE!")
            print("=" * 60)
            print("\nDo you want to start over?")
            choice = input("y(yes) or n(no)?: ")
            if choice == "y" or choice == "yes":
                progress = 0
                save_progress(progress)
                print("\nStarting fresh...\n")
                time.sleep(2)
                continue
            else:
                print("Exiting...")
                time.sleep(2)
                break

        clear_screen()
        lesson = load_lessons(lesson_files, progress)
        if lesson is None:
            print(" Could not load the next lesson. Check your lessons folder.")
            input("Press any key to exit")
            sys.exit(1)

        while True:
            if "task" in lesson:
                mode = input("\n[1] Write Code  [2] Quit\nChoose: ").strip()

                if mode == "1":
                    task = lesson["task"]
                    user_code = user_input(task, reset_file)
                    result    = exec_code(user_code)

                    print(f"\nYour code:\n{user_code}")
                    print(f"\nOutput:\n{result['output']}")

                    all_passed = True
                    for rule in lesson["validation"]:
                        passed = validate(result, rules=rule, user_code=user_code)
                        if passed.lower() == "fail":
                            all_passed = False
                            break

                    if all_passed:
                        print("✅ Task completed. All checks passed.")
                        progress  += 1
                        reset_file = True
                        save_progress(progress)
                        print("\nHIGH FIVE! Lesson complete.\n")
                        input("\nPress Enter to continue to the next lesson...")
                        break

                    if not result["is_standard"] and result.get("raw_err_str"):
                        query      = f"python {result['raw_err_str']}"
                        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                        print(f"\nThis is an uncommon error. Try searching for it:\n{search_url}\n")

                        if result["status"] != "sec_error" and result.get("raw_err_str"):
                            print("Fetching AI hint...")
                            try:
                                get_response(
                                    lesson_task=task,
                                    user_code=user_code,
                                    raw_error=result["raw_err_str"]
                                )
                            except Exception:
                                print("[AI hint unavailable — continuing without it.]")

                    print("\nTry again.\n")
                    reset_file = False

                elif mode == "2":
                    print("Goodbye!")
                    sys.exit(0)

                else:
                    print("Please enter 1 or 2.")
            else:
                progress += 1
                reset_file = True
                save_progress(progress)
                print("\nHIGH FIVE! Lesson complete.\n")
                input("\nPress Enter to continue to the next lesson...")
                break


if __name__ == "__main__":
    main()
