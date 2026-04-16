# PyFyve — Roadmap

Items marked ✅ are done. Everything else is planned or in progress.

---

## Safety & Sandboxing

- ✅ Code runs in a sandbox — it cannot touch the file system or run system commands
- ✅ Forbidden functions (`eval`, `exec`, `open`, `__import__`) blocked before running
- ✅ Forbidden imports (`os`, `sys`, `subprocess`, etc.) blocked via AST check
- ✅ Output captured cleanly via `redirect_stdout` without affecting app output
- ✅ `markup=False` on all `console.print()` calls that display student code or output
- [ ] **Infinite loop timeout** — `while True: pass` freezes the app. Need a background thread or `multiprocessing` that kills runaway code after a configurable timeout.
- [ ] **Smarter source checking** — `source_check` does a plain text search. Upgrade to AST inspection so only actual code usage counts.
- [ ] **Per-lesson module access** — add an optional `"allowed_imports"` field to enable `math`, `random`, etc. in specific lessons.

---

## Crash & Error Handling

- ✅ Missing code separator in workspace file — graceful recovery with warning message
- ✅ AI unavailability — lesson loop continues normally if Ollama is offline or the model returns malformed JSON
- ✅ Corrupted lesson file — skipped with a warning, progress advances automatically
- ✅ Progress file corruption — resets to 0 with a warning
- [ ] **Workspace file read error** — if `user_workspace.py` cannot be read after the editor closes, add a try/except around the file read.

---

## Practical Upgrades & Polish

- [ ] **Input mocking** — support `input()` calls by feeding values from the lesson JSON.
- [ ] **File watcher** — auto-run code on Ctrl+S instead of requiring the student to close the editor.
- [ ] **Visual progress** — persistent "Lesson X of Y" header during each lesson.
- [ ] **Attempt tracking** — AI hints become slightly more detailed if the student fails 3+ times on the same task.

---

## Editor & User Experience

- ✅ Bundled Notepad++ editor on Windows
- ✅ Notepad fallback if bundled editor is missing
- ✅ Terminal resizes to a comfortable width on launch
- ✅ Screen clears at the start of each lesson
- ✅ Restart-from-scratch option after completing all lessons
- ✅ Limitations notice shown on every launch
- [ ] **Cross-platform support** — proper Linux and Mac editor integration.
- [ ] **3-strike rule** — after failing the same task 3 times, offer to reveal the solution.
- [ ] **Multiple tasks in one lesson** — support for a `"tasks"` array so a lesson walks through 2-3 connected steps.
- [ ] **Practice exercise mode** — separate mode with harder tasks, no tutorial text, and no progress saved.
- [ ] **Better `source_check` failure messages** — more specific messaging that reflects the actual requirement that failed.
- [ ] **Local session stats** — track attempts per lesson and most common errors.

---

## AI Hints

- ✅ AI fires on non-standard Python errors and streams the hint one character at a time
- ✅ Hint is always exactly 3 sentences: what went wrong, which rule was broken, a guiding question
- ✅ Third sentence rendered in italic cyan to visually distinguish it
- ✅ AI retries up to 3 times if the response is malformed
- ✅ App keeps running if the AI is unavailable
- ✅ Ambiguous runtime errors (NameError, TypeError, AttributeError) removed from static hint map — AI handles these
- [ ] **Hints for wrong answers** — when code runs fine but gives wrong output or wrong variable value.
- [ ] **Expand model training data** — handle trailing comma creating tuples, stray brackets in unusual positions.

---

## Lessons & Curriculum

- ✅ Validator supports: `variable_check`, `output_check`, `type_check`, `source_check`, `collection_check`
- ✅ Multiple validation rules per lesson (all must pass)
- ✅ Type mismatch detection — tells the student when they used the wrong data type
- ✅ Float-numbered lesson files so new lessons insert anywhere without renaming
- ✅ Lessons without a `task` field auto-advance (reading/intro lessons)
- ✅ **Hello World lesson** — the very first lesson should be a simple `print("Hello, World!")` task.
- [ ] **Full beginner curriculum** — While Loops, Functions, Dictionaries, String Methods, and more.
- [ ] **Multi-step lessons** — walk through a concept in 2-3 connected tasks within one lesson.
- [ ] **Nested data checks** — `collection_check` for nested structures (e.g. a list of dicts).
- [ ] **Function testing** — run the student's function against multiple hidden test inputs.
- [ ] **Automated lesson tests** — test suite for `validator_test.py`.

---

## Setup & Distribution

- ✅ `start.bat` sets up a Python virtual environment automatically
- ✅ Dependencies installed and updated automatically (MD5 hash check)
- ✅ Ollama installed and launched automatically if not running
- ✅ Modelfile and AI model downloaded automatically on first run
- ✅ Model update check on launch with automatic cleanup
- ✅ No manual terminal commands required
- [ ] **`.gitignore` audit** — confirm `*.gguf`, `model/`, `user_progress.json`, `user_workspace.py`, `__pycache__/`, `.venv/` are all excluded.
- [ ] **One-click installer** — bundle Python, the app, and the model into a single `.exe`.
