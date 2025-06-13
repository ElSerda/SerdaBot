# tools/test_env.py

import importlib
import sys
import warnings

# Supprimer les warnings non critiques (comme pkg_resources)
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

REQUIRED_MODULES = [
    "httpx",
    "twitchio",
    "apscheduler",
    "flask",
    "prometheus_client",
    "fastapi",
    "uvicorn",
    "argostranslate",
]

print(f"Python executable: {sys.executable}")
print(f"Python version   : {sys.version.split()[0]}\n")

missing = []

for module in REQUIRED_MODULES:
    try:
        importlib.import_module(module)
        print(f"✅ {module} trouvé")
    except ImportError:
        print(f"❌ {module} manquant")
        missing.append(module)

if not missing:
    print("\n✅ Environnement et dépendances valides.")
else:
    print("\n⚠️ Modules manquants :", ", ".join(missing))
    print("💡 Tu peux les installer avec :")
    print(f"    pip install {' '.join(missing)}")
