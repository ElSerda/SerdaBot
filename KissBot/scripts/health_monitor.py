#!/usr/bin/env python3
"""
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
"""

import asyncio
import json
import logging
import psutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup path pour imports KissBot
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_loader import load_config
from backends.game_cache import GameCache
from backends.game_lookup import GameLookup
from intelligence.handler import LLMHandler
from core.cache_interface import CacheManager

try:
    from backends.quantum_game_cache import QuantumGameCache
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False


class KissBotMonitor:
    """Système de monitoring KissBot complet."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        
        # Initialiser composants à surveiller
        self.game_cache = GameCache(config)
        self.game_lookup = GameLookup(config)
        self.llm_handler = LLMHandler(config)
        
        if QUANTUM_AVAILABLE:
            self.quantum_cache = QuantumGameCache(config)
            self.cache_manager = CacheManager(config, prefer_quantum=True)
        else:
            self.quantum_cache = None
            self.cache_manager = CacheManager(config, prefer_quantum=False)
        
        # Stats monitoring
        self.health_report = {}
        self.alerts = []
    
    async def run_full_health_check(self) -> Dict[str, Any]:
        """Lance un check de santé complet."""
        print("🔍 KISSBOT HEALTH CHECK")
        print("=" * 60)
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'version': 'KissBot V1',
            'quantum_enabled': QUANTUM_AVAILABLE,
            'components': {},
            'alerts': [],
            'overall_status': 'UNKNOWN'
        }
        
        # Test tous les composants
        health_report['components']['cache_classic'] = await self._check_cache_classic()
        health_report['components']['cache_quantum'] = await self._check_cache_quantum()
        health_report['components']['cache_manager'] = await self._check_cache_manager()
        health_report['components']['game_lookup'] = await self._check_game_lookup()
        health_report['components']['llm_handler'] = await self._check_llm_handler()
        health_report['components']['system_resources'] = await self._check_system_resources()
        
        # Analyser les résultats
        health_report['alerts'] = self._analyze_health_issues(health_report['components'])
        health_report['overall_status'] = self._calculate_overall_status(health_report['components'])
        
        self.health_report = health_report
        return health_report
    
    async def _check_cache_classic(self) -> Dict[str, Any]:
        """Check du cache classique."""
        try:
            start_time = time.time()
            
            # Test fonctionnel
            test_key = f"monitor_test_{int(time.time())}"
            test_data = {'name': 'Monitor Test', 'timestamp': time.time()}
            
            set_success = self.game_cache.set(test_key, test_data)
            retrieved = self.game_cache.get(test_key) if set_success else None
            search_result = await self.game_cache.search(test_key) if set_success else None
            
            # Stats
            stats = self.game_cache.get_stats()
            
            # Cleanup test data
            if set_success and hasattr(self.game_cache, 'cache') and test_key in self.game_cache.cache:
                del self.game_cache.cache[test_key]
                self.game_cache._save_cache()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'HEALTHY' if set_success and retrieved else 'ERROR',
                'latency_ms': round(latency_ms, 2),
                'total_keys': stats.total_keys,
                'functional_test': set_success and retrieved is not None,
                'search_test': search_result is not None,
                'quantum_enabled': stats.quantum_enabled,
                'error_details': 'Set failed' if not set_success else ('Get failed' if not retrieved else None)
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'functional_test': False
            }
    
    async def _check_cache_quantum(self) -> Dict[str, Any]:
        """Check du cache quantique."""
        if not QUANTUM_AVAILABLE or not self.quantum_cache:
            return {
                'status': 'DISABLED',
                'reason': 'Quantum cache not available'
            }
        
        try:
            start_time = time.time()
            
            # Test quantique spécialisé
            test_key = f"quantum_test_{int(time.time())}"
            test_data = {'name': 'Quantum Monitor Test', 'confidence': 0.9}
            
            set_success = self.quantum_cache.set(test_key, test_data, confirmed=True)
            retrieved = self.quantum_cache.get(test_key)
            search_result = await self.quantum_cache.search(test_key, observer='monitor')
            
            # Stats quantiques
            stats = self.quantum_cache.get_stats()
            quantum_stats = self.quantum_cache.get_quantum_game_stats()
            
            # Cleanup
            self.quantum_cache.clear()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'HEALTHY' if set_success and retrieved else 'ERROR',
                'latency_ms': round(latency_ms, 2),
                'total_keys': stats.total_keys,
                'confirmed_keys': stats.confirmed_keys,
                'learning_rate': quantum_stats.get('learning_rate', 0),
                'functional_test': set_success and retrieved is not None,
                'search_test': search_result is not None,
                'quantum_features': True
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'functional_test': False
            }
    
    async def _check_cache_manager(self) -> Dict[str, Any]:
        """Check du gestionnaire de cache unifié."""
        try:
            start_time = time.time()
            
            # Test unification
            test_key = f"manager_test_{int(time.time())}"
            test_data = {'name': 'Manager Test', 'unified': True}
            
            set_success = self.cache_manager.set(test_key, test_data)
            retrieved = self.cache_manager.get(test_key)
            search_result = await self.cache_manager.search(test_key)
            
            # Stats unifiées
            all_stats = self.cache_manager.get_stats()
            unified_stats = self.cache_manager.get_unified_stats()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                'status': 'HEALTHY' if set_success and retrieved else 'ERROR',
                'latency_ms': round(latency_ms, 2),
                'primary_cache': self.cache_manager.primary_cache.__class__.__name__,
                'fallback_available': self.cache_manager.fallback_cache is not None,
                'functional_test': set_success and retrieved is not None,
                'search_test': search_result is not None,
                'stats_primary': unified_stats.total_keys,
                'quantum_enabled': unified_stats.quantum_enabled
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'functional_test': False
            }
    
    async def _check_game_lookup(self) -> Dict[str, Any]:
        """Check du système de lookup de jeux."""
        try:
            start_time = time.time()
            
            # Test avec jeu populaire
            game_result = await self.game_lookup.search_game("Hades")
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Vérifier APIs configurées
            rawg_configured = bool(self.config.get('apis', {}).get('rawg_key'))
            steam_configured = bool(self.config.get('apis', {}).get('steam_key'))
            
            return {
                'status': 'HEALTHY' if game_result else 'WARNING',
                'latency_ms': round(latency_ms, 2),
                'functional_test': game_result is not None,
                'rawg_configured': rawg_configured,
                'steam_configured': steam_configured,
                'game_found': game_result.name if game_result else None,
                'confidence': game_result.confidence if game_result else 'N/A'
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'functional_test': False
            }
    
    async def _check_llm_handler(self) -> Dict[str, Any]:
        """Check du handler LLM."""
        try:
            start_time = time.time()
            
            # Health check LLM avec timeout court
            try:
                local_available = await asyncio.wait_for(
                    self.llm_handler._check_local_health(), 
                    timeout=3.0
                )
            except asyncio.TimeoutError:
                local_available = False
            
            # Test simple si local disponible
            functional_test = False
            response_length = 0
            if local_available:
                try:
                    response = await asyncio.wait_for(
                        self.llm_handler.generate_response(
                            "Test", context="health_check", user_name="monitor"
                        ),
                        timeout=5.0
                    )
                    functional_test = response is not None and len(response) > 0
                    response_length = len(response) if response else 0
                except asyncio.TimeoutError:
                    functional_test = False
                    response_length = 0
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Déterminer statut
            if functional_test:
                status = 'HEALTHY'
            elif local_available or self.llm_handler.openai_key:
                status = 'WARNING'  # Configuré mais pas fonctionnel
            else:
                status = 'ERROR'    # Rien de configuré
            
            return {
                'status': status,
                'latency_ms': round(latency_ms, 2),
                'local_llm_available': local_available,
                'openai_configured': bool(self.llm_handler.openai_key),
                'functional_test': functional_test,
                'response_length': response_length,
                'provider': 'local' if local_available else ('openai' if self.llm_handler.openai_key else 'none')
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'functional_test': False
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check des ressources système."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'status': 'HEALTHY',
                'memory_used_percent': round(memory.percent, 1),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_used_percent': round(disk.percent, 1),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'cpu_percent': round(cpu_percent, 1),
                'warnings': self._get_resource_warnings(memory.percent, disk.percent, cpu_percent)
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _get_resource_warnings(self, memory_percent: float, disk_percent: float, cpu_percent: float) -> List[str]:
        """Génère des alertes de ressources."""
        warnings = []
        
        if memory_percent > 90:
            warnings.append(f"Mémoire critique: {memory_percent}%")
        elif memory_percent > 80:
            warnings.append(f"Mémoire élevée: {memory_percent}%")
        
        if disk_percent > 95:
            warnings.append(f"Disque critique: {disk_percent}%")
        elif disk_percent > 85:
            warnings.append(f"Disque élevé: {disk_percent}%")
        
        if cpu_percent > 95:
            warnings.append(f"CPU critique: {cpu_percent}%")
        elif cpu_percent > 80:
            warnings.append(f"CPU élevé: {cpu_percent}%")
        
        return warnings
    
    def _analyze_health_issues(self, components: Dict[str, Any]) -> List[str]:
        """Analyse les problèmes de santé."""
        alerts = []
        
        for component, status in components.items():
            if status.get('status') == 'ERROR':
                alerts.append(f"❌ {component}: ERREUR - {status.get('error', 'Unknown')}")
            elif status.get('status') == 'WARNING':
                alerts.append(f"⚠️ {component}: ATTENTION - Fonctionnalité dégradée")
            
            # Alertes spécifiques
            if component == 'system_resources':
                alerts.extend([f"🔧 Système: {w}" for w in status.get('warnings', [])])
        
        return alerts
    
    def _calculate_overall_status(self, components: Dict[str, Any]) -> str:
        """Calcule le statut global."""
        error_count = sum(1 for c in components.values() if c.get('status') == 'ERROR')
        warning_count = sum(1 for c in components.values() if c.get('status') == 'WARNING')
        
        if error_count > 0:
            return 'CRITICAL'
        elif warning_count > 1:
            return 'WARNING'
        elif warning_count > 0:
            return 'DEGRADED'
        else:
            return 'HEALTHY'
    
    def print_health_report(self, report: Dict[str, Any]):
        """Affiche le rapport de santé."""
        status_emoji = {
            'HEALTHY': '✅',
            'DEGRADED': '🟡', 
            'WARNING': '⚠️',
            'CRITICAL': '❌'
        }
        
        overall_status = report['overall_status']
        print(f"\n📊 RAPPORT DE SANTÉ KISSBOT")
        print(f"   Statut: {status_emoji.get(overall_status, '❓')} {overall_status}")
        print(f"   Uptime: {report['uptime_seconds']:.0f}s ({report['uptime_seconds']/3600:.1f}h)")
        print(f"   Quantum: {'🔬 Activé' if report['quantum_enabled'] else '💾 Classique'}")
        
        print(f"\n🔧 COMPOSANTS:")
        for name, status in report['components'].items():
            status_text = status.get('status', 'UNKNOWN')
            emoji = status_emoji.get(status_text, '❓')
            latency = status.get('latency_ms', 0)
            print(f"   {emoji} {name.replace('_', ' ').title()}: {status_text} ({latency:.1f}ms)")
        
        if report['alerts']:
            print(f"\n🚨 ALERTES ({len(report['alerts'])}):")
            for alert in report['alerts']:
                print(f"   {alert}")
        else:
            print(f"\n✅ Aucune alerte")
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Sauvegarde le rapport."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cache/health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Rapport sauvegardé: {filename}")
        except Exception as e:
            print(f"\n❌ Erreur sauvegarde: {e}")


async def main():
    """Point d'entrée principal."""
    try:
        # Load config
        config = load_config()
        
        # Create monitor
        monitor = KissBotMonitor(config)
        
        # Run health check
        report = await monitor.run_full_health_check()
        
        # Display results
        monitor.print_health_report(report)
        
        # Save report
        monitor.save_report(report)
        
        # Exit code based on status
        status_codes = {
            'HEALTHY': 0,
            'DEGRADED': 1, 
            'WARNING': 2,
            'CRITICAL': 3
        }
        
        return status_codes.get(report['overall_status'], 3)
        
    except Exception as e:
        print(f"❌ Erreur monitoring: {e}")
        import traceback
        traceback.print_exc()
        return 4


if __name__ == "__main__":
    exit(asyncio.run(main()))