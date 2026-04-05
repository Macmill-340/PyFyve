import os
import sys
import subprocess
import shutil
import time
import urllib.request

# --- CONFIG ---
MODEL_NAME = "fyve-ai"
MODEL_FILE = os.path.join("Fyve AI", "Modelfile")
OLLAMA_TIMEOUT = 30


def find_ollama_exe():
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return shutil.which("ollama")


def find_ollama_app():
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama app.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama app.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def is_ollama_online():
    try:
        urllib.request.urlopen("http://127.0.0.1:11434", timeout=1)
        return True
    except Exception:
        return False


def launch_ollama_tray():
    """Launch the Ollama GUI tray app as a detached background process."""
    app_exe = find_ollama_app()
    if app_exe:
        subprocess.Popen([app_exe],
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                         close_fds=True,
                         )
        return True

    # Fallback: run CLI serve silently
    cli_exe = find_ollama_exe()
    if cli_exe:
        subprocess.Popen(
            [cli_exe, "serve"],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    return False


def install_ollama():
    print("[ !! ] Ollama not found. Starting installation...")
    ps_cmd = 'powershell -ExecutionPolicy Bypass -Command "irm https://ollama.com/install.ps1 | iex"'
    try:
        subprocess.run(ps_cmd, shell=True, check=True)
        print("[ OK ] Ollama installation complete.")
        time.sleep(2)  # Give Windows file system time to catch up
    except Exception as e:
        print(f"[ EX ] Installation failed: {e}")
        print("       Please install Ollama manually from https://ollama.com")
        sys.exit(1)


def ensure_ollama_serving():
    print("[ .. ] Checking AI server status...")
    if is_ollama_online():
        print("[ OK ] AI server is online.")
        return

    print("[ .. ] Ollama is not running. Launching now...")
    if not launch_ollama_tray():
        print("[ EX ] Could not locate the Ollama application.")
        sys.exit(1)

    print(f"[ .. ] Waiting for Ollama to come online ", end="", flush=True)
    for _ in range(OLLAMA_TIMEOUT):
        time.sleep(1)
        print(".", end="", flush=True)
        if is_ollama_online():
            print("\n[ OK ] AI server is online.")
            return

    print("\n[ EX ] Timeout waiting for Ollama to start.")
    print("       Please start Ollama manually from the Start Menu and try again.")
    sys.exit(1)


def main():
    print("\n--- PyFyve AI Configuration ---")

    # 1. Check Install
    exe = find_ollama_exe()
    if not exe:
        install_ollama()
        exe = find_ollama_exe()
        if not exe:
            print("[ EX ] Ollama installed but executable not found. Please restart.")
            sys.exit(1)
    else:
        print("[ OK ] Ollama executable found.")

    # 2. Start Server
    ensure_ollama_serving()

    # 3. Model check
    if os.path.exists(MODEL_FILE):
        print(f"[ .. ] Verifying model: {MODEL_NAME}")
        try:
            check = subprocess.run(
                [exe, "list"],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=10
            )
            if MODEL_NAME not in check.stdout:
                print(f"[ .. ] Registering {MODEL_NAME} (this may take a moment)...")

                # Claude's Fix: No capture_output so user sees the progress bar
                res = subprocess.run([exe, "create", MODEL_NAME, "-f", MODEL_FILE],
                                     encoding="utf-8", errors="replace"
                                     )
                if res.returncode == 0:
                    print(f"[ OK ] Model '{MODEL_NAME}' registered.")
                else:
                    print(f"[ EX ] Registration failed.")
            else:
                print(f"[ OK ] Model '{MODEL_NAME}' is ready.")
        except Exception as e:
            print(f"[ EX ] Could not verify model: {e}")
    else:
        print(f"[ !! ] '{MODEL_FILE}' not found. AI hints disabled.")

    # 4. Launch
    print("\n[ OK ] System initialization complete.")
    print("[ >> ] Launching PyFyve...\n")
    time.sleep(1)

    if os.path.exists("main.py"):
        result = subprocess.run([sys.executable, "main.py"])
        sys.exit(result.returncode)
    else:
        print("[ EX ] main.py not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()