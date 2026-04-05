import os
import sys
import subprocess
import shutil
import time
import urllib.request

# --- CONFIG ---
MODEL_NAME = "fyve-ai"
MODEL_FILE = os.path.join("Fyve AI", "Modelfile")
OLLAMA_TIMEOUT = 30  # seconds to wait for Ollama to come online after launch


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
    """Find the Ollama GUI tray app (distinct from the CLI ollama.exe)."""
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
        urllib.request.urlopen("http://127.0.0.1:11434", timeout=3)
        return True
    except OSError:
        return False


def launch_ollama_tray():
    """Launch the Ollama GUI tray app as a detached background process (no terminal window)."""
    app_exe = find_ollama_app()
    if app_exe:
        subprocess.Popen(
            [app_exe],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        return True

    # Fallback: tray app not found, run CLI serve silently
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
        # The installer sometimes auto-launches Ollama.
        # Either way, ensure_ollama_serving() will handle it from here — no restart needed.
    except Exception as e:
        print(f"[ EX ] Installation failed: {e}")
        print("       Please install Ollama manually from https://ollama.com")
        input("Press Enter to exit...")
        sys.exit(1)


def ensure_ollama_serving():
    print("[ .. ] Checking AI server status...")
    if is_ollama_online():
        print("[ OK ] AI server is online.")
        return

    print("[ .. ] Ollama is not running. Launching the tray app now...")
    if not launch_ollama_tray():
        print("[ EX ] Could not locate the Ollama application.")
        print("       Please start Ollama from the Start Menu and run start.bat again.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Poll instead of forcing the user to restart — no unnecessary rerun needed.
    print(f"[ .. ] Waiting for Ollama to come online (up to {OLLAMA_TIMEOUT}s) ", end="", flush=True)
    for _ in range(OLLAMA_TIMEOUT):
        time.sleep(1)
        print(".", end="", flush=True)
        if is_ollama_online():
            print()
            print("[ OK ] AI server is online.")
            return

    print()
    print("[ !! ] Ollama is taking longer than expected.")
    print("       Please ensure the Ollama icon appears in your system tray,")
    print("       then close this window and run start.bat again.")
    input("Press Enter to exit...")
    sys.exit(1)


def main():
    print("\n--- PyFyve AI Configuration ---")

    # 1. Ollama installed?
    exe = find_ollama_exe()
    if not exe:
        install_ollama()
        exe = find_ollama_exe()  # re-check after install (known path, no restart needed)
        if not exe:
            # Extremely rare: installer ran but exe still not at expected path
            print("[ EX ] Ollama was installed but the executable could not be located.")
            print("       Please close this window and run start.bat again.")
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("[ OK ] Ollama executable found.")

    # 2. Server running? (launches tray + polls if not — no restart needed)
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
                # No capture_output — let registration progress stream live to the terminal
                res = subprocess.run(
                    [exe, "create", MODEL_NAME, "-f", MODEL_FILE],
                    encoding="utf-8", errors="replace"
                )
                if res.returncode == 0:
                    print(f"[ OK ] Model '{MODEL_NAME}' registered.")
                else:
                    print(f"[ EX ] Registration failed.")
                    print("       Try running manually: ollama create fyve-ai -f \"Fyve AI/Modelfile\"")
            else:
                print(f"[ OK ] Model '{MODEL_NAME}' is ready.")
        except Exception as e:
            print(f"[ EX ] Could not verify model: {e}")
            print("       AI hints will be unavailable. The lesson loop will still work.")
    else:
        print(f"[ !! ] '{MODEL_FILE}' not found.")
        print("       Download fyve-ai.gguf from the releases page and place it in 'Fyve AI/'.")
        print("       AI hints will be unavailable until the model is set up.")

    # 4. Launch
    print("\n[ OK ] System initialization complete.")
    print("[ >> ] Launching PyFyve...")
    time.sleep(1)

    if os.path.exists("main.py"):
        subprocess.run([sys.executable, "main.py"])
    else:
        print("[ EX ] main.py not found. Check your installation.")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()