#!/usr/bin/env python3
"""
🔄 Wrapper de Redémarrage Automatique

Lance le bot et le redémarre automatiquement en cas de crash ou déconnexion.
C'est la solution de production pour gérer les reconnexions.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config import load_config
from src.chat.twitch_bot import TwitchBot


class AutoRestartBot:
    """Wrapper qui redémarre automatiquement le bot."""
    
    def __init__(self, max_restarts=None, restart_delay=5):
        """
        Args:
            max_restarts: Nombre max de redémarrages (None = illimité)
            restart_delay: Délai entre les redémarrages (secondes)
        """
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.start_time = time.time()
    
    async def run(self):
        """Lance le bot avec redémarrage automatique."""
        while True:
            try:
                if self.max_restarts and self.restart_count >= self.max_restarts:
                    print(f"\n❌ Nombre maximum de redémarrages atteint ({self.max_restarts})")
                    break
                
                if self.restart_count > 0:
                    print(f"\n🔄 Redémarrage #{self.restart_count}...")
                    print(f"⏳ Attente de {self.restart_delay} secondes...\n")
                    await asyncio.sleep(self.restart_delay)
                
                # Charge la config à chaque redémarrage (au cas où elle change)
                config = load_config()
                bot = TwitchBot(config)
                
                print(f"\n🚀 Démarrage du bot (tentative #{self.restart_count + 1})...")
                print(f"⏰ Heure: {datetime.now().strftime('%H:%M:%S')}\n")
                
                await bot.start()
                
            except KeyboardInterrupt:
                print("\n\n👋 Arrêt manuel détecté")
                break
            except SystemExit as e:
                if e.code == 0:
                    print("\n✅ Bot arrêté proprement")
                    break
                else:
                    print(f"\n⚠️ Bot arrêté avec code {e.code}")
                    self.restart_count += 1
            except Exception as e:
                print(f"\n❌ Erreur: {e}")
                import traceback
                traceback.print_exc()
                self.restart_count += 1
        
        uptime = time.time() - self.start_time
        print(f"\n📊 Statistiques:")
        print(f"   - Uptime total: {uptime:.1f}s")
        print(f"   - Redémarrages: {self.restart_count}")
        print(f"   - Moyenne: {uptime/(self.restart_count+1):.1f}s par session\n")


async def main():
    print("\n" + "🔄 " + "="*57)
    print("   SERDABOT - Mode Redémarrage Automatique")
    print("="*60)
    print("\n💡 Le bot redémarrera automatiquement en cas de:")
    print("   - Perte de connexion réseau")
    print("   - Crash inattendu")
    print("   - Fermeture du websocket")
    print("\n📌 CTRL+C pour arrêter définitivement\n")
    print("="*60 + "\n")
    
    # Redémarrages illimités avec 5s de délai
    wrapper = AutoRestartBot(max_restarts=None, restart_delay=5)
    await wrapper.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye!\n")
