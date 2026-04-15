# PyFyve — Roadmap

Items marked ✅ are done. Everything else is planned or in progress.

---

## Safety & Sandboxing

- ✅ Code runs in a sandbox — it cannot touch the file system or run system commands
- ✅ Forbidden functions (`eval`, `exec`, `open`, `__import__`) blocked before running
- ✅ Forbidden imports (`os`, `sys`, `subprocess`, etc.) blocked via AST check
- ✅ Output captured cleanly via `redirect_stdout` without affecting app output
- ✅ `markup=False` on all `console.print()` calls that display student code or output — prevents Rich from interpreting brackets as markup tags
- [ ] **Infinite loop timeout** — `while True: pass` freezes the app with no recovery. Need a background thread or `multiprocessing` that kills runaway code after a configurable timeout and returns a clean error dict to the lesson loop.
- [ ] **Smarter source checking** — `source_check` does a plain text search, so a keyword inside a comment or string literal passes incorrectly. Upgrade to AST inspection so only actual code usage counts.
- [ ] **Per-lesson module access** — some lessons will need `math`, `random`, etc. Add an optional `"allowed_imports"` field to the lesson JSON and unlock only those modules in `approved_globals` for that lesson.

---

## Crash & Error Handling

- ✅ Missing code separator in workspace file — graceful recovery with warning message and file reset instead of IndexError crash
- ✅ AI unavailability — lesson loop continues normally if Ollama is offline or the model returns malformed JSON
- ✅ Corrupted lesson file — skipped with a warning, progress advances automatically
- ✅ Progress file corruption — resets to 0 with a warning instead of crashing
- [ ] **Workspace file read error** — if `user_workspace.py` cannot be read after the editor closes (permission issue, antivirus lock), the app currently crashes. Add a try/except around the file read in `user_input()`.

---

## Practical Upgrades & Polish

- [ ] **Input mocking** — support `input()` calls by feeding values from the lesson JSON, enabling lessons that teach interactive programs.
- [ ] **File watcher** — auto-run code on Ctrl+S (save) instead of requiring the student to close the editor entirely.
- [ ] **Visual progress** — persistent "Lesson X of Y" header visible during each lesson.
- [ ] **Attempt tracking** — AI hints become slightly more detailed if the student fails 3+ times on the same task.

---

## Editor & User Experience

- ✅ Bundled Notepad++ editor on Windows
- ✅ Notepad fallback if bundled editor is missing
- ✅ Terminal resizes to a comfortable width on launch (via Windows Terminal relaunch in `start.bat`)
- ✅ Screen clears at the start of each lesson — no setup noise visible during lesson content
- ✅ Restart-from-scratch option after completing all lessons
- ✅ Limitations notice shown on every launch so new users are not surprised by known gaps
- [ ] **Cross-platform support** — proper Linux and Mac editor integration, tested end-to-end. Only after Windows is stable.
- [ ] **Escape hatch (3-strike rule)** — after failing the same task 3 times, offer to reveal the solution. Being completely stuck with no way forward is worse than seeing an answer once.
- [ ] **Multiple tasks in one lesson** — add support for a `"tasks"` array so a lesson walks through a concept in 2-3 connected steps. Requires changes to the validator loop in `main.py` and the lesson JSON schema.
- [ ] **Practice exercise mode** — a separate mode with harder tasks, no tutorial text, and no progress saved. Uses a separate `exercises/` folder with the same JSON format.
- [ ] **Better `source_check` failure messages** — the current message is generic and often misleading. It should reflect the specific requirement that failed.
- [ ] **Local session stats** — track attempts per lesson and most common errors, saved quietly to `stats.json`.

---

## AI Hints

- ✅ AI fires on non-standard Python errors and streams the hint one character at a time
- ✅ Hint is always exactly 3 sentences: what went wrong, which rule was broken, a guiding question
- ✅ Third sentence (guiding question) rendered in italic cyan to visually distinguish it
- ✅ AI retries up to 3 times if the response is malformed
- ✅ App keeps running if the AI is unavailable — lesson loop does not crash
- ✅ Ambiguous runtime errors (NameError, TypeError, AttributeError) removed from the static hint map — AI handles these since the cause varies too much for a single fixed message
- [ ] **Hints for wrong answers** — when code runs fine but gives the wrong output or wrong variable value, the AI receives the error but was not trained on these cases. Needs dedicated training examples where the hint guides toward a logic mistake rather than an exception.
- [ ] **Expand model training data** — known gaps in the current 555-example dataset: trailing comma creating tuples, stray brackets in unusual positions. Need new training examples before these are handled reliably.

---

## Lessons & Curriculum

- ✅ Validator supports: `variable_check`, `output_check`, `type_check`, `source_check`, `collection_check`
- ✅ Multiple validation rules per lesson (all must pass)
- ✅ Type mismatch detection — tells the student when they used the wrong data type
- ✅ Float-numbered lesson files so new lessons insert anywhere without renaming
- ✅ Lessons without a `task` field auto-advance (reading/intro lessons)
- [ ] **Hello World lesson** — the very first lesson should be a simple `print("Hello, World!")` task to confirm setup is working and ease beginners in.
- [ ] **Write the full beginner curriculum** — current lessons are functional placeholders. Needed: While Loops, Functions, Dictionaries, String Methods, and more.
- [ ] **Multi-step lessons** — walk through a concept in 2-3 connected tasks within one lesson.
- [ ] **Nested data checks** — `collection_check` cannot currently verify inside nested structures (e.g. a list of dicts).
- [ ] **Function testing** — run the student's function against multiple hidden test inputs to verify it works generally, not just for one case.
- [ ] **Automated lesson tests** — test suite for `validator_test.py` so lesson authors can confirm rules work before publishing.

---

## Setup & Distribution

- ✅ `start.bat` sets up a Python virtual environment automatically
- ✅ Dependencies installed and updated automatically when `requirements.txt` changes (MD5 hash check)
- ✅ Ollama installed and launched automatically if not running
- ✅ Modelfile downloaded automatically from HuggingFace if missing
- ✅ AI model downloaded automatically on first run with a progress bar
- ✅ Model update check on launch — user is prompted if a newer version is available; old files cleaned up automatically
- ✅ No manual terminal commands required from the user
- [ ] **`.gitignore` audit** — confirm `*.gguf`, `model/`, `user_progress.json`, `user_workspace.py`, `__pycache__/`, `.venv/` are all excluded.
- [ ] **One-click installer** — bundle Python, the app, and the model into a single `.exe`. Only once the app is fully stable.