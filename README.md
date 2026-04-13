# PyFyve

A completely offline, free Python tutor that guides you toward the answer — without ever giving it to you.

---

## What It Does

PyFyve gives beginners a step-by-step Python curriculum with a built-in code editor. When you make a mistake, a locally-running AI model looks at your error and responds with exactly three sentences:

1. What specifically went wrong in your code
2. Which Python rule you violated
3. A question that points you in the right direction — without telling you the fix

No internet required once it's set up. No subscriptions. No data leaves your machine.

---

## Why It Works This Way

Most learning tools — AI assistants, tutorials, Stack Overflow — just show you the answer. That feels helpful in the moment, but it skips the part where actual learning happens: figuring it out yourself.

PyFyve uses the Socratic method. You get a diagnosis, a rule, and a nudge. You still have to make the connection. That struggle is the point.

---

## How It Works

```
You write code in the built-in Notepad++ editor
        ↓
Your code is run safely in a sandbox
        ↓
A validator checks if you completed the task correctly
        ↓
On failure: the error is classified and the AI generates a 3-line hint
        ↓
The hint appears in the terminal, one character at a time
```

---

## Setup

> **Windows only.** Linux and Mac are not supported in this version.

**What you need first:**
- Python 3.13 ([python.org](https://python.org))
- [Ollama](https://ollama.com) — the app that runs the AI locally

**Steps:**

1. Download or clone this repository
2. Double-click **start.bat**
3. The script handles everything automatically:
   - Creates a Python virtual environment
   - Installs required libraries
   - Checks if Ollama is installed and running
   - Offers to download the AI model if it's not present (~2.6 GB, one-time)
   - Launches PyFyve

On every run after the first, `start.bat` is fast — it only redoes steps that actually need doing.

---

## Project Structure

```
PyFyve/
├── start.bat
├── setup.py
├── requirements.txt
├── src/ ← all Python code lives here
│ ├── main.py
│ ├── ai_response.py
│ ├── console.py
│ ├── validator_test.py
│ ├── user_code.py
│ ├── load_lessons.py
│ └── load_progress.py
├── lessons/ ← lesson JSON files
└── models/ ← downloaded on first run (ignored by git)
```

---

## Lesson Format

Each lesson is a JSON file in `lessons/`:

```json
{
  "id": 1,
  "topic": "Variables & Assignment",
  "text": "A variable is a named container for a value...",
  "common_errors": "Writing 100 = score instead of score = 100.",
  "task": "Create a variable called score and assign it the value 100.",
  "validation": [
    {"type": "variable_check", "var_info": {"score": 100}}
  ]
}
```

**Supported check types:**
- `variable_check` — checks that variables exist with the right names and values
- `output_check` — checks what your code prints
- `type_check` — checks the data type of a variable (int, str, list, etc.)
- `source_check` — checks that you used a specific keyword or method
- `collection_check` — checks lists and dictionaries for size and contents

---

## The AI Model

The AI that powers PyFyve's hints is a custom fine-tuned model built specifically for this one job: reading a Python error and responding with a Socratic 3-sentence hint. It does not know how to do anything else — it cannot give you the answer, explain concepts freely, or write code for you. That's intentional.

The model runs entirely on your machine through Ollama. No internet connection is needed after the initial download.

---

## Limitations

**Please read these before using PyFyve. This is a prototype and an honest accounting of what it can and cannot do.**

**Windows only**
Linux and Mac are not supported. The editor integration uses a bundled Notepad++ (with Notepad as a fallback), which is Windows-specific. Cross-platform support is planned but not yet built.

**This is a prototype**
PyFyve is early-stage software built by one developer. Expect rough edges. The goal right now is to validate the core concept — Socratic AI hints for Python beginners — before expanding the feature set.

**The lessons are placeholders**
The included lessons cover the basic curriculum and are functional, but they are not the final curriculum. They exist to demonstrate the system and are suitable for light use and testing. A more comprehensive set of lessons with harder tasks and better progression is in development.

**The AI model has real limits**
The model was trained on 555 examples of specific, well-defined Python errors — syntax errors, NameErrors, TypeErrors, IndexErrors, and similar common mistakes. It performs well on what it was trained on. Outside that, it may produce hints that are directionally reasonable but not precisely correct. Specific known limitations:

- **Trailing comma on assignment** — writing `x = 90,` creates a tuple in Python, not an integer. The model has never seen this pattern and may give a vague or slightly inaccurate hint.
- **Wrong value without an error** — when your code runs without crashing but produces the wrong value (e.g. assigning the right variable name but wrong number), the AI fires but was not trained on these cases. It may still help, but it is not reliable here.
- **Unusual punctuation errors** — stray commas, extra brackets in unusual positions, or other uncommon syntax mistakes may confuse the model.

**No infinite loop protection**
If you write `while True: pass` or any other infinite loop, the app will freeze with no way out except closing the terminal window. This is a known issue being worked on.

**No hints for logic errors**
The AI only fires when Python raises an actual exception. If your code runs without errors but does the wrong thing — calculates the wrong answer, prints the wrong text — validation will fail but the AI cannot help. It has no way to know what your code was supposed to do.

---

## Roadmap

See [TODO.md](TODO.md) for the full list.

**What's coming next:**
- Infinite loop timeout
- AI hints for wrong answers (not just errors)
- More lessons covering Strings, Conditionals, Loops, and Functions
- Cross-platform editor support

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache 2.0