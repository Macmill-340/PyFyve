# Contributing to PyFyve

PyFyve is currently a solo project. This document exists so that when contributions happen, they're consistent and the codebase stays clean.

---

## The One Rule That Overrides Everything

**The AI hint must never give the answer.**

Every feature, lesson, and code change should be evaluated against this. If a change makes the app more convenient by reducing the student's need to think, it's probably the wrong change.

---

## A Note on AI-Generated Code

You are welcome to use AI assistants (Copilot, Claude, ChatGPT) to help write your pull requests, but **you must fully understand every line of code you submit.**

This codebase relies on a strict, deterministic state machine and a highly specific AST-parsing sandbox. AI models often try to "helpfully" over-engineer these systems, refactor them into non-deterministic loops, or introduce subtle bugs that are a nightmare to debug. 

If you use AI to "vibe-code" a feature without understanding the underlying architecture, it might break the app. If you submit a PR containing AI-generated code that you cannot explain or debug yourself, it will be rejected. 

If an AI wrote it, you still own it. Test it thoroughly.

---

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a branch: `git checkout -b fix/what-you-are-fixing`
4. Make your changes
5. Test end-to-end: run `start.bat`, go through at least one lesson
6. Commit with a clear message
7. Push and open a pull request against `main`

---

## Branch Naming

| Prefix | Use for |
|--------|---------|
| `fix/` | Bug fixes |
| `feat/` | New features |
| `lesson/` | New or updated lesson files |
| `docs/` | README, CONTRIBUTING, comments |
| `refactor/` | Code restructuring with no behaviour change |

---

## Commit Messages

```
type: short description in present tense

Optional body — explain why, not what. The diff shows what.
```

**Types:** `fix`, `feat`, `docs`, `refactor`, `lesson`, `test`

Good:
```
fix: recover gracefully when code separator is missing from workspace file
fix: pass markup=False to console.print for user code and output display
feat: add input() and infinite loop warnings to limitations banner
lesson: add hello world lesson with output_check
```

Bad:
```
update
wip
changes
```

---

## What Belongs in a Commit

One logical change per commit. Fixing a bug in `user_code.py` and updating the README to document it is one commit. Fixing two unrelated bugs is two commits.

---

## Files That Should Never Be Committed

```
# Model files
*.gguf
model/

# Runtime-generated files
user_workspace.py
user_progress.json

# Python
__pycache__/
*.pyc
.venv/
.env

# Installer
installer_output/
*.exe

# OS
.DS_Store
Thumbs.db
```

The GGUF model file is ~2.6 GB and must not go in git. It is distributed via the auto-download in `setup.py`.

---

## Adding Lessons

Lessons live in `lessons/` as numbered JSON files. Use this convention (`1_0`, `2_0`, `3_0`) so you can insert lessons between existing ones without renaming everything.

Every lesson must have:
- A single, clearly stated `task`
- At least one `validation` rule that tests what the task actually asked for
- A `common_errors` field describing the most likely mistake

**Test your lesson before committing:**
1. Complete the task correctly — it should pass
2. Make the common error described — it should fail with a clear message
3. Do something plausible but wrong — it should also fail

Don't write tasks that can be passed by hardcoding the expected output. If `output_check` expects `"Hello"`, add a `source_check` too that verifies the student used the right construct.

---

## Changing `user_code.py`

### The `raw_err_str` format

The `raw_err_str` field is the string passed to the AI. Its format must match what the model was trained on:

- Syntax errors: `"Syntax Error in line N: <message>"`
- Runtime errors: `"ErrorType on line: N: <message>"`

If you change this format, hint quality will silently degrade. Any change to `raw_err_str` requires a comment explaining the format.

### The `markup=False` requirement

When displaying student code or execution output with `console.print()`, always pass `markup=False`. Without it, Rich interprets brackets in student code (list literals, dictionary keys, etc.) as markup tags and corrupts the display.

### The code separator

The workspace file is split on `# Write your code here:` to extract student code. If you rename this sentinel, update it consistently across `user_input()` and test that the recovery path (when the sentinel is missing) still works.

---

## Pull Requests

Make sure:
- The app runs end-to-end after your change
- You haven't committed `user_progress.json`, `user_workspace.py`, `model/`, or any `.gguf` file
- If you changed prompt logic, you tested it manually across multiple error types
- If you changed `console.print()` calls that display student output, you included `markup=False`
- The commit message is clear

---

## Questions

Open an issue. If it's about the AI model or hint quality, describe the specific error type and what you observed.
