# INSTALL_WINDOWS.md — SerdaBot v0.1.0

Guide d'installation pour **Windows 10/11** avec PowerShell.

---

## 1. Prérequis

- **Python 3.10+** : [python.org/downloads](https://www.python.org/downloads/)
  - ⚠️ Cocher "Add Python to PATH" lors de l'installation
- **Git** : [git-scm.com/download/win](https://git-scm.com/download/win)
- **PowerShell 5.1+** (inclus dans Windows 10/11)

---

## 2. Cloner le Projet

Ouvre **PowerShell** ou **Windows Terminal** :

```powershell
mkdir serdabot-test
cd serdabot-test
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot
```

---

## 3. Créer l'Environnement Virtuel

```powershell
python -m venv venv
```

### Activer l'environnement virtuel

```powershell
.\venv\Scripts\Activate.ps1
```

**Si tu as une erreur "execution policy"**, lance cette commande **en tant qu'administrateur** :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 4. Installer les Dépendances

```powershell
pip install -r requirements.txt
```

---

## 5. Configuration

```powershell
Copy-Item src\config\config.sample.yaml src\config\config.yaml
```

Édite `src\config\config.yaml` avec tes tokens et paramètres.

---

## 6. Démarrer le Bot

### Option 1 : Script PowerShell (recommandé)

```powershell
.\start_bot.ps1
```

### Option 2 : Commande manuelle

```powershell
$env:PYTHONPATH = "."
python src\chat\twitch_bot.py
```

---

## 7. Tester l'Installation

```powershell
$env:PYTHONPATH = "src"
python tools\test_env.py
```

---

## 8. Tests Unitaires

```powershell
pytest tests\
```

---

## Différences Windows vs Linux

| Fonctionnalité | Linux | Windows |
|----------------|-------|---------|
| Script de démarrage | `./start_bot.sh` | `.\start_bot.ps1` |
| Activation venv | `source venv/bin/activate` | `.\venv\Scripts\Activate.ps1` |
| Séparateur de chemin | `/` | `\` |
| Variables d'env | `export VAR=value` | `$env:VAR = "value"` |
| Scripts tools/ | Bash (`.sh`) | Pas encore portés |

---

## Limitations Windows

⚠️ Les scripts dans `tools/` sont en **Bash uniquement** (Linux/macOS) :
- `start_servers.sh`
- `stop_servers.sh`
- `install_project.sh`

**Solution** : Lance ces commandes manuellement sous Windows ou utilise **WSL** (Windows Subsystem for Linux).

---

## Utiliser WSL (Alternative Recommandée)

Si tu veux utiliser les scripts Bash, installe **WSL** :

1. Ouvre PowerShell en admin :
   ```powershell
   wsl --install
   ```

2. Redémarre ton PC

3. Lance Ubuntu depuis le menu démarrer

4. Suis les instructions de `INSTALL.md` normalement

---

## Notes

- **Logs** : stockés dans `.\logs\`
- **Config** : `src\config\config.yaml`
- **Données** : `data\*.json`

---

## Support

Pour les problèmes Windows spécifiques, ouvre une issue sur GitHub avec le tag `[Windows]`.

---

## Licence

Ce projet est sous licence **AGPLv3** — voir [LICENSE](LICENSE) pour les détails.
