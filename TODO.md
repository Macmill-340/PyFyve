# PyFyve: Project Roadmap

## ⚙️ Core Engine & Security
- [x] Basic Execution Sandbox (using `exec()` and `redirect_stdout`).
- [x] Security Blacklist (Static string checking).
- [x] Security Whitelist (Runtime restriction of `__builtins__`).
- [x] Implement AST (Abstract Syntax Tree) parsing to block forbidden nodes (`import`, `eval`).
- [x] Fix `raw_err_str` format for syntax errors — must be `"Syntax Error in line N: <msg>"` to match training data (was passing bare `se.msg`).
- [x] Fix `raw_err_str` format for runtime errors — must be `"ErrorType on line: N: <message>"` to match training data (was passing bare `str(e)`).
- [x] Separate `search_str` from `raw_err_str` — search URL includes error + offending line of code for better Google/AI search results; `raw_err_str` stays clean for the AI model.
- [ ] **AST Source Check:** Upgrade `source_check` to use AST parsing (Verify logic structure like `ast.For`, ignore comments/strings).
- [ ] **Modular Whitelists:** Dynamically allow specific modules (e.g., `math`, `random`) based on lesson requirements.
- [ ] **Process Watchdog:** Add a timer/multiprocessing limit to kill infinite loops in user code — a bare `while True: pass` currently hangs the app with no recovery.

## 🖥️ User Experience (UX) & Editor
- [x] Implement Notepad++ access for taking inputs on Windows.
- [x] Add standardized error messages for common beginner syntax mistakes.
- [x] Integrate browser search link for non-standardized errors (includes offending code line for better search results).
- [ ] **Strip Linux/Mac dead code:** Remove the untested `nano` fallback from `user_code.py`. Windows-only is the honest current state; cross-platform comes later as a real tested feature.
- [ ] **Cross-Platform Support:** Add Linux and Mac support properly (Nano, TextEdit, or `$EDITOR`) — only after Windows version is stable and shipped.
- [ ] **Rich UI:** Use the `rich` library to enhance terminal UI/UX (colours, panels, syntax highlighting).
- [ ] **Refactor Validator Returns:** Change `validator_test.py` to return `(status, message)` tuples instead of printing directly to console — required before the pytest suite can test output properly.

## 🧠 AI & Data Pipeline
- [x] Generate 555 high-quality Socratic examples using Qwen3 30B-A3B teacher model.
- [x] Build data hygiene scripts (`fix_data_user.py`, `shuffle.py`).
- [x] Build quality validation in `hint_generator.py` with `validate_hint_quality()`.
- [x] Fine-tune Qwen3 4B with QLoRA via Unsloth on Colab T4.
- [x] Local LLM inference via Ollama.
- [x] Few-shot examples anchored in `ai_response.py` at inference time (confirmed necessary — model reverts to answer-giving without them).
- [ ] **Phase 2 Logical Error Hints:** When code runs without exceptions but validation fails (wrong value, wrong output), fire a second AI path that receives expected vs actual result and guides Socratically. Requires separate prompt design and its own training data — distinct from the exception-based hint system.
- [ ] **Expand `validate_hint_quality()` Semantic Checks:** Currently only covers `str.append → list conversion` and `unmatched ) → add vs remove` cases. Extend as new error types are trained on.
- [ ] **Native Inference:** Migrate from Ollama to `llama-cpp-python` to remove third-party app dependency for end-users.
- [ ] **Pipeline Cleanup:** Move all dataset and training scripts to a dedicated `data_pipeline/` subfolder with a README documenting the full pipeline stages (staging → hint generation → merge → shuffle → verify → train).

## 🎓 Curriculum & Validation
- [x] Implement `validator_test.py` (variable, output, type, source, collection checks).
- [x] Multi-type checks (multiple validation rules per lesson).
- [x] `variable_check` with type mismatch detection (prints specific message for int vs str etc.).
- [x] `output_check` with `.strip()` on both sides.
- [x] `type_check` using `isinstance`.
- [x] `collection_check` for lists and dicts (size, type, contents).
- [x] Add `author` field to lesson JSON schema for contribution tracking and future lesson pack segregation.
- [ ] **Write Real Lessons:** Current lesson set is placeholder only. Need minimum 10 lessons covering Variables → Strings → Conditionals → Loops → Functions before the app is demonstrable.
- [ ] **Nested Data Checks:** Drill into complex structures (e.g. check `users[1]["name"] == "Alice"`).
- [ ] **Function Unit Testing:** Hidden test cases run against student's function (e.g. FizzBuzz checked against multiple inputs).
- [ ] **Multi-Task Lessons:** Step-by-step progression through multiple tasks within a single lesson file.
- [ ] **Test Suite:** Write `test_validator.py` — automated pytest suite for all validation types. Prerequisite: refactor validator returns to tuples first.

## 💾 State Management
- [x] Session progress saved/loaded via `user_progress.json`.
- [x] Lessons dynamically loaded from `lessons/*.json`.
- [x] Float-based lesson file sorting (`01.0`, `02.5` etc.) for inserting intermediate lessons without renaming.

## 📦 Product & Distribution
- [x] Licence decided: AGPL-3.0 for app and pipeline code (attribution required, modifications must be open); CC BY-NC-SA 4.0 for fine-tuned model weights (non-commercial, attribution, share-alike). Base model is Qwen3 4B under Qianwen Licence — read it before distributing.
- [ ] **Model Distribution via GitHub Releases:** Attach GGUF as a GitHub Release asset (not in git history — git cannot handle 3GB files). Update `start.bat` to auto-download the GGUF on first run using PowerShell `Invoke-WebRequest` if `models/fyve-ai.gguf` does not exist. Add `models/` to `.gitignore` and a `models/.gitkeep` to keep the folder in the repo so path assumptions hold.
- [ ] **Robust `start.bat` and `setup.py`:** Add exception handling for every failure point in the batch script and setup — Ollama not installed, model file missing, model not registered, Ollama service not running. Instead of crashing `main.py`, these should print a clear human-readable message and either exit gracefully or continue with AI disabled. Currently a missing model silently breaks the hint system with no explanation to the user.
- [ ] **Graceful AI Degradation in `main.py`:** If Ollama is unavailable or the model fails to load, `main.py` should catch the exception, print "AI hints unavailable — continuing without hints", and keep the lesson loop running. The app should never crash because the AI is missing.
- [ ] **`models/` folder scaffolding:** Add `models/.gitkeep` to repo so the download path exists on fresh clone. Add `models/` to `.gitignore` so the GGUF is never accidentally committed.
- [ ] **`.gitignore`:** Add before first commit — must exclude `*.gguf`, `*.jsonl`, `user_workspace.py`, `user_progress.json`, `__pycache__/`, `venv/`, `.env`.
- [ ] **The "Escape Hatch":** 3-strike rule that offers to reveal the solution if the student is stuck.
- [ ] **Local Analytics:** Track time-to-completion and error frequencies in a hidden `stats.json` to identify poorly written lessons.
- [ ] **One-Click Installer:** PyInstaller or Nuitka to bundle Python environment + GGUF + scripts into a single `.exe` — only after app is stable and model distribution via HuggingFace is proven.
- [ ] **Dynamic Curriculum:** AI generates a valid `lesson.json` on the fly for topics not in the syllabus.
