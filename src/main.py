import os
import time
import sys
import glob
import shutil
import subprocess
import urllib.parse
from ai_response import MODEL_ID
from ai_response import write_line
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

    # Load the AI model into memory before showing the welcome screen.
    # This is a blocking call — the app waits here deliberately so the user
    # sees a clear status message rather than an unexplained delay later.
    # On CPU-only machines this can take 1-2 minutes on first run of a session.
    console.print("\n[ AI ] Loading model into memory...", style="info")
    try:
        import ollama as _ollama
        _ollama.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": """You are a Socratic Python Tutor. You analyse a student's Python error and output ONLY a JSON object with exactly two keys:
                    1. "reasoning": First, explicitly quote the exact line of code that failed. Then, identify what is structurally missing or wrong with that specific line.
                    2. "hint": Exactly 3 sentences separated by newline characters (\\n).
                    
                    The 3 sentences must follow this exact structure:
                    Sentence 1: Diagnose the specific error - name the variable or construct involved.
                    Sentence 2: State the Python rule that was violated, clearly and concisely.
                    Sentence 3: Start with 'Think about...' or 'Consider...' and guide the student toward the fix.
                    
                    Rules:
                     - DO NOT provide corrected code.
                     - DO NOT use metaphors or analogies.
                     - DO NOT use headings or labels like 'Line 1:'.
                     - Write exactly 3 sentences in "hint", no more, no less."""
                                    },
                                    {
                                        "role": "user",
                                        "content": f"""EXAMPLES — study how each hint guides toward the concept without stating the fix:
                    
                            Example 1 (Missing Colon):
                            Task:
                            Write an if statement that prints 'Yes' if x is greater than 5.
                            Code:
                            x = 10
                            if x > 5
                                print('Yes')
                            Error:
                            SyntaxError: expected ':' at line 2
                            {{"reasoning": "The if statement on line 2 is missing a colon after the condition. I will name the construct, explain the punctuation rule, and direct the student to think about what Python requires after every control flow header — not state the character.", "hint": "Your if statement on line 2 does not end with the required punctuation after the condition 'x > 5'.\\nIn Python, every control flow header — if, for, while, and def — must end with a specific punctuation mark to signal the start of the indented block.\\nThink about what punctuation character Python requires at the end of every control flow header."}}
                    
                            Example 2a (Extra Closing Parenthesis — remove, not add):
                            Task:
                            Print a simple message.
                            Code:
                            print('Done'))
                            Error:
                            SyntaxError: unmatched ')' at line 1
                            {{"reasoning": "There is one extra closing parenthesis at the end of line 1. The print call is already correctly closed. I must guide toward counting and removing — NOT adding anything.", "hint": "Your print statement on line 1 has one more closing parenthesis than it has opening ones.\\nIn Python, every opening parenthesis must be matched by exactly one closing parenthesis — no more, no less.\\nConsider how many opening parentheses appear in that line and whether the number of closing ones matches exactly."}}
                    
                            Example 2b (Stray Parenthesis in Assignment):
                            Task:
                            Assign 90 to the variable stamina.
                            Code:
                            stamina = 90)
                            Error:
                            SyntaxError: unmatched ')' at line 1
                            {{"reasoning": "The assignment 'stamina = 90)' ends with a closing parenthesis, but there is no opening parenthesis on the line. I must point out the stray character without claiming assignments can't have parentheses.", "hint": "Your assignment on line 1 ends with a closing parenthesis ')', but there is no opening parenthesis to match it.\\nIn Python, a closing parenthesis is only valid if it follows an earlier opening parenthesis.\\nLook closely at the end of the line and remove the stray character that does not belong there."}}
                    
                            Example 3 (AttributeError string .append — guide toward +, not list):
                            Task:
                            Create a string 'Hello' and try to append ' World' using .append().
                            Code:
                            s = 'Hello'
                            s.append(' World')
                            Error:
                            AttributeError: 'str' object has no attribute 'append' at line 2
                            {{"reasoning": "s is a string. The student wants to add text to it using .append() which is a list method. I must guide toward + or += for string joining — never toward converting to a list.", "hint": "You are calling .append() on the variable s, which holds a string value.\\nIn Python, .append() belongs exclusively to lists — strings use a different operator to join text together.\\nThink about what operator you would use to combine two strings, and how you could apply it to s and the new text using + or +=."}}
                    
                            Example 4 (NameError — case sensitivity):
                            Task:
                            Create a variable score = 95 and print its value.
                            Code:
                            score = 95
                            print(Score)
                            Error:
                            NameError: name 'Score' is not defined at line 2
                            {{"reasoning": "score is defined lowercase but Score (capital S) is used in print. I name both spellings, explain case sensitivity, and direct toward comparing the two usages.", "hint": "You defined a variable called score on line 1 but referenced Score on line 2.\\nIn Python, variable names are case-sensitive, so score and Score are treated as two completely different identifiers.\\nConsider whether the capitalisation of the variable name is consistent between where it was defined and where it is used."}}
                    
                            Example 5 (TypeError — str + int):
                            Task:
                            Add the string 'Age: ' to the integer 25 and print.
                            Code:
                            age = 25
                            print('Age: ' + age)
                            Error:
                            TypeError: can only concatenate str (not 'int') to str at line 2
                            {{"reasoning": "The + operator tries to combine a string literal and an integer variable. I name both operands and explain type compatibility, directing toward conversion without naming str().", "hint": "The expression on line 2 uses + to combine the string literal 'Age: ' with the variable age, which holds an integer.\\nIn Python, the + operator can only join values of the same type — a string and an integer are incompatible without conversion.\\nThink about what you would need to do to one of the values so that both sides of the + operator are the same type."}}
                    
                            Example 6 (Mismatched Brackets — list):
                            Task:
                            Create a list of numbers 1, 2, 3.
                            Code:
                            nums = [1, 2, 3)
                            Error:
                            SyntaxError: closing parenthesis ')' does not match opening parenthesis '[' at line 1
                            {{"reasoning": "The list opens with '[' but closes with ')'. I name the variable, explain that bracket types must match, and direct toward thinking about which bracket type belongs to a list.", "hint": "Your list nums on line 1 opens with a square bracket but closes with a different bracket type.\\nIn Python, a list must open and close with the same bracket type, and each bracket type has a specific purpose in the language.\\nConsider which bracket type is used to define a list and whether the closing bracket on that line matches the opening one."}}
                    
                            Example 7 (NoneType — function returns nothing):
                            Task:
                            Define a function greet() that prints 'Hello', call it, store the result, then print the result with '!'.
                            Code:
                            def greet():
                                print('Hello')
                            result = greet()
                            print(result + '!')
                            Error:
                            TypeError on line: 4: can only concatenate str (not 'NoneType') to str
                            {{"reasoning": "greet() has no return statement so it returns None. result holds None. I name the variable result, explain that functions without return produce None, and guide toward thinking about what the function actually gives back.", "hint": "The variable result on line 3 holds the value that greet() produces when called.\\nIn Python, a function that does not have a return statement automatically produces a value that cannot be used in string or arithmetic expressions.\\nThink about what greet() currently gives back when it finishes, and what you would need to add to make it produce a usable value."}}
                    
                            Example 8 (UnboundLocalError — variable used before local assignment):
                            Task:
                            Write a function that adds 10 to a global variable total and prints it.
                            Code:
                            total = 50
                            def add_ten():
                                total += 10
                                print(total)
                            add_ten()
                            Error:
                            UnboundLocalError on line: 3: local variable 'total' referenced before assignment
                            {{"reasoning": "Inside add_ten(), total += 10 makes Python treat total as local. But it has no local value yet. I name the variable and line, explain that assignment inside a function creates a local variable, and guide toward what Python needs to know about total.", "hint": "The variable total on line 3 is being modified inside add_ten(), which makes Python treat it as a local variable with no initial value.\\nIn Python, any variable that is assigned inside a function is considered local to that function — even if a variable with the same name exists outside.\\nConsider what Python needs to know about total before the function can modify the value that exists outside it."}}
                    
                            Example 9 (RecursionError — missing base case):
                            Task:
                            Write a recursive function countdown() that prints numbers from n down to 1.
                            Code:
                            def countdown(n):
                                print(n)
                                countdown(n - 1)
                            countdown(5)
                            Error:
                            RecursionError on line: 3: maximum recursion depth exceeded
                            {{"reasoning": "countdown() calls itself on every invocation with no condition to stop. I name the function and recursive call, explain that recursion requires a stopping condition, and guide toward what value of n should stop the calls.", "hint": "Your function countdown() on line 3 calls itself every time without any condition that would stop the calls.\\nIn Python, a recursive function must have a condition that stops it from calling itself — otherwise it runs until the program crashes.\\nThink about what value of n means the countdown is finished, and what you could check at the start of the function to stop it at that point."}}
                    
                            ---
                            NOW GENERATE JSON FOR THIS CASE:
                            Task:
                            Write an if statement that prints 'Yes' if x is greater than 5.
                            Code:
                            x = 10
                            if x > 5
                                print('Yes')
                            Error:
                            SyntaxError: expected ':' at line 2
                            JSON:"""
                }
            ],
            format="json",
            options={
                "temperature": 0.2,
                "num_predict": 1,
                "num_thread": 4,
                "num_ctx": 2048
            },
            keep_alive=-1,
            think=False
        )
        console.print("[ AI ] Model ready.\n", style="success")
    except Exception:
        console.print("[ AI ] Model unavailable — hints will be skipped.\n", style="warning")
    time.sleep(1)

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
    console.print("  - Windows only — Linux/Mac not yet supported.", style="limitation")
    console.print("  - Infinite loops will freeze the app. Avoid while True.", style="limitation")
    console.print("  - input() is not supported in lessons.", style="limitation")
    console.print("  - AI handles common syntax and runtime errors best.", style="limitation")
    console.print("  - No hints when code runs but gives the wrong result.", style="limitation")
    console.print("=" * 60, style="separator")
    pyinput("\nPress Enter to continue to lessons...")

    while True:
        if progress >= len(lesson_files):
            console.print("\n" + "=" * 60, style="separator")
            console.print("  🎉 You've completed all lessons! Great work!", style="success")
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

                    console.print(":" * 150, style="separator")
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
                        console.print("\nCongratulations! You did it. Lesson complete.\n", style="success")
                        pyinput("\nPress Enter to continue to the next lesson...")
                        break

                    if not result["is_standard"] and result.get("raw_err_str"):
                        query      = f"python code: {user_code.strip()} error: {result['raw_err_str']} "
                        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                        console.print("\nThis is an uncommon error. Try searching for it:", style="info")
                        console.print(search_url)
                        console.print("")

                        if result["status"] != "sec_error":
                            hint_text = None
                            with console.status("[info]Fetching AI hint...[/info]", spinner="dots", spinner_style="hint"):
                                hint_text = get_response(
                                    lesson_task=task,
                                    user_code=user_code,
                                    raw_error=result["raw_err_str"]
                                )
                            if hint_text:
                                console.print("\nAI RESPONSE:", style="accent")
                                console.print("Hint:", style="info")

                                hint_lines = [l.strip() for l in hint_text.split('\n') if l.strip()]
                                for i, line in enumerate(hint_lines):
                                    # i == 2 is the 3rd sentence for the Socratic nudge
                                    write_line(line, italic_sage=(i == 2))
                            else:
                                console.print("[AI hint unavailable — continuing without it.]", style="info")

                    console.print("\nTry again.\n", style="info")
                    reset_file = False

                elif mode == "2":
                    console.print("\nUnloading model from memory", style="info")
                    # Unload model from RAM so Ollama doesn't hold ~2.5 GB
                    # of memory after PyFyve closes.
                    try:
                        _ollama_exe = shutil.which("ollama")
                        if _ollama_exe:
                            subprocess.run([str(_ollama_exe), "stop", MODEL_ID], capture_output=True, timeout=5)
                        console.print("\nGoodbye!", style="accent")
                        time.sleep(1)
                    except Exception:
                        pass
                    time.sleep(1)
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