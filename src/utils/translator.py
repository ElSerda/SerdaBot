"""
Simple Translator - Version Légère
===================================

Traduction automatique pour devs anglophones.
Pas de over-engineering, juste ce qu'il faut.
"""

import json
from pathlib import Path

from deep_translator import GoogleTranslator


class Translator:
    """Traducteur simple avec whitelist devs"""

    def __init__(self, devs_file='data/devs.json', blocked_file='data/blocked_sites.json',
                 bot_whitelist_file='data/bot_whitelist.json',
                 bot_blacklist_file='data/bot_blacklist.json'):
        self.translator_en_fr = GoogleTranslator(source='en', target='fr')
        self.translator_fr_en = GoogleTranslator(source='fr', target='en')

        self.devs_file = Path(devs_file)
        self.blocked_file = Path(blocked_file)
        self.bot_whitelist_file = Path(bot_whitelist_file)
        self.bot_blacklist_file = Path(bot_blacklist_file)

        self.devs = self._load_json(self.devs_file, set())
        self.blocked_sites = self._load_json(self.blocked_file, set())
        self.bot_whitelist = self._load_json(self.bot_whitelist_file, set())
        self.bot_blacklist = self._load_json(self.bot_blacklist_file, set())

    def _load_json(self, filepath, default):
        """Charge un fichier JSON ou retourne default"""
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(list(default) if isinstance(default, set) else default, f)
            return default

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return set(data) if isinstance(default, set) else data
        except:
            return default

    def _save_json(self, filepath, data):
        """Sauvegarde dans un fichier JSON"""
        with open(filepath, 'w') as f:
            json.dump(sorted(list(data)) if isinstance(data, set) else data, f, indent=2)

    # === DEVS WHITELIST ===

    def add_dev(self, username):
        """Ajoute un dev à la whitelist"""
        username = username.lower().strip('@')
        self.devs.add(username)
        self._save_json(self.devs_file, self.devs)
        return True

    def remove_dev(self, username):
        """Retire un dev de la whitelist"""
        username = username.lower().strip('@')
        if username in self.devs:
            self.devs.remove(username)
            self._save_json(self.devs_file, self.devs)
            return True
        return False

    def is_dev(self, username):
        """Vérifie si username est un dev whitelisté"""
        return username.lower() in self.devs

    def get_devs(self):
        """Retourne la liste des devs"""
        return sorted(list(self.devs))

    # === BLOCKED SITES ===

    def add_blocked_site(self, site):
        """Ajoute un site à la blacklist (ex: 'streamboo')"""
        site = site.lower().strip()
        self.blocked_sites.add(site)
        self._save_json(self.blocked_file, self.blocked_sites)
        return True

    def remove_blocked_site(self, site):
        """Retire un site de la blacklist"""
        site = site.lower().strip()
        if site in self.blocked_sites:
            self.blocked_sites.remove(site)
            self._save_json(self.blocked_file, self.blocked_sites)
            return True
        return False

    def is_spam_bot(self, username, message=None, channel_owner=None):
        """
        Détecte si c'est un spam bot.
        Vérifie si le username ou le message contient un site bloqué.
        EXCLUT le propriétaire du channel et les devs whitelistés.
        """
        username_lower = username.lower()
        message_lower = message.lower() if message else ""

        # Exclure le propriétaire du channel
        if channel_owner and username_lower == channel_owner.lower():
            return False

        # Exclure les devs whitelistés
        if self.is_dev(username):
            return False

        # Check si le username contient un site bloqué
        for site in self.blocked_sites:
            if site in username_lower or (message and site in message_lower):
                return True

        return False

    def get_blocked_sites(self):
        """Retourne la liste des sites bloqués"""
        return sorted(list(self.blocked_sites))

    # === BOT WHITELIST / BLACKLIST ===

    def add_bot_to_whitelist(self, bot_name):
        """Ajoute un bot à la whitelist (SerdaBot ne lui répondra jamais)"""
        bot_name = bot_name.lower().strip('@')
        self.bot_whitelist.add(bot_name)
        self._save_json(self.bot_whitelist_file, self.bot_whitelist)
        return True

    def remove_bot_from_whitelist(self, bot_name):
        """Retire un bot de la whitelist"""
        bot_name = bot_name.lower().strip('@')
        if bot_name in self.bot_whitelist:
            self.bot_whitelist.remove(bot_name)
            self._save_json(self.bot_whitelist_file, self.bot_whitelist)
            return True
        return False

    def add_bot_to_blacklist(self, bot_name):
        """Ajoute un bot à la blacklist (SerdaBot ignorera tous ses messages)"""
        bot_name = bot_name.lower().strip('@')
        self.bot_blacklist.add(bot_name)
        self._save_json(self.bot_blacklist_file, self.bot_blacklist)
        return True

    def remove_bot_from_blacklist(self, bot_name):
        """Retire un bot de la blacklist"""
        bot_name = bot_name.lower().strip('@')
        if bot_name in self.bot_blacklist:
            self.bot_blacklist.remove(bot_name)
            self._save_json(self.bot_blacklist_file, self.bot_blacklist)
            return True
        return False

    def is_bot_whitelisted(self, bot_name):
        """Vérifie si un bot est dans la whitelist"""
        return bot_name.lower() in self.bot_whitelist

    def is_bot_blacklisted(self, bot_name):
        """Vérifie si un bot est dans la blacklist"""
        return bot_name.lower() in self.bot_blacklist

    def get_whitelisted_bots(self):
        """Retourne la liste des bots whitelistés"""
        return sorted(list(self.bot_whitelist))

    def get_blacklisted_bots(self):
        """Retourne la liste des bots blacklistés"""
        return sorted(list(self.bot_blacklist))

    def should_ignore_bot(self, username):
        """
        Détermine si SerdaBot doit ignorer ce bot.
        - Si bot est dans la whitelist → IGNORER (ne pas répondre)
        - Si bot est dans la blacklist → IGNORER (bloquer complètement)
        """
        username_lower = username.lower()
        return self.is_bot_whitelisted(username_lower) or self.is_bot_blacklisted(username_lower)

    # === TRADUCTION ===

    def should_translate(self, user, text):
        """
        Détermine si on doit traduire automatiquement.

        Règles:
        - User doit être un dev whitelisté
        - Pas une commande (!cmd)
        - Message assez long (>= 3 mots)
        """
        return (
            self.is_dev(user) and
            not text.strip().startswith('!') and
            len(text.split()) >= 3
        )

    def translate(self, text, source='en', target='fr'):
        """
        Traduit un texte.

        Args:
            text: Texte à traduire
            source: Langue source ('en' ou 'fr')
            target: Langue cible ('en' ou 'fr')

        Returns:
            Texte traduit ou None si erreur
        """
        try:
            if source == 'en' and target == 'fr':
                return self.translator_en_fr.translate(text)
            elif source == 'fr' and target == 'en':
                return self.translator_fr_en.translate(text)
            return None
        except Exception as e:
            error_str = str(e).lower()
            print(f"Translation error: {e}")

            # Gestion spécifique des erreurs de traduction
            # NOTE: On ne renvoie PLUS le texte original dans l'erreur (évite spam)
            if 'quota' in error_str or 'limit' in error_str:
                print("🚨 [TRANSLATOR] Quota Google Translate épuisé!")
                return "⚠️ Traduction temporairement indisponible (quota dépassé)"

            elif 'network' in error_str or 'timeout' in error_str or 'connection' in error_str:
                print("🚨 [TRANSLATOR] Problème de connexion Google Translate")
                return "⚠️ Erreur réseau - Service de traduction inaccessible"

            elif 'blocked' in error_str or 'forbidden' in error_str:
                print("🚨 [TRANSLATOR] Service de traduction bloqué!")
                return "⚠️ Service de traduction bloqué"

            else:
                print(f"🚨 [TRANSLATOR] Erreur inconnue: {e}")
                return "⚠️ Erreur de traduction (service indisponible)"
