# PyFyve

**A completely offline, free Python tutor that guides you toward the answer — without ever giving it to you.**

## What It Does

PyFyve gives beginners a step-by-step Python curriculum with a built-in code editor. When you make a mistake, a locally-running AI model looks at your error and responds with exactly three sentences:

1. What specifically went wrong in your code
2. Which Python rule you violated
3. A question that points you in the right direction — without telling you the fix

No internet required once it's set up. No subscriptions. No data leaves your machine.

## Why It Works This Way

PyFyve uses the Socratic method. You get a diagnosis, a rule, and a nudge. You still have to make the connection. That struggle is the point.

## How It Works

You write code in the built-in Notepad++ editor
        ↓
Your code is run safely in a sandbox
        ↓
A validator checks if you completed the task correctly
        ↓
On failure: the error is classified and the AI generates a 3-line hint
        ↓
The hint appears in the terminal, one character at a time

## Setup

> **Windows only.** Linux and Mac are not supported in this version.

**What you need first:**
* Python 3.13
* Ollama — the app that runs the AI locally

**Steps:**
1. Download or clone this repository
2. Double-click `start.bat` — that's it

`start.bat` handles everything automatically:
* Creates a Python virtual environment
* Installs required libraries
* Checks if Ollama is installed and running (installs it if not)
* Offers to download the AI model if it's not present (~2.6 GB, one-time)
* Launches PyFyve

> **Note:** Keep `start.bat` in the project root folder and always launch PyFyve by double-clicking it. Do not run `main.py` directly.

## Project Structure

PyFyve/
├── start.bat               ← Launch PyFyve by double-clicking this
├── setup.py                ← Environment checks, Ollama + model setup
├── requirements.txt
├── src/                    ← All Python source files
│   ├── main.py             ← Lesson loop and entry point
│   ├── ai_response.py      ← AI hint generation via Ollama
│   ├── console.py          ← Rich terminal theme and shared UI helpers
│   ├── validator_test.py   ← Lesson validation rules
│   ├── user_code.py        ← Editor integration, sandboxed execution
│   ├── load_lessons.py     ← Load and display lesson JSON
│   └── load_progress.py    ← Save and restore lesson progress
├── lessons/                ← Lesson JSON files (numbered, e.g. 01.0_intro.json)
├── model/                  ← AI model files — downloaded on first run (git-ignored)
└── npp/                    ← Bundled Notepad++ editor (Windows)

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

**Supported validation types:**
* `variable_check` — variables exist with the right names and values
* `output_check` — checks what your code prints
* `type_check` — checks the data type of a variable (int, str, list, etc.)
* `source_check` — checks that you used a specific keyword or method
* `collection_check` — checks lists and dicts for type, size, and contents

## The AI Model

The AI that powers PyFyve's hints is a custom fine-tuned model built for exactly one job: reading a Python error and responding with a Socratic 3-sentence hint. It cannot give you the answer, explain concepts freely, or write code for you. That's intentional.

The model runs entirely on your machine through Ollama. No internet connection is needed after the initial download.

## Current Limitations

**Windows only**: Linux and Mac are not supported. The editor integration uses a bundled Notepad++ (with Notepad as a fallback), which is Windows-specific.

**Infinite loops**: If you write `while True: pass` or any other infinite loop, the app will freeze with no recovery. Avoid `while True` in your code.

**`input()` is not supported**: Code that calls `input()` will fail with an error.

**AI hint coverage**: The model was trained on specific Python errors. It handles common syntax and runtime errors well. Logic errors (where code runs without crashing but produces the wrong result) currently don't trigger AI hints.

## Roadmap

See [TODO.md](/Macmill-340/PyFyve/blob/main/TODO.md) for the full list. Key items coming next:
* Infinite loop timeout protection
* AI hints for wrong answers (not just exceptions)
* Full beginner curriculum (While Loops, Functions, Dictionaries)
* Cross-platform editor support

## License

Apache 2.0

## Related Documentation
* [CONTRIBUTING.md](/Macmill-340/PyFyve/blob/main/CONTRIBUTING.md)
* [TODO.md](/Macmill-340/PyFyve/blob/main/TODO.md)
* [LICENSE.md](/Macmill-340/PyFyve/blob/main/LICENSE.md)

## Dependencies
* Python 3.13
* Ollama (local AI runtime)
* Rich (terminal UI)
* Other libraries specified in requirements.txt
