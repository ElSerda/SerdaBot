# 🔬 Optimisation Modèle - Résultats Tests Scientifiques

> Documentation des tests comparatifs entre Qwen2.5-1.5B et Qwen2.5-7B

## 📊 Résumé Exécutif

**Modèle retenu** : Qwen2.5-1.5B-Instruct-Q4_K_M  
**Raison** : Fiabilité supérieure (98.9% vs 94.4%), plus concis, moins de ressources

---

## 🧪 Tests Effectués

### Test 1 : max_tokens (30-80)
- **Objectif** : Trouver la limite optimale pour phrases complètes
- **Méthode** : Question identique testée avec différentes limites
- **Résultat** : 
  - 1.5B : 100% complet dès 40 tokens avec prompt "Réponds en une phrase"
  - 7B : Nécessite 70-80 tokens, plus verbeux

### Test 2 : Températures (0.0-1.0)
- **Objectif** : Impact de la température sur qualité/créativité
- **Méthode** : 15 questions × 6 températures (90 tests totaux)
- **Dataset** : Animaux, tech, science, histoire, gaming, divers

#### Résultats Qwen2.5-1.5B
```
Tests total: 90
Longueur moyenne: 97.6 chars
Range: 15-180 chars
Taux phrases complètes: 98.9% (89/90)

Par température:
  T=0.0: 102 chars, 100% ✅
  T=0.2:  97 chars,  93%
  T=0.4:  98 chars, 100% ✅ ← OPTIMAL
  T=0.6: 104 chars, 100% ✅
  T=0.8:  98 chars, 100% ✅
  T=1.0:  87 chars, 100% ✅
```

#### Résultats Qwen2.5-7B
```
Tests total: 90
Longueur moyenne: 120.8 chars (+24% vs 1.5B)
Range: 41-247 chars
Taux phrases complètes: 94.4% (85/90)

Par température:
  T=0.0: 130 chars, 100% ✅
  T=0.2: 131 chars, 100% ✅
  T=0.4: 122 chars,  93%
  T=0.6: 118 chars,  93%
  T=0.8: 102 chars,  87% ❌ (glitchs chinois)
  T=1.0: 122 chars,  93%
```

### Test 3 : Avec/Sans Exemples Few-Shot
- **Avec exemples** : 1.5B copie exactement (perroquet)
- **Sans exemples** : 1.5B varie naturellement, reste fiable à 98.9%
- **Conclusion** : Exemples inutiles, le modèle est performant sans

---

## 🎯 Configuration Finale Optimale

### Mode ASK (Questions factuelles)
```python
MAX_TOKENS_ASK = 80     # Permet finir phrases proprement
TEMP_ASK = 0.4          # Sweet spot: 98 chars moyens, 100% fiable
```

**Prompt** :
```
Réponds en une phrase. Maximum 230 caractères. 
Si tu ne sais pas, dis "Je ne sais pas".
```

**Transformation question** :
```python
# Force le modèle à finir en ajoutant contrainte dans USER prompt
"parle moi des pandas roux" → "parle moi des pandas roux ? Réponds en une phrase."
"python" → "C'est quoi python ? Réponds en une phrase."
```

### Mode CHILL (Interactions sociales)
```python
MAX_TOKENS_CHILL = 45   # Adapte naturellement 1-2 phrases
TEMP_CHILL = 0.5        # Légèrement plus créatif
```

**Prompt** :
```
Tu es serda_bot, bot Twitch cool et décontracté.
Adapte ta réponse : 1-5 mots pour réactions simples, 
jusqu'à 2 phrases courtes si question intéressante.
TERMINE TOUJOURS tes phrases.
```

---

## ⚠️ Problèmes Identifiés

### Hallucinations (1.5B)
Le modèle invente des faits incorrects :
- "pandas roux = louveteaux bearacées"
- "trou noir = jeu vidéo Ubisoft 1998"
- "axolotl = poisson amphibien" (c'est une salamandre)

**Solution prévue** : Fact Cache (Wikipedia/Wikidata) pour questions factuelles courantes

### Glitchs Multilingues (7B)
À T≥0.8, le 7B bascule en chinois aléatoirement :
- "blockchain" → Mix français/chinois
- "react" → "React est un framework JavaScript用于构建用户界面"
- "trou noir" → Réponse complète en chinois

**Raison** : Modèle multilingue instable à haute température  
**Solution** : Utiliser le 1.5B qui n'a pas ce problème

---

## 📈 Métriques de Performance

| Métrique | 1.5B | 7B | Gagnant |
|----------|------|-----|---------|
| **Fiabilité** | 98.9% | 94.4% | 🏆 1.5B |
| **Concision** | 97.6 chars | 120.8 chars | 🏆 1.5B |
| **Stabilité temp** | 100% à T=0.4-1.0 | 87% à T=0.8 | 🏆 1.5B |
| **Qualité factuelle** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 7B |
| **RAM/CPU** | ~1.5 GB | ~5 GB | 🏆 1.5B |
| **Vitesse** | ~70 tok/s | ~80 tok/s | 7B |

**Score final** : 1.5B domine sur fiabilité, ressources et stabilité

---

## 🚀 Prochaines Étapes

### 1. Fact Cache (Priorité Haute)
Implémenter cache Wikipedia/Wikidata pour corriger hallucinations sur :
- Animaux (pandas roux, axolotl, etc.)
- Technologie (Python, blockchain, etc.)
- Science (trou noir, ADN, etc.)
- Gaming (Minecraft, Valorant, etc.)

**APIs potentielles** :
- Wikipedia API (fr.wikipedia.org/api)
- Wikidata SPARQL
- DBpedia (fallback)

### 2. Monitoring Production
Logger les métriques :
- Longueur réponses
- finish_reason (stop vs length)
- Taux phrases incomplètes
- Hallucinations détectées (via fact_cache)

### 3. Fine-tuning (Long terme)
Si hallucinations persistent :
- Dataset curated français
- LoRA fine-tune sur connaissances factuelles
- Validation humaine

---

## 📝 Changelog

**2025-10-18** : Tests scientifiques initiaux
- Comparaison 1.5B vs 7B (90 tests)
- Optimisation max_tokens et température
- Décision : 1.5B en production
- Config : MAX_TOKENS_ASK=80, TEMP_ASK=0.4

---

## 🔗 Scripts de Test

- `scripts/test_max_tokens.py` : Test limites tokens
- `scripts/compare_1_5b_vs_7b.py` : Comparaison côte à côte
- `scripts/compare_temperatures.py` : Analyse températures (90 tests)

**Relancer les tests** :
```bash
source venv/bin/activate
python scripts/compare_temperatures.py
```
