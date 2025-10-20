# 🎯 Auto-Tune Scripts

Scripts d'optimisation automatique pour trouver les limites optimales du modèle LLM.

## 📁 Contenu

### `find_max_concurrent.py`
**Recherche automatique du nombre max d'utilisateurs concurrents**

Utilise un algorithme de **dichotomie (binary search)** pour trouver le nombre maximum d'utilisateurs pouvant être servis simultanément sans dépasser 3s de latence.

#### Fonctionnement
1. Teste une plage de 1 à 50 utilisateurs
2. Chaque utilisateur envoie 3 messages (avec historique de 4 messages max)
3. Dès qu'une latence > 3.0s est détectée, le test est marqué comme raté
4. L'algorithme converge vers la valeur optimale en ~6 itérations (log₂(50))

#### Utilisation
```bash
python3 auto-tune/find_max_concurrent.py
```

#### Configuration
Le script teste actuellement avec :
- **Historique** : 4 messages max (2 tours de conversation)
- **Cooldown** : 10 secondes entre chaque message (configurable dans `config.yaml`)
- **Timeout** : 3 secondes max par requête
- **Plage de test** : 1-50 utilisateurs concurrents

#### Résultat
Sauvegarde automatiquement dans `config/model_limits.json` :
```json
{
  "model_name": "qwen2.5-3b-instruct",
  "max_concurrent_users": 5,
  "max_history_messages": 4,
  "user_rate_limit": 0.5,
  "response_timeout": 3.0,
  "tested_at": "2025-10-19 04:30:58",
  "test_results": [...]
}
```

#### Versions testées

| Version | Cooldown | Kill immédiat | Résultat | Notes |
|---------|----------|---------------|----------|-------|
| V1 | ❌ Non | ❌ Non | **8 users** | Spam dans les logs, stats complètes |
| V2 | ❌ Non | ✅ Oui | **2 users** | Propre mais stats incomplètes (sous-évalué) |
| V3 | ✅ 5s | ✅ Oui | **5 users** | **OPTIMAL** - Logs propres, modèle pas saturé |

#### Algorithme de dichotomie
```
Plage initiale : [1, 50]
├─ Test 25 users → ❌ Trop lent
├─ Nouvelle plage : [1, 24]
│  ├─ Test 12 users → ❌ Trop lent
│  ├─ Nouvelle plage : [1, 11]
│  │  ├─ Test 6 users → ❌ Trop lent
│  │  ├─ Nouvelle plage : [1, 5]
│  │  │  ├─ Test 3 users → ✅ OK
│  │  │  ├─ Test 4 users → ✅ OK
│  │  │  ├─ Test 5 users → ✅ OK
│  │  │  └─ Test 6 users → ❌ Trop lent
│  │  └─ RÉSULTAT : 5 users max ✅
```

## 🔧 Développement

### Ajouter un nouveau script d'auto-tune

1. Créer le script dans `auto-tune/`
2. Utiliser le même format de sortie (sauvegarde JSON dans `config/`)
3. Documenter dans ce README
4. Ajouter dans `.gitignore` si génère des fichiers temporaires

### Principes
- ✅ Automatisation complète (pas d'intervention manuelle)
- ✅ Logs clairs et concis
- ✅ Résultats sauvegardés en JSON pour traçabilité
- ✅ Convergence rapide (dichotomie plutôt que brute-force)
- ✅ Tests réalistes (scénarios proches de la production)

## 📊 Historique des optimisations

### 2025-10-19 : Découverte initiale
- **Test V1** (sans cooldown, avec spam) : 8 users max
- **Test V2** (sans cooldown, kill immédiat) : 2 users max (faux)
- **Test V3** (cooldown 5s, kill immédiat) : 5 users max ✅

### Configuration production actuelle
```python
MAX_CONCURRENT_USERS = 5
MAX_HISTORY_MESSAGES = 4
USER_RATE_LIMIT = 0.5
RESPONSE_TIMEOUT = 3.0
```

## 🚀 Prochaines étapes

- [ ] Auto-tune pour `MAX_HISTORY_MESSAGES` (trouver l'optimal entre mémoire et performance)
- [ ] Auto-tune pour `temperature` (trouver le meilleur équilibre créativité/cohérence)
- [ ] Auto-tune pour `max_tokens` (optimiser la longueur des réponses)
- [ ] Benchmark comparatif entre différents modèles (Qwen vs GPT vs autres)
