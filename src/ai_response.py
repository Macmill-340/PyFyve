import sys
import ollama
import time
import json
from console import console

MODEL_ID = "fyve-ai"



def write_line(text, italic_sage=False):
    """Print one hint sentence with typewriter effect in Sage Leaf."""
    # Base Sage Leaf RGB: 160, 195, 145
    color_code = "\033[38;2;160;195;145m"
    if italic_sage:
        # Adds \033[3; for Italics
        color_code = "\033[3;38;2;160;195;145m"

    sys.stdout.write(color_code)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.01)
    sys.stdout.write("\033[0m\n")
    sys.stdout.flush()


def get_response(lesson_task, user_code, raw_error, max_retries=3, is_init = False):
    """Call local AI model and stream Socratic hint to terminal."""
    system_prompt = """You are a Socratic Python Tutor. You analyse a student's Python error and output ONLY a JSON object with exactly two keys:
    1. "reasoning": Your internal analysis — explicitly identify the SPECIFIC variable, expression, or line causing the error by name. Plan your hint to follow the 3-sentence structure without giving the answer.
    2. "hint": Exactly 3 sentences, each on its own line, separated by newline characters (\n). No more, no less.

    The 3 sentences must follow this exact structure:
    Sentence 1 (Diagnosis): Name the SPECIFIC variable, expression, or construct that caused the error. Do NOT just restate the error type.
    Sentence 2 (Rule): State the Python rule that was violated, clearly and concisely.
    Sentence 3 (Directive): Start with 'Think about...' or 'Consider...' and guide the student toward the fix without giving it.

    IMPORTANT RULES:
    - For AttributeError on strings (.append on a string): the directive MUST guide toward using + or += to combine strings. Do NOT suggest converting to a list.
    - For an extra or unmatched closing parenthesis: the directive must guide toward REMOVING the extra character, not adding a missing one.
    - For missing quotes around text: the directive must guide toward wrapping the entire phrase in quotation marks.

    ABSOLUTE RULES:
    - DO NOT provide corrected code.
    - DO NOT use metaphors or analogies.
    - DO NOT use headings or labels like 'Line 1:' or 'Diagnosis:' in the hint.
    - DO NOT break method names like .append() or .upper() across lines.
    - Write exactly 3 sentences in "hint", no more, no less."""

    user_prompt = f"""PATTERN REFERENCE: You must follow the reasoning style and the 3-sentence hint structure shown in these examples for the task at the end:

    Example 1 (Missing Quotes around multi-word text):
    Task:
    Print the greeting 'Hello, World!' to the screen.
    Code:
    print(Hello, World!)
    Error:
    Syntax Error in line 1: invalid syntax
    {{"reasoning": "The text Hello, World! is inside the print statement without quotes. Python thinks Hello and World! are variables, and the comma is separating arguments. I must guide the student to wrap the entire phrase in quotes so Python treats it as a single string.", "hint": "The text inside your print() call on line 1 is missing the quotation marks needed to mark it as a string literal.\\nIn Python, any plain text that you want to display must be enclosed in either single or double quotes so the interpreter knows it is a string, not a variable or expression.\\nConsider what punctuation characters you would need to add at the beginning and end of the phrase to make Python understand it as a single string value."}}

    Example 2 (Extra Closing Parenthesis):
    Task:
    Calculate the length of the string 'Python'.
    Code:
    length = len('Python'))
    Error:
    SyntaxError: unmatched ')' at line 1
    {{"reasoning": "There is one extra closing parenthesis at the end of line 1. The len() call is already correctly closed. I must guide toward removing the character, not adding one.", "hint": "Your expression on line 1 ends with a closing parenthesis that does not have a matching opening parenthesis.\\nIn Python, every opening parenthesis must be matched by exactly one closing parenthesis — no more, no less.\\nConsider how many opening parentheses appear in that line and whether the number of closing ones matches exactly."}}

    Example 3 (AttributeError string .append):
    Task:
    Add '!' to the end of the variable greeting.
    Code:
    greeting = 'Hello'
    greeting.append('!')
    Error:
    AttributeError: 'str' object has no attribute 'append' at line 2
    {{"reasoning": "The student is calling .append() on a string. .append() is a list method. I must guide them toward using string concatenation (+ or +=) instead.", "hint": "You are calling .append() on the variable greeting, which holds a string value.\\nIn Python, the .append() method belongs exclusively to lists — strings use a different operator to join text together.\\nThink about what operator you would use to combine two strings, and how you could apply it to greeting and the new character using + or +=."}}
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
                model=MODEL_ID,
                messages=messages,
                format="json",
                options={
                    "temperature": 0.0,
                    "num_predict": 1 if is_init else -1,
                },
                keep_alive=-1,
                think=False
            )
            if not is_init:
                full_data = json.loads(response['message']['content'])
                reasoning = full_data.get("reasoning", "")
                hint      = full_data.get("hint", "")

                if not reasoning or not hint:
                    raise ValueError("Missing reasoning or hint keys")

                return hint
            else:
                console.print("[ AI ] Model ready.\n", style="success")
                return None

        except Exception as e:
            if attempt < max_retries:
                console.print(f"[Attempt {attempt} failed: {e}. Retrying...]", style="info")
            else:
                console.print(f"[AI hint unavailable after {max_retries} attempts: {e}]", style="info") if not is_init else console.print(f"[AI model unavailable after {max_retries} attempts: {e}]. Hints will be skipped", style="info")
    return None