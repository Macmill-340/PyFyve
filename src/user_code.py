import builtins
from console import console, apply_terminal_theme, pyinput
import io
import os
import ast
import subprocess
import sys
import traceback
from contextlib import redirect_stdout

def user_input(task, reset_file):
    filename = "user_workspace.py"
    code_separator = "# Write your code here:"

    if reset_file or not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f'"""\nTASK: {task}\n')
            f.write('--------------------------------------------------\n')
            f.write('INSTRUCTIONS:\n')
            f.write('1. Write your code below.\n')
            f.write('2. Save the file (CTRL+S).\n')
            f.write('3. EXIT this text editor to run your code (Alt + F4).\n')
            f.write('"""\n\n')
            if reset_file:
                f.write(f"{code_separator}\n")

    # Try notepad++ first, fall back to windows notepad otherwise
    try:
        if os.path.exists("npp/npp.exe"):
            subprocess.run(["npp/npp.exe", filename], check=True)
        else:
            console.print("[Note] Bundled editor not found — opening with Notepad.")
            subprocess.run(["notepad.exe", filename], check=True)
    except Exception as e:
        console.print(f"Error opening editor: {e}")
        pyinput(f"Please edit '{filename}' manually, save it, and press [Enter] here...")

    # Full clear + grey background fill after the editor closes.
    # restore_background() alone only sets the colour attribute — blank terminal
    # cells stay black. apply_terminal_theme() clears the screen and fills every
    # cell with grey, giving a clean slate before "Your code:" is printed.
    apply_terminal_theme()

    with open(filename, "r") as f:
        workspace_content = f.read()

    code_parts = workspace_content.split(code_separator)
    separated_code = code_parts[1].strip()
    return separated_code

def security_check(user_code):
    forbidden_modules = {"os", "sys", "shutil", "subprocess"}
    forbidden_functions = {"eval", "exec", "__import__", "open"}
    try:
        tree = ast.parse(user_code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden_modules:
                    return f"Security Error: Importing '{alias.name}' is forbidden."

        if isinstance(node, ast.ImportFrom):
            if node.module in forbidden_modules:
                return f"Security Error: Importing from '{node.module}' is forbidden."

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in forbidden_functions:
                    return f"Security Error: Function '{node.func.id}' is forbidden."
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden_functions:
                    return f"Security Error: Function '{node.func.attr}' is forbidden."
        if isinstance(node, ast.Attribute):
            if node.attr.startswith('__') and node.attr.endswith('__'):
                return f"Security Error: Dunder attribute access is forbidden."

    return None


def exec_code(user_code):
    security_error = security_check(user_code)
    if security_error:
        return {
            "status": "sec_error",
            "output": f"{security_error}\n",
            "variables": {},
            "raw_err_str": security_error,
            "is_standard": True
        }

    whitelist = ['print', 'range', 'len', 'int', 'str', 'float', 'list', 'dict', 'set', 'bool', 'abs', 'min', 'max', 'sum', 'enumerate']
    safe_builtins = {name: getattr(builtins, name) for name in whitelist}
    approved_globals = {"__builtins__": safe_builtins}

    user_locals = {}

    try:
        compiled_code = compile(user_code, "user_workspace.py", "exec")
        f = io.StringIO()
        with redirect_stdout(f):
            exec(compiled_code, approved_globals, user_locals)
        output = f.getvalue().strip()
        return {
            "status": "Success",
            "output": f"{output}\n",
            "variables": user_locals,
            "raw_err_str": None,
            "is_standard": True
        }

    except SyntaxError as se:
        syn_err_map = {
            "cannot assign to literal":
                "You can't assign values to a number or string directly.\n"
                "Variable names go LEFT of '=', values go RIGHT.\n"
                "Correct: age = 25  |  Wrong: 25 = age",

            "cannot assign to function call":
                "You can't put a function call on the left side of '='.\n"
                "Correct: result = print('Hi')  |  Wrong: print('Hi') = result",

            "Missing parentheses in call to 'print'":
                "Python 3 requires parentheses for print statements: Use print('Hello') instead of print 'Hello'",

            "expected an indented block":
                "The line after a colon (:) must be indented with 4 spaces or 1 tab.\n"
                "Mostly used after if, while, for, def statements.",

            "unexpected indent":
                "You have indentation where Python doesn't expect it.\n"
                "Check if the line in the error should align with the line above.",

            "unindent does not match any outer indentation level":
                "Your indentation is inconsistent.\n"
                "Use either all spaces OR all tabs, not both. Python recommends 4 spaces or 1 tab.",

            "EOL while scanning string literal":
                "You forgot to close your quote.\n"
                "Every opening quote (' or \") needs a closing quote on the same line. Check for that in the error line",

            "unexpected EOF while parsing":
                "Your code ended unexpectedly—check for unclosed ( ) [ ] { } in the error line",

            "positional argument follows keyword argument":
                "In function calls, all positional arguments must come before keyword arguments.\n"
                "Correct: func(1, 2, x=3)  |  Wrong: func(x=3, 1, 2)",

            "keyword argument repeated":
                "You used the same keyword argument twice in a function call.\n"
                "Check for duplicate parameter names.",

            "invalid character in identifier":
                "Variable names can only contain letters, numbers, and underscores.\n"
                "They can't start with a number or contain spaces/special characters.",
        }

        syn_err_msg = se.msg
        standard = False
        for key, msg in syn_err_map.items():
            if key in se.msg:
                standard = True
                syn_err_msg = msg
                break
        raw_err_str = f"Syntax Error in line {se.lineno}: {se.msg}"

        return {
            "status": "error",
            "output": f"Syntax Error in line {se.lineno}:\n{syn_err_msg}\n",
            "variables": user_locals,
            "raw_err_str": raw_err_str,
            "is_standard": standard
        }

    except Exception as e:
        tb = sys.exc_info()
        stack = traceback.extract_tb(tb[2])
        lineno = "unknown"
        for frame in reversed(stack):
            if frame.filename == "user_workspace.py":
                lineno = frame.lineno
                break

        if "__import__" in str(e) or "not found" in str(e):
            return {
                "status": "sec_error",
                "output": "Access Denied: Imports are disabled in this sandbox.\n",
                "variables": user_locals,
                "raw_err_str": "Access Denied: Imports are disabled in this sandbox.",
                "is_standard": True
            }

        # Only errors with a single unambiguous cause get a static hint.
        runt_err_map = {
            "ZeroDivisionError":
                "You tried to divide by zero. It is not allowed in programming.\n"
                "Ensure that the denominator is non-zero.",

            "IndexError":
                "You tried to access a list/string index that doesn't exist.\n"
                "Check your index number—lists start at 0, not 1.",

            "KeyError":
                "You tried to access a dictionary key that doesn't exist.\n"
                "Use .get() method or check if key exists with 'if key in dict'.",

            "RecursionError":
                "Your function called itself too many times (infinite recursion).\n"
                "Check your base case—when should the function stop calling itself?",
        }

        error_type = type(e).__name__
        raw_err_str = f"{error_type} on line: {lineno}: {str(e)}"

        if error_type in runt_err_map:
            return {
                "status": "error",
                "output": f"{error_type} on line: {lineno}:\n{runt_err_map[error_type]}\n",
                "variables": user_locals,
                "raw_err_str": raw_err_str,
                "is_standard": True
            }

        return {
            "status": "error",
            "output": f"{error_type} on line: {lineno}:\n{str(e)}\n",
            "variables": user_locals,
            "raw_err_str": raw_err_str,
            "is_standard": False
        }