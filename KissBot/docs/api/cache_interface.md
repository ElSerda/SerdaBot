# core.cache_interface

**Migré depuis**: `core/cache_interface.py`  
**Lignes doc originales**: 69  
**Éléments over-engineered**: 1  

---

## Module Overview

```text

Common cache interface for GameCache and QuantumGameCache. See: docs/api/cache_interface.md

```

## API Reference

### 🚨 Over-engineered Components (migrated)

#### set (func)

**Original doc**: 11 lines, 0 quantum terms


```text


        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de stockage
            value: Données à stocker
            **kwargs: Options spécifiques (ttl, confirmed, etc.)
            
        Returns:
            True si stockage réussi

```

### Standard Components

#### BaseCacheInterface (class)

```text

Interface abstraite pour tous les caches KissBot.

```

#### CacheEntry (class)

```text

Entrée de cache standardisée.

```

#### CacheManager (class)

```text


    Gestionnaire unifié pour tous les types de cache.
    
    Permet de switcher entre GameCache/QuantumGameCache de façon transparente.

```

#### CacheStats (class)

```text

Statistiques de cache standardisées.

```

#### _create_fallback_cache (func)

```text

Crée le cache de fallback.

```

#### _create_primary_cache (func)

```text

Crée le cache principal selon la configuration.

```

#### cleanup_expired (func)

```text


        Nettoie les entrées expirées.
        
        Returns:
            Nombre d'entrées supprimées

```

#### cleanup_expired (func)

```text

Nettoie tous les caches.

```

#### clear (func)

```text


        Vide le cache.
        
        Returns:
            True si vidage réussi

```

#### clear (func)

```text

Vide tous les caches.

```

#### get (func)

```text


        Récupère une valeur du cache.
        
        Args:
            key: Clé de recherche
            
        Returns:
            Dict avec les données ou None si non trouvé

```

#### get (func)

```text

Récupération avec fallback automatique.

```

#### get_stats (func)

```text


        Retourne les statistiques du cache.
        
        Returns:
            CacheStats avec métriques actuelles

```

#### get_stats (func)

```text

Statistiques combinées des caches.

```

#### get_unified_stats (func)

```text

Statistiques unifiées pour compatibilité.

```

#### has_key (func)

```text

Vérifie si une clé existe.

```

#### is_quantum_enabled (func)

```text

Indique si ce cache supporte les fonctionnalités quantiques.

```

#### search (func)

```text


        Recherche intelligente dans le cache.
        
        Args:
            query: Terme de recherche
            **kwargs: Options spécifiques (observer, mode, etc.)
            
        Returns:
            Résultat de recherche ou None

```

#### search (func)

```text

Recherche avec fallback automatique.

```

#### set (func)

```text

Stockage avec synchronisation optionnelle.

```

#### size (func)

```text

Retourne le nombre d'entrées.

```
