# ✅ Migration vers une structure `src/tools/` (style FastAPI)

Cette checklist prépare ton projet SerdaBot à une architecture plus modulaire, plus compatible packaging, et plus robuste aux erreurs d'import.

---

## 🧭 Objectif
Migrer tous les fichiers de `tools/` vers `src/tools/`, en conservant la compatibilité avec les scripts `.sh` et les modules Python.

---

## 📦 Checklist de migration

### 1. 📁 Structure des dossiers
- [ ] Déplacer tout le contenu de `tools/` vers `src/tools/`
- [ ] Supprimer le dossier `tools/` à la racine
- [ ] Créer `src/tools/__init__.py` s’il n’existe pas

### 2. 🔁 Mise à jour des scripts shell
Dans tous les `.sh` de lancement (`start_servers.sh`, `stop_servers.sh`, `reload_servers.sh`, etc.) :
- [ ] Ajouter `export PYTHONPATH=src` en début de script
- [ ] Adapter les appels à Python avec `-m tools.nom_script`

Exemple :
```bash
export PYTHONPATH=src
python -m tools.start_servers
```

### 3. 🧪 Mise à jour de `tools/test_env.py`
- [ ] Ajouter un check d’environnement : avertir si `PYTHONPATH` n’est pas défini ou erroné

### 4. 🛠️ Mise à jour `INSTALL.md`
- [ ] Expliquer dans la section "Démarrage" qu’il faut utiliser `PYTHONPATH=src`
- [ ] Donner un exemple concret pour Linux et pour Windows (via PowerShell ou `.bat`)

### 5. 🧪 Tests post-migration
- [ ] Tester tous les `.sh` : `start_servers`, `stop_servers`, `reload_servers`
- [ ] Vérifier que le bot démarre depuis `start_bot.sh`
- [ ] Vérifier les imports Python dans tous les scripts déplacés

---

## 🚀 Bonus

- [ ] Ajouter un script CLI `serdabot` via `pyproject.toml` (avec `console_scripts`)
- [ ] Préparer le terrain pour une future commande : `pipx install serdabot`

---

## ✨ Bénéfices
- Structure compatible FastAPI / Poetry / Typer
- Préparation à un packaging `.whl` propre
- Imports `from tools.xyz import` fiables
- Réduction du risque de conflits système