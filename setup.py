import os
import sys
import subprocess
import shutil
import time
import urllib.request

# --- CONFIG ---
MODEL_NAME     = "fyve-ai"
MODEL_DIR      = "model"
MODEL_FILE     = os.path.join(MODEL_DIR, "Modelfile")
GGUF_FILE      = os.path.join(MODEL_DIR, "fyve-ai.Q4_K_M.gguf")
VERSION_FILE   = os.path.join(MODEL_DIR, "version.txt")

GGUF_URL       = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "fyve-ai.Q4_K_M.gguf?download=true"
)
MODELFILE_URL  = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "Modelfile?download=true"
)
VERSION_URL    = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "version.txt?download=true"
)

GGUF_SIZE_HINT  = "~2.6 GB"
OLLAMA_TIMEOUT  = 30


# ── Ollama location helpers ────────────────────────────────────────────────────

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


# ── Ollama server helpers ──────────────────────────────────────────────────────

def is_ollama_online():
    try:
        urllib.request.urlopen("http://127.0.0.1:11434", timeout=3)
        return True
    except Exception:
        return False


def launch_ollama_tray():
    app_exe = find_ollama_app()
    if app_exe:
        subprocess.Popen(
            [app_exe],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        return True

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
        print("       Please start Ollama from the Start Menu and try again.")
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


# ── Download helpers ───────────────────────────────────────────────────────────

def download_file(url, dest_path, label):
    """Download a file with a live progress bar. Returns True on success."""
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            pct    = min(100.0, downloaded * 100.0 / total_size)
            filled = int(pct / 2)
            bar    = "#" * filled + "-" * (50 - filled)
            mb_done  = downloaded / (1024 * 1024)
            mb_total = total_size  / (1024 * 1024)
            print(f"\r[ .. ] [{bar}] {pct:5.1f}%  {mb_done:.0f}/{mb_total:.0f} MB",
                  end="", flush=True)
        else:
            mb_done = downloaded / (1024 * 1024)
            print(f"\r[ .. ] {mb_done:.1f} MB downloaded...", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, dest_path, show_progress)
        print(f"\n[ OK ] {label} downloaded.")
        return True
    except Exception as e:
        print(f"\n[ EX ] Download failed: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False


def get_remote_version():
    """Fetch the latest version string from HuggingFace. Returns None if offline."""
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as r:
            return r.read().decode().strip()
    except Exception:
        return None


def get_local_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return None


def save_local_version(version):
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(VERSION_FILE, "w") as f:
        f.write(version)


# ── Model helpers ──────────────────────────────────────────────────────────────

def unregister_model(exe):
    """Remove the model from Ollama's registry."""
    print(f"[ .. ] Removing old model from Ollama...")
    try:
        subprocess.run(
            [exe, "rm", MODEL_NAME],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=15
        )
        print(f"[ OK ] Old model removed from Ollama.")
    except Exception as e:
        print(f"[ !! ] Could not remove old model from Ollama: {e}")


def delete_gguf():
    """Delete the local GGUF file to free disk space."""
    if os.path.exists(GGUF_FILE):
        os.remove(GGUF_FILE)
        print("[ OK ] Old model file deleted.")


def register_model(exe):
    """Register the model with Ollama using the Modelfile. Returns True on success."""
    print(f"[ .. ] Registering {MODEL_NAME} with Ollama (this may take a moment)...")
    res = subprocess.run(
        [exe, "create", MODEL_NAME, "-f", MODEL_FILE],
        encoding="utf-8", errors="replace"
    )
    if res.returncode == 0:
        print(f"[ OK ] Model '{MODEL_NAME}' registered.")
        return True
    else:
        print(f"[ EX ] Registration failed.")
        print(f"       Try manually: ollama create {MODEL_NAME} -f \"{MODEL_FILE}\"")
        return False


def check_for_model_update(exe):
    """
    If internet is available, check if a newer model version exists.
    Update order (critical): unregister → delete GGUF → download Modelfile →
    download GGUF → register. This ensures we never register a partial update.
    If download fails at any point, the user is told AI hints are unavailable
    and the app continues without them.
    """
    print("[ .. ] Checking for model updates...")
    remote_version = get_remote_version()

    if remote_version is None:
        print("[ .. ] Offline or unreachable — skipping update check.")
        return

    local_version = get_local_version()

    if local_version == remote_version:
        print(f"[ OK ] Model is up to date (v{local_version}).")
        return

    if local_version:
        print(f"\n[ !! ] Model update available: v{local_version} → v{remote_version}")
    else:
        print(f"\n[ !! ] Model update available (v{remote_version}).")

    answer = input("       Download update now? (~2.6 GB, existing model will be replaced) [Y/n]: ").strip().lower()
    if answer not in ("", "y", "yes"):
        print("[ .. ] Skipping update. Continuing with current model.")
        return

    # Step 1: Remove old model from Ollama FIRST (before touching files)
    unregister_model(exe)

    # Step 2: Delete old GGUF to free space
    delete_gguf()

    # Step 3: Download fresh Modelfile (covers Modelfile changes too)
    print("[ .. ] Downloading updated Modelfile...")
    if not download_file(MODELFILE_URL, MODEL_FILE, "Modelfile"):
        print("[ EX ] Could not download updated Modelfile. AI hints will be unavailable.")
        return

    # Step 4: Download new GGUF
    if not download_file(GGUF_URL, GGUF_FILE, "AI model"):
        print("[ EX ] Model download failed. AI hints will be unavailable until next run.")
        return

    # Step 5: Register — only reached if both downloads succeeded
    if register_model(exe):
        save_local_version(remote_version)
        print(f"[ OK ] Model updated to v{remote_version}.")
    else:
        print("[ EX ] Registration failed after download. Try running start.bat again.")


def ensure_model_registered(exe):
    """
    Ensure the model is present and registered. Downloads Modelfile and GGUF
    from HuggingFace if either is missing. Checks for updates if already installed.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Ensure Modelfile exists
    if not os.path.exists(MODEL_FILE):
        print("[ .. ] Modelfile not found. Downloading...")
        if not download_file(MODELFILE_URL, MODEL_FILE, "Modelfile"):
            print("[ EX ] Could not download Modelfile. AI hints will be unavailable.")
            return

    print(f"[ .. ] Verifying model: {MODEL_NAME}")
    try:
        check = subprocess.run(
            [exe, "list"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=10
        )
    except Exception as e:
        print(f"[ EX ] Could not query Ollama: {e}")
        print("       AI hints will be unavailable. The lesson loop will still work.")
        return

    if MODEL_NAME in check.stdout:
        print(f"[ OK ] Model '{MODEL_NAME}' is ready.")
        # Already installed — check for updates
        check_for_model_update(exe)
        return

    # Not registered — need GGUF
    if not os.path.exists(GGUF_FILE):
        print(f"\n[ !! ] AI model file not found in '{MODEL_DIR}/'.")
        answer = input(f"       Download it now? ({GGUF_SIZE_HINT}, requires internet) [Y/n]: ").strip().lower()
        if answer in ("", "y", "yes"):
            if not download_file(GGUF_URL, GGUF_FILE, "AI model"):
                print("[ EX ] Download failed. AI hints will be unavailable.")
                return
        else:
            print("       Skipping. AI hints will be unavailable.")
            print("       https://huggingface.co/Macmill/qwen-finetune-v3")
            return

    if register_model(exe):
        remote_version = get_remote_version()
        if remote_version:
            save_local_version(remote_version)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    print("\n--- PyFyve Setup ---")

    exe = find_ollama_exe()
    if not exe:
        install_ollama()
        exe = find_ollama_exe()
        if not exe:
            print("[ EX ] Ollama installed but executable not found. Please restart.")
            sys.exit(1)
    else:
        print("[ OK ] Ollama executable found.")

    ensure_ollama_serving()
    ensure_model_registered(exe)

    print("\n[ OK ] Setup complete. Launching PyFyve...")
    time.sleep(1)

    if os.path.exists("src/main.py"):
        result = subprocess.run([sys.executable, "src/main.py"])
        sys.exit(result.returncode)
    else:
        print("[ EX ] main.py not found. Your installation may be incomplete.")
        sys.exit(1)


if __name__ == "__main__":
    main()