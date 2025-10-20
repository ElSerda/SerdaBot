# 🎮 RAWG API - Mode Kiff

Setup ultra simple pour tester RAWG.

## ⚡ Quick Start

### 1. Ajoute ta clé RAWG

Dans `config/config.yaml`:
```yaml
rawg:
  api_key: "ta_clé_ici"  # Obtenir sur https://rawg.io/apidocs
```

### 2. Lance le test

```bash
python test_rawg_simple.py
```

## 🎯 Ce que ça fait

- ✅ Test 3 jeux populaires
- ✅ Affiche: nom, année, plateformes, notes
- ✅ Logs clairs et simples

## 📊 Résultat attendu

```
🔍 Recherche: Hades
------------------------------------------------------------
✅ Hades (2020)
📅 Sortie: 2020-09-17
🎮 Plateformes: PC, PlayStation 4, PlayStation 5, Xbox One, Xbox Series S/X
⭐ Metacritic: 93/100
⭐ Note: 4.3/5 (15,234 avis)
🎭 Genres: Action, Indie, RPG
```

## 🐛 Troubleshooting

**Erreur "No API key":**
→ Ajoute ta clé RAWG dans config.yaml

**Erreur "httpx not found":**
→ `pip install httpx`

**Rien ne s'affiche:**
→ Active debug dans config.yaml: `debug: true`

## 🚀 Après validation

Une fois que RAWG fonctionne:
1. Intégrer dans `!gameinfo`
2. Tester en live sur Twitch

C'est tout ! 🎉
