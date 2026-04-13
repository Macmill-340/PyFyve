"""
console.py — PyFyve Rich console configuration.

Import this module instead of using print() directly:
    from console import console
    console.print("Your message here")
    console.print("[accent]Highlighted text[/accent]")

The grey terminal background is set via ANSI escape codes at import time.
It applies only to this terminal session — the user's terminal returns to
normal when they close the window. No cleanup required.

Works best inside Windows Terminal. In standard cmd, color is controlled
by start.bat's `color` command instead and the ANSI codes are ignored.
"""

import os
from rich.console import Console
from rich.theme import Theme

# ── Session-scoped terminal background ────────────────────────────────────────
# ANSI escape: set background to dark grey (RGB 45, 45, 45) and clear the screen.
# This only takes effect in terminals that support VT/ANSI sequences (Windows Terminal).
# In standard cmd, these codes are ignored and start.bat's `color` command applies.
if os.environ.get("WT_SESSION"):
    # Dark grey background, white foreground, clear screen
    print("\033[48;2;45;45;45m\033[38;2;240;240;240m\033[2J\033[H", end="", flush=True)

# ── Rich theme ─────────────────────────────────────────────────────────────────
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
    "separator":    "dim white",          # ═══ dividers
})

# ── Console instance ───────────────────────────────────────────────────────────
# Import this and use console.print() everywhere instead of print().
console = Console(theme=pyfyve_theme, highlight=False)


# ── Helper functions ───────────────────────────────────────────────────────────

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