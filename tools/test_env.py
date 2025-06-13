import os
import sys
import time
import subprocess
import requests
import importlib

from config.config import load_config

REQUIRED_MODULES = [
    "httpx",
    "twitchio",
    "requests",
    "yaml",
    "fastapi",
    "uvicorn",
    "argostranslate",
    "bs4",
    "langdetect",
    "apscheduler",
    "prometheus_client"
]

def test_dependencies():
    print("🔍 Checking Python dependencies...")
    missing = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"❌ Missing modules: {', '.join(missing)}")
        print(f"💡 Install with: pip install {' '.join(missing)}")
        sys.exit(1)
    else:
        print("✅ All required modules are installed.")

def ping_model_endpoint(endpoint, timeout=5):
    try:
        r = requests.post(endpoint, json={"messages": [{"role": "user", "content": "ping"}]}, timeout=timeout)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️  Could not reach model endpoint: {e}")
        return False

def test_config():
    print("🔧 Checking bot configuration...")

    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Failed to load config.yaml: {e}")
        sys.exit(1)

    model_path = os.path.join(config["bot"]["model_path"], config["bot"]["model_file"])
    endpoint = config["bot"]["model_endpoint"]

    print(f"📁 Checking model file: {model_path}")
    if os.path.isfile(model_path):
        print("✅ Model file exists.")
    else:
        print("❌ Model file not found.")

    print(f"🌐 Pinging model endpoint: {endpoint}")
    if ping_model_endpoint(endpoint):
        print("✅ Model endpoint is responsive.")
    else:
        print("🛠️  Trying to start model server...")
        try:
            subprocess.Popen(["tools/start_servers.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(6)  # Wait for the server to spin up
        except Exception as e:
            print(f"❌ Failed to launch start_servers.sh: {e}")
            sys.exit(1)

        print("🔁 Retrying model endpoint...")
        if ping_model_endpoint(endpoint, timeout=5):
            print("✅ Model endpoint is now responsive.")
        else:
            print("❌ Model endpoint is still unreachable after startup attempt.")

if __name__ == "__main__":
    print("🧪 Running full environment check...")
    test_dependencies()
    print("")
    test_config()
    print("\n✅ Environment check complete.")
