# scripts.health_monitor

**Migré depuis**: `scripts/health_monitor.py`  
**Lignes doc originales**: 35  
**Éléments over-engineered**: 0  

---

## Module Overview

**(Documentation originale over-engineered - migrated from inline)**

```text


📊 KissBot Monitoring & Health Check

Script de monitoring pour surveiller le système KissBot en production.
Vérifie le statut de tous les composants et génère des rapports.

COMPOSANTS SURVEILLÉS :
├── Cache Systems      : GameCache + QuantumGameCache
├── APIs Status       : RAWG, Steam, OpenAI, LLM Local  
├── Intelligence      : LLMHandler cascade
├── Quantum Health    : États, décohérence, apprentissage
├── Performance       : Latence, hit rates, mémoire
└── Logs Analysis     : Erreurs récentes, patterns

ALERTES :
- Cache hit rate < 80%
- API failures > 10%
- LLM indisponible > 5min
- États quantiques corrompus
- Mémoire > 90%

```

## API Reference

### Standard Components

#### KissBotMonitor (class)

```text

Système de monitoring KissBot complet.

```

#### _analyze_health_issues (func)

```text

Analyse les problèmes de santé.

```

#### _calculate_overall_status (func)

```text

Calcule le statut global.

```

#### _check_cache_classic (func)

```text

Check du cache classique.

```

#### _check_cache_manager (func)

```text

Check du gestionnaire de cache unifié.

```

#### _check_cache_quantum (func)

```text

Check du cache quantique.

```

#### _check_game_lookup (func)

```text

Check du système de lookup de jeux.

```

#### _check_llm_handler (func)

```text

Check du handler LLM.

```

#### _check_system_resources (func)

```text

Check des ressources système.

```

#### _get_resource_warnings (func)

```text

Génère des alertes de ressources.

```

#### main (func)

```text

Point d'entrée principal.

```

#### print_health_report (func)

```text

Affiche le rapport de santé.

```

#### run_full_health_check (func)

```text

Lance un check de santé complet.

```

#### save_report (func)

```text

Sauvegarde le rapport.

```
