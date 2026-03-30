import os
import sys
import subprocess
import shutil
import time
import winreg

# --- CONFIG ---
MODEL_NAME = "fyve-ai"
MODEL_FILE = os.path.join("Fyve AI", "Modelfile")

def refresh_path():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
            sys_path, _ = winreg.QueryValueEx(key, "Path")
        os.environ["PATH"] = sys_path
        print("[ OK ] System PATH updated.")
    except:
        pass

def install_ollama():
    print("[ !! ] Ollama not found. Starting terminal installation...")
    ps_cmd = "powershell -ExecutionPolicy Bypass -Command \"irm https://ollama.com/install.ps1 | iex\""
    
    try:
        subprocess.run(ps_cmd, shell=True, check=True)
        print("[ OK ] Ollama installation complete.")
        time.sleep(2)
        refresh_path()
        return True
    except Exception as e:
        print(f"[ EX ] Installation failed: {e}")
        return False

def ensure_ollama_serving():
    print("[ .. ] Checking AI server status...")
    try:
        subprocess.run(["ollama", "list"], capture_output=True, check=True, timeout=3)
        print("[ OK ] AI server is online.")
    except:
        print("[ .. ] Server offline. Starting background service...")
        subprocess.Popen(["ollama", "serve"], 
                         creationflags=subprocess.CREATE_NEW_CONSOLE,
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        time.sleep(5)
        print("[ OK ] Service started.")

def main():
    print("\n--- PyFyve AI Configuration ---")

    # 1. Ollama Check
    if not shutil.which("ollama"):
        if not install_ollama():
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("[ OK ] Ollama executable found.")

    # 2. Server Check
    ensure_ollama_serving()

    # 3. Model Check
    if os.path.exists(MODEL_FILE):
        print(f"[ .. ] Verifying model: {MODEL_NAME}")
        check = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if MODEL_NAME not in check.stdout:
            print(f"[ .. ] Registering {MODEL_NAME} (please wait)...")
            res = subprocess.run(["ollama", "create", MODEL_NAME, "-f", MODEL_FILE], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[ OK ] Model '{MODEL_NAME}' registered.")
            else:
                print(f"[ EX ] Registration failed: {res.stderr}")
        else:
            print(f"[ OK ] Model '{MODEL_NAME}' is ready.")
    else:
        print(f"[ EX ] Error: '{MODEL_FILE}' missing.")

    # 4. Final Launch
    print("\n[ OK ] System initialization complete.")
    print("[ >> ] Launching PyFyve...")
    time.sleep(1.5)
    
    if os.path.exists("main.py"):
        subprocess.run([sys.executable, "main.py"])
    else:
        print("[ EX ] Error: 'main.py' not found.")

if __name__ == "__main__":
    main()
