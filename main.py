import sys
import glob
import urllib.parse
from validator_test import validate
from ai_response import get_response
from user_code import exec_code, user_input
from load_lessons import load_lessons
from load_progress import load_progress, save_progress

lesson_files = sorted(glob.glob("placeholder_lessons/*.json", recursive=True))


def main():

    reset_file = True
    progress = load_progress()
    if progress < len(lesson_files):
        print(f"📂 Starting at: {lesson_files[progress]}")
    else:
        print("🎉 You have already completed all available lessons!")

    while True:
        if progress >= len(lesson_files):
            print("All lessons completed.")
            break

        lesson = load_lessons(lesson_files, progress)
        task   = lesson["task"]

        while True:
            mode = input("\n[1] Write Code\n[2] Quit\nChoose(1/2): ").strip()

            if mode == "1":
                user_code = user_input(task, reset_file)
                result    = exec_code(user_code)
                print(f"Your code:\n{user_code}\n")
                print(f"Output:\n{result['output']}")

                all_passed = True
                for types in lesson["validation"]:
                    passed = validate(result, rules=types, user_code=user_code)
                    if passed.lower() == "fail":
                        all_passed = False
                        break

                if all_passed:
                    print("✅ Task Completed. All checks passed.")
                    progress   += 1
                    reset_file  = True
                    save_progress(progress)
                    break

                # Show search link only for non-standard errors (multiple possible causes)
                if not result["is_standard"]:
                    query        = f"python {result['raw_err_str']}"
                    search_url   = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                    print(f"You have hit a non-standardized error.\n"
                          f"Try searching the web with the following link:\n{search_url}\n")

                # AI hint for all errors except security blocks
                if result["status"] != "sec_error":
                    print("Fetching AI Hint...")
                    get_response(
                        lesson_task=task,
                        user_code=user_code,
                        raw_error=result["raw_err_str"]
                    )

                print("Try Again")
                reset_file = False

            elif mode == "2":
                sys.exit()

            else:
                print("Please choose a valid option.")

if __name__ == "__main__":
    main()