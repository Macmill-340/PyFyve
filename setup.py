import os
import sys
import ssl
import subprocess
import shutil
import time
import urllib.request

MODEL_NAME     = "fyve-ai"
MODEL_DIR      = "model"
MODEL_FILE     = os.path.join(MODEL_DIR, "Modelfile")
GGUF_FILE      = os.path.join(MODEL_DIR, "fyve-ai.Q4_K_M.gguf")
VERSION_FILE   = os.path.join(MODEL_DIR, "version.txt")

GGUF_URL      = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "fyve-ai.Q4_K_M.gguf?download=true"
)
MODELFILE_URL = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "Modelfile?download=true"
)
VERSION_URL   = (
    "https://huggingface.co/Macmill/Fyve-AI/resolve/main/"
    "version.txt?download=true"
)

GGUF_SIZE_HINT = "~2.6 GB"
OLLAMA_TIMEOUT = 30


# ── SSL ────────────────────────────────────────────────────────────────────

def _make_ssl_context():
    """Return a verified SSL context that works on fresh Windows installs.

    Fresh Windows VMs can have an empty or incomplete system certificate store.
    certifi (a portable CA bundle) is always available here because it is a
    transitive dependency of ollama → httpx → certifi, installed by start.bat
    before setup.py runs. We try it first, then fall back to the system store.
    SSL verification is never disabled.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    return ssl.create_default_context()


# ── Download ───────────────────────────────────────────────────────────────

def download_file(url, dest_path, label):
    """Download a file with a live progress bar. Returns True on success.

    Uses chunked urlopen with a custom SSL context so downloads work on
    fresh Windows VMs where the system certificate store may be incomplete.
    """
    ssl_ctx = _make_ssl_context()
    opener  = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl_ctx)
    )

    try:
        with opener.open(url, timeout=60) as response:
            total_size = int(response.headers.get("Content-Length", 0) or 0)
            downloaded = 0

            with open(dest_path, "wb") as out:
                while True:
                    chunk = response.read(65536)   # 64 KB chunks
                    if not chunk:
                        break
                    out.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        pct      = min(100.0, downloaded * 100.0 / total_size)
                        filled   = int(pct / 2)
                        bar      = "#" * filled + "-" * (50 - filled)
                        mb_done  = downloaded / (1024 * 1024)
                        mb_total = total_size  / (1024 * 1024)
                        print(
                            f"\r[ .. ] [{bar}] {pct:5.1f}%  {mb_done:.0f}/{mb_total:.0f} MB",
                            end="", flush=True
                        )
                    else:
                        mb_done = downloaded / (1024 * 1024)
                        print(f"\r[ .. ] {mb_done:.1f} MB downloaded...", end="", flush=True)

        print(f"\n[ OK ] {label} downloaded.")
        return True

    except Exception as e:
        print(f"\n[ EX ] Download failed: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False


# ── Ollama location helpers ────────────────────────────────────────────────

def find_ollama_exe():
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama.exe"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return shutil.which("ollama")


def find_ollama_app():
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama app.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Ollama", "ollama app.exe"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


# ── Ollama server helpers ──────────────────────────────────────────────────

def is_ollama_online():
    """Check if the Ollama server is listening on localhost."""
    try:
        urllib.request.urlopen("http://127.0.0.1:11434", timeout=3)
        return True
    except Exception:
        return False


def launch_ollama_tray():
    """Launch Ollama as a detached background process. Returns True if started."""
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
    """Download and run the Ollama installer via PowerShell."""
    print("[ !! ] Ollama not found. Starting installation...")
    # Full path avoids "not recognized" errors on minimal VMs where
    # System32 may not be in the inherited PATH.
    ps_exe = os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"),
        "System32", "WindowsPowerShell", "v1.0", "powershell.exe"
    )
    try:
        subprocess.run(
            [ps_exe, "-ExecutionPolicy", "Bypass", "-Command",
             "irm https://ollama.com/install.ps1 | iex"],
            check=True
        )
        print("[ OK ] Ollama installation complete.")
    except Exception as e:
        print(f"[ EX ] Installation failed: {e}")
        print("       Please install Ollama manually from https://ollama.com")
        sys.exit(1)


def ensure_ollama_serving():
    """Ensure the Ollama server is running, launching it if necessary."""
    print("[ .. ] Checking AI server status...")
    if is_ollama_online():
        print("[ OK ] AI server is online.")
        return

    print("[ .. ] Ollama is not running. Launching now...")
    if not launch_ollama_tray():
        print("[ EX ] Could not locate the Ollama application.")
        print("       Please start Ollama from the Start Menu and try again.")
        sys.exit(1)

    print("[ .. ] Waiting for Ollama to come online...(This can take upto 2 minutes on first launch.)", end="", flush=True)
    for _ in range(OLLAMA_TIMEOUT):
        time.sleep(1)
        print(".", end="", flush=True)
        if is_ollama_online():
            print("\n[ OK ] AI server is online.")
            return

    print("\n[ EX ] Timeout waiting for Ollama to start.")
    print("       Please start Ollama manually from the Start Menu and try again.")
    sys.exit(1)


# ── Version helpers ────────────────────────────────────────────────────────

def get_remote_version():
    """Fetch the latest model version string from HuggingFace.

    Returns None silently if the machine is offline or the request fails,
    so callers can skip the update check gracefully.
    """
    try:
        ssl_ctx = _make_ssl_context()
        opener  = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_ctx)
        )
        with opener.open(VERSION_URL, timeout=5) as r:
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


# ── Model helpers ──────────────────────────────────────────────────────────

def unregister_model(exe):
    """Remove the model from Ollama's registry."""
    print("[ .. ] Removing old model from Ollama...")
    try:
        subprocess.run(
            [exe, "rm", MODEL_NAME],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=15
        )
        print("[ OK ] Old model removed from Ollama.")
    except Exception as e:
        print(f"[ !! ] Could not remove old model from Ollama: {e}")


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
    print("[ EX ] Registration failed.")
    print(f"       Try manually: ollama create {MODEL_NAME} -f \"{MODEL_FILE}\"")
    return False


