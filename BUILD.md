# BUILD.md — Guide de Build SerdaBot

Guide pour créer un exécutable Windows (`.exe`) du bot Twitch.

---

## 📋 Checklist Avant Build

### ✅ Code
- [x] Tous les tests passent (68/68)
- [x] Coverage à 27%+
- [x] Pas d'import absolu cassé
- [x] Config sample présent
- [ ] Version mise à jour dans README

### ✅ Configuration
- [x] `config.sample.yaml` présent
- [x] `.gitignore` propre (pas de secrets)
- [ ] Créer `version.txt` avec numéro de version

### ✅ Dépendances
- [x] `requirements.txt` complet
- [ ] Tester installation propre dans nouveau venv
- [ ] PyInstaller installé

---

## 🛠️ Installation de PyInstaller

```bash
# Linux/macOS
pip install pyinstaller

# Windows
pip install pyinstaller
```

---

## 🔨 Build de l'Exécutable

### Option 1 : Build Simple (Un seul fichier)

```bash
pyinstaller --onefile --name SerdaBot src/chat/twitch_bot.py
```

### Option 2 : Build avec Spec (Recommandé)

```bash
# Générer le fichier .spec
pyi-makespec --onefile --name SerdaBot src/chat/twitch_bot.py

# Éditer SerdaBot.spec si nécessaire

# Build
pyinstaller SerdaBot.spec
```

### Option 3 : Build Complet avec Ressources

```bash
pyinstaller \
  --onefile \
  --name SerdaBot \
  --add-data "src/prompts:prompts" \
  --add-data "src/config/config.sample.yaml:config" \
  --hidden-import twitchio \
  --hidden-import httpx \
  --hidden-import deep_translator \
  --hidden-import langdetect \
  src/chat/twitch_bot.py
```

---

## 📦 Structure Après Build

```
dist/
  SerdaBot.exe          # Exécutable Windows
  SerdaBot              # Exécutable Linux/macOS

build/                  # Fichiers temporaires (ignorés)

SerdaBot.spec          # Configuration PyInstaller
```

---

## 🚀 Distribution

### Fichiers à Inclure

```
SerdaBot-v0.1.0-alpha/
├── SerdaBot.exe
├── config.sample.yaml
├── README.md
├── LICENSE
├── data/
│   └── (fichiers vides pour structure)
└── logs/
    └── (vide)
```

### Créer une Archive

```bash
# Windows (PowerShell)
Compress-Archive -Path dist\SerdaBot.exe,config.sample.yaml,README.md,LICENSE -DestinationPath SerdaBot-v0.1.0-alpha.zip

# Linux/macOS
zip -r SerdaBot-v0.1.0-alpha.zip dist/SerdaBot config.sample.yaml README.md LICENSE
```

---

## ⚠️ Limitations du Build .exe

### Ce qui NE sera PAS inclus :
- ❌ LM Studio (doit être installé séparément)
- ❌ Modèles GGUF (trop gros pour distribuer)
- ❌ Python (embarqué dans l'exe)

### L'utilisateur devra :
1. Télécharger l'exe
2. Créer `config.yaml` depuis `config.sample.yaml`
3. Installer LM Studio et charger un modèle
4. Lancer `SerdaBot.exe`

---

## 🐛 Troubleshooting

### Erreur : Module not found

```bash
# Ajouter manuellement le module
pyinstaller --hidden-import nom_du_module ...
```

### Erreur : File not found (prompts)

```bash
# Inclure les ressources
pyinstaller --add-data "src/prompts:prompts" ...
```

### L'exe est trop gros (>100 MB)

- ✅ Normal pour PyInstaller (embarque Python + libs)
- 🔧 Utiliser `--exclude-module` pour retirer des libs inutilisées
- 🔧 Utiliser UPX pour compresser l'exe

```bash
pip install pyinstaller[encryption]
pyinstaller --upx-dir=/path/to/upx ...
```

---

## 📊 Taille Estimée

| Version | Taille |
|---------|--------|
| OneFile (.exe) | ~50-80 MB |
| OneDir (dossier) | ~120-150 MB |
| Avec UPX | ~30-50 MB |

---

## 🔐 Signature de l'Exe (Optionnel)

Pour éviter les warnings Windows SmartScreen :

1. Acheter un certificat de code signing ($$$)
2. Signer avec `signtool.exe`
3. Uploader sur Microsoft pour validation

**Alternative gratuite** : Distribuer le code source + instructions d'installation.

---

## ✅ Release GitHub

```bash
# Tagger la version
git tag -a v0.1.0-alpha -m "Release Alpha v0.1.0"
git push origin v0.1.0-alpha

# Créer release sur GitHub
# Uploader SerdaBot-v0.1.0-alpha.zip
```

---

## 📝 Notes

- Build Windows doit être fait **sur Windows**
- Build Linux doit être fait **sur Linux**
- Build macOS doit être fait **sur macOS**
- Pas de cross-compilation avec PyInstaller

---

## 🆘 Support

Pour les problèmes de build, ouvre une issue sur GitHub avec :
- OS et version Python
- Commande PyInstaller utilisée
- Log d'erreur complet
