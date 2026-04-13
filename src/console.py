import os
from rich.console import Console
from rich.theme import Theme
def apply_terminal_theme():
    if os.environ.get("WT_SESSION"):
        # Dark grey background, white foreground, clear screen
        print("\033[48;2;45;45;45m\033[38;2;240;240;240m\033[2J\033[H", end="", flush=True)

# All colours are defined here. Change them in one place.
pyfyve_theme = Theme({
    "default":      "white",
    "accent":       "bold cyan",           # lesson titles, section headers
    "success":      "bold green",          # ✅ pass messages
    "warning":      "bold yellow",         # ⚠️ watch out messages
    "error":        "bold red",            # ❌ fail messages
    "info":         "dim white",           # secondary info, separators
    "prompt":       "bold white",          # input prompts
    "task":         "bold white",          # YOUR TASK text
    "hint_line1":   "white",               # AI hint sentence 1
    "hint_line2":   "white",              # AI hint sentence 2
    "hint_line3":   "italic cyan",        # AI hint sentence 3 (the question)
    "separator":    "dim white",          # "═" dividers
})

console = Console(theme=pyfyve_theme, highlight=False)

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