def _cleanup_temps(*paths):
    """Remove partial download files, ignoring errors."""
    for path in paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def check_for_model_update(exe):
    """Check if a newer model version exists on HuggingFace.

    Skips silently if offline. Both files are downloaded to temp paths before
    the existing model is touched — if either download fails, the current
    model is left completely unchanged. The user always has the choice to skip.
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
        print(f"\n[ !! ] Model update available: v{local_version} -> v{remote_version}")
    else:
        print(f"\n[ !! ] Model update available (v{remote_version}).")

    answer = input(
        "       Download update now? (~2.6 GB, existing model will be replaced) [Y/N]: "
    ).strip().lower()
    if answer not in ("", "y", "yes"):
        print("[ .. ] Skipping update. Continuing with current model.")
        return

    tmp_modelfile = MODEL_FILE + ".tmp"
    tmp_gguf      = GGUF_FILE  + ".tmp"

    print("[ .. ] Downloading updated Modelfile...")
    if not download_file(MODELFILE_URL, tmp_modelfile, "Modelfile"):
        print("[ EX ] Could not download updated Modelfile. Existing model is unchanged.")
        _cleanup_temps(tmp_modelfile, tmp_gguf)
        return

    if not download_file(GGUF_URL, tmp_gguf, "AI model"):
        print("[ EX ] Model download failed. Existing model is unchanged.")
        _cleanup_temps(tmp_modelfile, tmp_gguf)
        return

    # Both downloads succeeded — safe to swap
    unregister_model(exe)
    shutil.move(tmp_modelfile, MODEL_FILE)
    shutil.move(tmp_gguf, GGUF_FILE)

    if register_model(exe):
        save_local_version(remote_version)
        print(f"[ OK ] Model updated to v{remote_version}.")
    else:
        print("[ EX ] Registration failed after download. Try running start.bat again.")


def ensure_model_registered(exe):
    """Ensure the model is present and registered with Ollama.

    Downloads the Modelfile and GGUF from HuggingFace if either is missing.
    If the model is already registered, checks for updates instead.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

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
        check_for_model_update(exe)
        return

    # Model not registered — need the GGUF
    if not os.path.exists(GGUF_FILE):
        print(f"\n[ !! ] AI model file not found in '{MODEL_DIR}/'.")
        answer = input(
            f"       Download it now? ({GGUF_SIZE_HINT}, requires internet) [Y/n]: "
        ).strip().lower()
        if answer in ("", "y", "yes"):
            if not download_file(GGUF_URL, GGUF_FILE, "AI model"):
                print("[ EX ] Download failed. AI hints will be unavailable.")
                return
        else:
            print("       Skipping. AI hints will be unavailable.")
            print("       https://huggingface.co/Macmill/Fyve-AI")
            return

    if register_model(exe):
        remote_version = get_remote_version()
        if remote_version:
            save_local_version(remote_version)


# ── Entry point ────────────────────────────────────────────────────────────

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
