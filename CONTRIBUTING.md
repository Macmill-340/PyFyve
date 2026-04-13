# Contributing to PyFyve

PyFyve is currently a solo project. This document exists so that when contributions happen, they're consistent and the codebase stays clean.

---

## The One Rule That Overrides Everything

**The AI hint must never give the answer.**

Every feature, lesson, and code change should be evaluated against this. If a change makes the app more convenient by reducing the student's need to think, it's probably the wrong change.

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
fix: validator now fails loudly for unknown rule types instead of passing silently
feat: add download prompt for missing model file in setup.py
lesson: add string methods lesson with source_check
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

# Runtime-generated files
user_workspace.py
user_progress.json

# Python
__pycache__/
*.pyc
.venv/
.env

# OS
.DS_Store
Thumbs.db
```

The GGUF model file is ~2.6 GB and must not go in git. It is distributed via the auto-download in `setup.py`.

---

## Adding Lessons

Lessons live in `lessons/` as numbered JSON files. Use float numbering (`01.0`, `02.0`, `02.5`) so you can insert lessons between existing ones without renaming everything.

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

## Changing the AI Prompt

The few-shot examples in `ai_response.py` are what keep the model's output Socratic. Changes here have outsized effects.

If you change the prompt:
1. Test it manually across at least 5 different error types before committing
2. Document what changed and why in the commit message body
3. Do not remove or reduce the number of few-shot examples

---

## Changing `user_code.py`

The `raw_err_str` field is the string passed to the AI. Its format must match what the model was trained on:

- Syntax errors: `"Syntax Error in line N: <message>"`
- Runtime errors: `"ErrorType on line: N: <message>"`

If you change this format, the model's hint quality will silently degrade. Any change to `raw_err_str` requires a comment explaining why the format is what it is.

---

## Pull Requests

Make sure:
- The app runs end-to-end after your change
- You haven't committed `user_progress.json`, `user_workspace.py`, or any `.gguf` file
- If you changed prompt logic, you tested it manually across multiple error types
- The commit message is clear

---

## Questions

Open an issue. If it's about the AI model or hint quality, describe the specific error type and what you observed.
