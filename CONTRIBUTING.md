# Contributing to PyFyve

PyFyve is currently a solo project by one developer. This document exists to establish good habits, keep the codebase consistent, and make it easier to onboard contributors later.

---

## Project Philosophy

Before contributing anything, understand the core constraint: **the AI hints must never give the answer.**

Every feature, prompt change, validation rule, and lesson must be evaluated against this. If a change makes the app more convenient by reducing the student's need to think, it is the wrong change.

---

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/pyfyve.git`
3. Create a branch for your change: `git checkout -b fix/validator-type-mismatch`
4. Make your changes
5. Test manually against the app
6. Commit with a clear message (see below)
7. Push and open a pull request against `main`

---

## Branch Naming

Use a short prefix that describes the type of change:

| Prefix | Use for |
|--------|---------|
| `fix/` | Bug fixes |
| `feat/` | New features |
| `lesson/` | New or updated lesson JSON files |
| `docs/` | README, CONTRIBUTING, comments |
| `refactor/` | Code restructuring with no behaviour change |
| `pipeline/` | Dataset generation, training scripts |

Examples:
```
fix/raw-err-str-format
feat/process-watchdog
lesson/variables-assignment
docs/update-readme-limitations
```

---

## Commit Messages

Follow this format:

```
type: short description in present tense

Optional body explaining why, not what. The diff shows what.
Reference issues with #number if applicable.
```

**Types:** `fix`, `feat`, `docs`, `refactor`, `lesson`, `pipeline`, `test`

Good examples:
```
fix: raw_err_str format now matches training data for syntax errors
feat: add search_str field to separate AI input from search URL
docs: add limitations section to README
lesson: add variables and assignment lesson with variable_check
refactor: extract offending line logic into helper function
```

Bad examples:
```
fixed stuff
update
wip
changes to user_code
```

**Why this matters:** commit messages are the changelog. When something breaks three months from now, a good commit history tells you exactly what changed and why. Treat each message as a note to your future self.

---

## What Belongs in a Commit

**One logical change per commit.** Not one file, not one session — one logical unit.

If you fix a bug in `user_code.py` and also update the README to document it, that is fine as one commit. If you fix two unrelated bugs, that is two commits.

This is not bureaucracy. Small, focused commits make it easy to revert a specific change without undoing unrelated work.

---

## Files That Should Never Be Committed

Make sure these are in `.gitignore`:

```
# Model and training data
*.gguf
*.jsonl
dataset_*.json

# User state (generated at runtime)
user_workspace.py
user_progress.json

# Python
__pycache__/
*.pyc
*.pyo
venv/
.env

# OS
.DS_Store
Thumbs.db
```

The GGUF model file is large (2-4GB). It does not belong in git. Distribute via releases or a separate download link.

---

## Adding Lessons

Lessons live in `lessons/` as numbered JSON files (`01.0_variables.json`, `02.0_strings.json`). Numbering uses floats so intermediate lessons can be inserted without renaming (`02.5_string_methods.json` fits between 2 and 3).

Every lesson must have:
- A clear, single-concept `task`
- At least one `validation` rule that actually tests what the task asked for
- A `common_errors` field that warns about the most likely mistake

Test your lesson manually before committing:
1. Complete the task correctly — it should pass
2. Make the described common error — it should fail with a clear message
3. Make a type mistake (string instead of int) — the validator should catch it

Do not write lessons that can be gamed by hardcoding the expected output. If `output_check` expects `"Hello"`, use `source_check` too to verify they used the right construct.

---

## Changing the AI Prompt

The few-shot examples in `ai_response.py` and `hint_generator.py` are load-bearing. They are the primary mechanism keeping the model's output Socratic. Changes here have outsized effects.

If you modify the prompt:
1. Run the full verify suite (`verify_beginner_hint.py`, `verify_intermediate_hint.py`) before and after
2. Document what changed and why in the commit message body
3. Note any tests that regressed

Do not remove the few-shot examples. Do not reduce their count. If you want to test without them, do it on a branch.

---

## Changing `user_code.py`

The `raw_err_str` field is the string passed to the AI. Its format must exactly match the training data:

- Syntax: `"Syntax Error in line N: <msg>"`
- Runtime: `"ErrorType on line: N: <message>"`

If you change this format, the model's hint quality will silently degrade. Any change to `raw_err_str` formatting requires a comment explaining the format and why it matches training data.

---

## Pull Requests

For now, PRs are low-ceremony. Just make sure:

- The app still runs end-to-end after your change
- You haven't accidentally committed `user_progress.json` or any `.jsonl` data files
- The commit message is clear
- If you changed prompt logic, you ran the verify suite

There is no CI yet. That is coming once the pytest suite exists.

---

## Questions

Open an issue. If the question is about the AI model, dataset, or fine-tuning specifics, reference the handoff document in `docs/` — it contains the complete technical history of training decisions.
