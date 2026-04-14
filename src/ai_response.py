import sys
import ollama
import time
import json
from console import console

def _write_line(text, italic_cyan=False):
    """Write one hint line with typewriter effect."""
    if italic_cyan:
        sys.stdout.write("\033[3;96m") # Italic Cyan

    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.01)

    sys.stdout.write("\033[0m\n") # Reset and Newline
    sys.stdout.flush()

# ... get_response function continues as normal ...


def get_response(lesson_task, user_code, raw_error, max_retries=3):
    system_prompt = """You are a Socratic Python Tutor. You analyse a student's Python error and output ONLY a JSON object with exactly two keys:
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

    user_prompt = f"""EXAMPLES — study how each hint guides toward the concept without stating the fix:

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
        Task:\n{lesson_task}\n
        Code:\n{user_code}\n
        Error:\n{raw_error}\n
        JSON:"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]

    for attempt in range(1, max_retries + 1):
        try:
            response = ollama.chat(
                model="fyve-ai",
                messages=messages,
                format="json",
                options={"temperature": 0.2},
                think=False
            )
            full_data = json.loads(response['message']['content'])
            reasoning = full_data.get("reasoning", "")
            hint      = full_data.get("hint", "")

            if not reasoning or not hint:
                raise ValueError("Missing reasoning or hint keys")

            console.print("\nAI RESPONSE:", style="accent")
            console.print("Hint:", style="info")

            hint_lines = [l.strip() for l in hint.split('\n') if l.strip()]
            for i, line in enumerate(hint_lines):
                _write_line(line, italic_cyan=(i == 2))
            return

        except Exception as e:
            if attempt < max_retries:
                console.print(f"[Attempt {attempt} failed: {e}. Retrying...]", style="info")
            else:
                console.print(f"[AI hint unavailable after {max_retries} attempts: {e}]", style="info")