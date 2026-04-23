import sys
import atexit
from rich.console import Console
from rich.theme import Theme

pyfyve_theme = Theme({
    "default":    "#E0E0E0",        # Soft gray base text
    "accent":     "bold #F5F5DC",   # Logo & Headers
    "success":    "bold green",     # Standard green for "Correct"
    "warning":    "#E9AF58",        # Important/Caution
    "limitation": "italic #E9AF58", # Specifically for limitation messages
    "error":      "bold #E84118",   # Deep red for crashes
    "info":       "#F5F5DC",        # Subdued metadata
    "prompt":     "bold #F5F5DC",   # Matches Logo for the input cursor
    "task":       "bold #CD736E",   # Instructions
    "hint":       "#F5F5DC",        # AI Advice
    "separator":  "#F5F5DC",        # Subtle division lines
})

console = Console(theme=pyfyve_theme, highlight=False)

def apply_terminal_theme():
    """Paint terminal background #2D2D2D and set base text to #E0E0E0."""
    sys.stdout.write("\033]11;#2D2D2D\007\033]10;#E0E0E0\007\033[0m\033[2J\033[3J\033[H")
    sys.stdout.flush()


def reset_terminal_theme():
    """Restore original terminal colors on exit."""
    sys.stdout.write("\033]110\007\033]111\007\033[0m\033[2J\033[H")
    sys.stdout.flush()


atexit.register(reset_terminal_theme)
apply_terminal_theme()


def pyinput(prompt=""):
    """Print styled prompt then read user input."""
    if prompt:
        console.print(prompt, style="prompt", end="")
    return input()


def print_separator():
    """Print full-width dim separator line."""
    console.print("=" * 60, style="separator")


def print_lesson_header(lesson_id, topic):
    """Print standard lesson title block."""
    print_separator()
    console.print(f"LESSON {lesson_id}: {topic}", style="accent")
    print_separator()


def print_success(message):
    """Print green success message."""
    console.print(f"✅ {message}", style="success")


def print_fail(message):
    """Print red failure message."""
    console.print(f"❌ {message}", style="error")


def print_task(task_text):
    """Print lesson task description followed by separator."""
    console.print(f"YOUR TASK: {task_text}", style="task")
    print_separator()


def print_watch_out(text):
    """Print common-errors warning block."""
    console.print(f"WATCH OUT FOR: {text}", style="warning")
    print_separator()
