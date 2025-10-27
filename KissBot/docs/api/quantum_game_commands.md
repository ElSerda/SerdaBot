# commands.quantum_game_commands

**Migré depuis**: `commands/quantum_game_commands.py`  
**Lignes doc originales**: 46  
**Éléments over-engineered**: 0  

---

## Module Overview

```text

Quantum-inspired game commands. See: docs/api/quantum_game_commands.md

```

## API Reference

### Standard Components

#### QuantumGameCommands (class)

```text

Commandes de jeu avec comportements quantiques.

```

#### cog_unload (func)

```text

Nettoyage à la décharge du cog.

```

#### collapse_game_state (func)

```text


        !collapse <jeu> - COLLAPSE quantique (fixe l'état définitivement)
        
        EFFONDREMENT: Superposition → État permanent (verified: 1)
        LEARNING: Le bot apprend de vos confirmations

```

#### entangle_games (func)

```text


        !qentangle <jeu1> <jeu2> - Créer intrication entre jeux
        
        INTRICATION: Confirmations d'un jeu influencent l'autre

```

#### prepare (func)

```text

Prépare le cog pour TwitchIO.

```

#### quantum_cleanup (func)

```text


        !qclean - Décohérence manuelle (évaporation états expirés)
        
        DÉCOHÉRENCE: Supprime les "particules virtuelles" non-confirmées

```

#### quantum_dashboard (func)

```text


        !qdash [jeu] - Dashboard visuel quantique
        
        INTERFACE: Affichage visuel des états quantiques avec barres de progression

```

#### quantum_game_search (func)

```text


        !qgame <nom> - Recherche quantique de jeu
        
        SUPERPOSITION: Propose des états possibles jusqu'à validation
        OBSERVATION: Chaque recherche influence les probabilités futures

```

#### quantum_game_stats (func)

```text


        !qstats - Statistiques du système quantique des jeux
        
        MÉTRIQUES: États, superpositions, intrications, apprentissage

```

#### quantum_help (func)

```text


        !qhelp - Aide commandes quantiques
        
        DOCUMENTATION: Guide d'utilisation du système quantique

```

#### quantum_suggestions (func)

```text


        !qsuggest <jeu> - Affiche tous les états en superposition
        
        SUPERPOSITION: Visualise tous les états possibles avant collapse

```
