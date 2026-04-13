# PyFyve — Roadmap

Items marked ✅ are done. Everything else is planned or in progress.

---

## Safety & Sandboxing

- ✅ Code runs in a sandbox — it cannot touch the file system or run system commands
- ✅ Forbidden functions (`eval`, `exec`, `open`, `__import__`) blocked before running
- ✅ Forbidden imports (`os`, `sys`, `subprocess`, etc.) blocked
- ✅ Output captured cleanly without affecting the rest of the app
- [ ] **Infinite loop timeout** — a `while True: pass` freezes the app with no way out. Need a background timer that kills runaway code after a few seconds and returns a clean error message.
- [ ] **Smarter source checking** — `source_check` currently looks for a keyword anywhere in the code as plain text, so it can be fooled by a comment. Upgrade to check actual code structure so only real usage counts.
- [ ] **Per-lesson module access** — some lessons will need `math`, `random`, etc. Add a way for a lesson to specify which extra modules are allowed, and unlock only those for that lesson.

---

## Editor & User Experience

- ✅ Bundled Notepad++ editor on Windows
- ✅ Notepad fallback if bundled editor is missing
- ✅ Linux/Mac dead code removed — Windows-only is the honest current state
- ✅ Friendly error messages for the most common beginner mistakes
- ✅ Search link for unusual errors (includes the offending line for better results)
- ✅ Terminal resizes to a comfortable width on launch
- ✅ Screen clears when the lesson loop starts — no setup noise visible during lessons
- ✅ Restart-from-scratch option after completing all lessons
- [ ] **Cross-platform support** — proper Linux and Mac editor integration, tested end-to-end. Only after Windows is stable.
- [ ] **Colour and formatting** — use the `rich` library for coloured headings, bordered lesson panels, and cleaner output overall.
- [ ] **Escape hatch (3-strike rule)** — after failing the same task 3 times, offer to reveal the solution. Being completely stuck with no way forward is worse than seeing an answer once.
- [ ] **Multiple tasks in one lesson** — right now each lesson has one task. Add support for a `tasks` array so a lesson can walk through a concept in 2-3 connected steps before moving on. Requires changes to the validator loop in `main.py` and the lesson JSON schema.
- [ ] **Practice exercise mode** — a separate mode accessible from the main menu, distinct from lessons. Exercises are harder, have no tutorial text, and test the same concepts with less hand-holding. Uses a separate `exercises/` folder with the same JSON format. No progress saved — pure practice.
- [ ] **Solution reveal block** — lessons and exercises can optionally include a `"solution"` field in the JSON that is only shown after the escape hatch triggers or enough failed attempts. Never displayed during normal play.
- [ ] **Better source_check failure messages** — the current message ("It is suspected you are not using the methods...") is too generic and often misleading. The message should reflect the actual requirement that failed, not imply a general method-usage issue.
- [ ] **Fresh Notepad++ portable** — replace the current bundled npp.exe with a clean portable build with dark mode enabled as the only non-default setting.

---

## AI Hints

- ✅ AI fires on Python errors and streams the hint one character at a time
- ✅ Hint is always exactly 3 sentences: what went wrong, which rule was broken, a guiding question
- ✅ AI retries up to 3 times if the response is malformed
- ✅ App keeps running if the AI is unavailable — the lesson loop does not crash
- ✅ Ambiguous runtime errors (NameError, TypeError) removed from static hint map — AI handles these since the cause varies too much for a single fixed message
- [ ] **Hints for wrong answers** — when code runs fine but gives the wrong output or wrong variable value, the AI fires but was not trained on these cases. Needs a dedicated training path: a second set of examples where the error is a wrong value or wrong output, and the hint guides toward the logic mistake. This is the next major AI feature.
- [ ] **Expand model training data** — known gaps in the current 555-example dataset: trailing comma creating tuples, stray brackets in unusual positions, uncommon punctuation errors. These need new training examples before the model handles them reliably.
- [ ] **Remove Ollama dependency** — long-term goal is to run the AI as a Python library directly, with no external app required.

---

## Lessons & Curriculum

- ✅ Validator supports: variable check, output check, type check, source check, collection check
- ✅ Multiple validation rules per lesson (all must pass)
- ✅ Type mismatch detection — tells the student when they used the wrong data type
- ✅ Float-numbered lesson files so new lessons can be inserted anywhere without renaming
- ✅ Lessons without a task (intro/reading lessons) are supported and auto-advance
- [ ] **Write the full beginner curriculum** — current lessons are functional placeholders. Need: While Loops, Functions, Dictionaries, and more before the curriculum is complete.
- [ ] **Multi-step lessons** — walk through a concept in 2-3 connected tasks within one lesson before moving on. Blocked on the multiple tasks UX work above.
- [ ] **Nested data checks** — validator currently can't check inside nested structures like a list of dictionaries.
- [ ] **Function testing** — run the student's function against multiple hidden test inputs to check it works generally, not just for one case.
- [ ] **Automated lesson tests** — write a test suite for `validator_test.py` so lesson authors can confirm their validation rules work before publishing.

---

## Setup & Distribution

- ✅ `start.bat` sets up a Python virtual environment automatically
- ✅ Dependencies installed and updated automatically when `requirements.txt` changes
- ✅ Ollama installed and launched automatically if not running
- ✅ Modelfile downloaded automatically from HuggingFace if missing — model folder not required in repository
- ✅ AI model downloaded automatically on first run if not found (with progress bar)
- ✅ Model update check on launch — if a newer version is on HuggingFace and internet is available, user is prompted to update; old model and GGUF cleaned up automatically
- ✅ No manual terminal commands required from the user
- [ ] **`.gitignore` audit** — confirm `*.gguf`, `model/`, `user_progress.json`, `user_workspace.py`, `__pycache__/`, `.venv/` are all excluded.
- [ ] **Local session stats** — track attempts per lesson and most common errors, saved quietly to `stats.json`. Useful for spotting poorly written lessons.
- [ ] **One-click installer** — bundle Python, the app, and the model into a single `.exe`. Only once the app is fully stable.