import os
from rich.console import Console
from rich.theme import Theme

def apply_terminal_theme():

    if os.environ.get("WT_SESSION"):
        # Set background RGB(45,45,45), foreground RGB(240,240,240), clear screen
        print("\033[48;2;45;45;45m\033[38;2;240;240;240m\033[2J\033[H", end="", flush=True)

# Apply once at import time for the initial launch screen.
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