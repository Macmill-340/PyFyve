import os
import sys
from rich.console import Console
from rich.theme import Theme

# ANSI sequences. Centralised here so ai_response.py can import them too.
ANSI_BG  = "\033[48;2;45;45;45m"    # grey background  RGB(45,45,45)
ANSI_FG  = "\033[38;2;240;240;240m"  # white foreground RGB(240,240,240)
IN_WT    = bool(os.environ.get("WT_SESSION"))


def apply_terminal_theme():
    """
    Full clear + set background/foreground. Use on clear_screen() and after
    the code editor subprocess closes (to wipe black areas before printing results).
    """
    if IN_WT:
        # Set background, set foreground, clear entire screen, move cursor to top-left.
        # \033[2J fills ALL terminal cells with the current background — this is the
        # only way to make blank areas grey, not just text characters.
        sys.stdout.write(f"{ANSI_BG}{ANSI_FG}\033[2J\033[H")
        sys.stdout.flush()


def pyinput(prompt=""):
    """
    Replacement for console.input() / input() throughout the app.

    Rich's console.input() renders its prompt and then resets ANSI state
    with \\033[0m before Python reads input. The OS then echoes typed
    characters using the terminal's default background (black).

    This function renders the prompt with Rich, then immediately re-asserts
    the ANSI background codes BEFORE input() is called, so the OS echoes
    keystrokes on the correct grey background.
    """
    if prompt:
        # end="" so no newline — cursor stays on the same line for the user to type
        console.print(prompt, style="prompt", end="")
    if IN_WT:
        # Re-assert background AFTER Rich has finished rendering (and resetting)
        sys.stdout.write(ANSI_BG + ANSI_FG)
        sys.stdout.flush()
    return input()


# Apply once at import time so the setup screen already has the grey background.
apply_terminal_theme()


pyfyve_theme = Theme({
    "default":    "white",
    "accent":     "bold cyan",
    "success":    "bold green",
    "warning":    "bold yellow",
    "error":      "bold red",
    "info":       "dim white",
    "prompt":     "bold white",
    "task":       "bold white",
    "hint_line1": "white",
    "hint_line2": "white",
    "hint_line3": "italic cyan",
    "separator":  "dim white",
})

console = Console(
    theme=pyfyve_theme,
    highlight=False,
    style="on rgb(45,45,45)",
)


def print_separator():
    console.print("=" * 60, style="separator")

def print_lesson_header(lesson_id, topic):
    print_separator()
    console.print(f"LESSON {lesson_id}: {topic}", style="accent")
    print_separator()

def print_success(message):
    console.print(f"✅ {message}", style="success")

def print_fail(message):
    console.print(f"❌ {message}", style="error")

def print_task(task_text):
    console.print(f"YOUR TASK: {task_text}", style="task")
    print_separator()

def print_watch_out(text):
    console.print(f"WATCH OUT FOR: {text}", style="warning")
    print_separator()