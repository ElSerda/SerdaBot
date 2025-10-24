"""
KissBot V1 - LLM Handler KISS avec cascade fallback + Model-Specific Prompting
Version simplifiée inspirée de SerdaBot avec randomizer El_Serda + optimisation prompts !
"""

import logging
import random
import httpx
from typing import Dict, Optional


class ModelPromptOptimizer:
    """Optimiseur de prompts par modèle - Version KISS."""
    
    @staticmethod
    def get_system_prompt(model_type: str, context: str, bot_name: str) -> str:
        """Retourne le prompt système optimisé par modèle."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Détection modèle simple
        model_lower = model_type.lower()
        logger.info(f"🧠 ModelPromptOptimizer: Détection modèle '{model_type}' -> '{model_lower}'")
        
        if "qwen" in model_lower:
            prompt = f"Tu es {bot_name}, bot Twitch. Réponds en français, factuel et concis, max 150 chars. {context}"
            logger.info(f"🎯 Prompt QWEN optimisé sélectionné")
            return prompt
            
        elif "llama" in model_lower:
            prompt = f"Tu es {bot_name}, assistant gaming sur Twitch. Sois concis et utile. {context}"
            logger.info(f"🦙 Prompt LLAMA optimisé sélectionné")
            return prompt
            
        elif "gpt" in model_lower or "openai" in model_lower:
            prompt = f"You are {bot_name}, a gaming expert on Twitch. Be helpful and concise. Context: {context}"
            logger.info(f"🤖 Prompt OPENAI optimisé sélectionné")
            return prompt
            
        else:
            # Fallback générique
            prompt = f"Tu es {bot_name}, bot Twitch gaming. Réponds en français, max 150 chars. {context}"
            logger.info(f"🔧 Prompt GENERIQUE utilisé (fallback)")
            return prompt


class LLMHandler:
    """Handler LLM KISS avec cascade à 3 niveaux."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        apis_config = config.get('apis', {})
        llm_config = config.get('llm', {})
        
        # Configuration avec option local_llm ON/OFF
        self.provider = llm_config.get('provider', 'local')
        self.local_llm_enabled = llm_config.get('local_llm', True)  # 🔥 ON/OFF pour LM Studio
        self.local_endpoint = llm_config.get('model_endpoint') if self.local_llm_enabled else None
        self.local_model = llm_config.get('model_name', 'qwen2.5-7b-instruct')
        self.openai_key = apis_config.get('openai_key')
        self.openai_model = llm_config.get('openai_model', 'gpt-3.5-turbo')
        
        # Paramètres
        self.max_tokens_ask = llm_config.get('max_tokens_ask', 150)
        self.max_tokens_mention = llm_config.get('max_tokens_mention', 80)
        self.temperature_ask = llm_config.get('temperature_ask', 0.7)
        self.temperature_mention = llm_config.get('temperature_mention', 0.9)
        
        # 🎭 Bot personality from config (fallback)
        self.bot_name = config.get('bot', {}).get('name', 'UnknownBot')  # Fallback avant TwitchIO
        self.personality = config.get('bot', {}).get('personality', 'sympa, direct, et passionné de tech')
        
        # 🎯 Flag: Utiliser personality selon contexte ET modèle
        # ask/command = CLEAN (factuel)
        # mention/chill = PERSONALITY
        self.use_personality_on_mention = llm_config.get('use_personality_on_mention', True)
        self.use_personality_on_ask = llm_config.get('use_personality_on_ask', False)
        self.personality_only_on_cloud = llm_config.get('personality_only_on_cloud', True)  # 💡 Genius mode
        

        
        # Cache des endpoints échoués (style SerdaBot mais simple)
        self.failed_endpoints: set[str] = set()
        
        # Validation et logs
        self.enabled = bool(self.local_endpoint or self.openai_key)
        if self.enabled:
            local_status = "✅ ON" if self.local_llm_enabled else "❌ OFF"
            openai_status = "✅" if self.openai_key else "❌"
            self.logger.info(f"🤖 LLM configuré - Local: {local_status} | OpenAI: {openai_status} | Provider: {self.provider}")

        else:
            self.logger.warning("⚠️ Aucun LLM configuré - Mode répliques fun uniquement")
    
    def update_bot_name(self, twitch_name: str) -> None:
        """🔄 Met à jour le nom du bot avec le vrai nom TwitchIO."""
        old_name = self.bot_name
        self.bot_name = twitch_name
        self.logger.info(f"🏷️ Bot name updated: '{old_name}' → '{twitch_name}'")
    
    async def generate_response(self, prompt: str, context: str = "general", user_name: str = "") -> Optional[str]:
        """Génère une réponse LLM avec fallback cascade."""
        
        # Si LLM désactivé → fallback
        if not self.enabled:
            return self.get_fallback_response(context, user_name)
        
        # Paramètres selon contexte
        if context == "ask":
            max_tokens = self.max_tokens_ask
            temperature = self.temperature_ask
        else:
            max_tokens = self.max_tokens_mention
            temperature = self.temperature_mention
        
        # 🎯 OPTIMISATION MODEL-SPECIFIC PROMPTING
        model_type = self._detect_model_type()
        system_prompt = ModelPromptOptimizer.get_system_prompt(
            model_type, context, self.bot_name
        )
        self.logger.info(f"🚀 Optimisation activée: modèle={model_type}, context={context}")
        
        # Tentative local en premier
        if self.local_llm_enabled:
            response = await self._try_local(prompt, system_prompt, max_tokens, temperature)
            if response:
                return response
            self.logger.warning("LLM local échoué, tentative OpenAI...")
        
        # Fallback OpenAI
        if self.openai_key:
            response = await self._try_openai(prompt, system_prompt, max_tokens, temperature)
            if response:
                return response
            self.logger.warning("OpenAI échoué, fallback statique...")
        
        # Fallback statique final
        return self.get_fallback_response(context, user_name)
    async def _try_openai(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Essai OpenAI avec gestion d'erreur et quota."""
        try:
            payload = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post("https://api.openai.com/v1/chat/completions", 
                                           json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            self.logger.error(f"💥 ERREUR OPENAI DÉTAILLÉE: {e}")
            # Gestion spéciale quota/rate limit
            error_str = str(e).lower()
            if any(word in error_str for word in ['quota', 'rate limit', 'billing', 'insufficient']):
                self.logger.warning("🚨 OpenAI quota/rate limit atteint!")
        
        return None
    
    async def _check_local_health(self) -> bool:
        """🏥 Health check rapide du LLM local (2s max)."""
        try:
            base_url = self.local_endpoint.replace('/chat/completions', '/models') if self.local_endpoint else "http://127.0.0.1:1234/v1/models"
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(base_url)
                return response.status_code == 200
        except Exception:
            return False

    async def _try_local(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Essai Local LM Studio avec health check préalable."""
        if not self.local_llm_enabled:
            self.logger.debug("🔇 Local LLM désactivé via config")
            return None
        
        # 🏥 Health check rapide d'abord
        if not await self._check_local_health():
            self.logger.warning("💀 Local LLM health check échoué - skip direct")
            # Cache temporaire désactivé pour permettre retry
            # self.failed_endpoints.add("local")
            return None
            
        try:
            payload = {
                "model": self.local_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.local_endpoint, json=payload)
                response.raise_for_status()
                
                data = response.json()
                if "choices" in data and data["choices"]:
                    raw_response = data["choices"][0]["message"]["content"]
                    cleaned_response = raw_response.strip() if raw_response else ""
                    
                    if cleaned_response:
                        # Succès → retirer du cache d'échec (style SerdaBot)
                        self.failed_endpoints.discard("local")
                        return cleaned_response
                    else:
                        self.logger.warning("⚠️ LLM a retourné une réponse vide!")
                        return None
                
        except Exception as e:
            self.logger.error(f"Local LLM error: {e}")
            # Note: Cache d'échec non implémenté par choix KISS
        
        return None
    
    def _get_fun_fallback(self, context: str, user_name: str = "") -> str:
        """Répliques de fallback simples."""
        
        fallbacks = {
            "ask": [
                "🤔 Je réfléchis... 💭",
                "Mon cerveau est en pause café ☕",
                "Question intéressante ! Mais mon IA fait la sieste 😴",
                "Désolé, mes neurones sont en mode économie d'énergie 🔋",
                "Sans mon LLM, je suis juste un bot qui dit des trucs random 🤷"
            ],
            "mention": [
                "Hey ! Tu m'appelles ? 📞", 
                "Présent ! 🙋‍♂️", 
                "Ouais ? 😏", 
                "Tu veux quoi chef ? 👨‍💼", 
                "J'écoute ! 👂"
            ],
            "general": [
                "🤖 Bip boop, je suis là !", 
                "Mode robot activé ! 🚀", 
                "Prêt à vous servir ! 🫡", 
                "En ligne ! ⚡"
            ]
        }
        
        responses = fallbacks.get(context, fallbacks["general"])
        return random.choice(responses)
    
    def _detect_model_type(self) -> str:
        """Détecte le type de modèle en cours d'utilisation - Version KISS."""
        if self.local_llm_enabled and self.local_model:
            self.logger.info(f"🔍 Modèle détecté: LOCAL -> '{self.local_model}'")
            return self.local_model
        elif self.openai_key and self.openai_model:
            self.logger.info(f"🔍 Modèle détecté: OPENAI -> '{self.openai_model}'")
            return self.openai_model
        else:
            self.logger.info(f"🔍 Modèle détecté: DEFAULT (aucun modèle configuré)")
            return "default"

    def get_fallback_response(self, context: str, user_name: str = "") -> str:
        """Fallback statique simple."""
        fallbacks = {
            "ask": "Désolé, mon IA n'est pas disponible. Essayez plus tard ! 🤖",
            "mention": "Salut ! Mon IA fait une pause mais je suis là ! 👋",
            "general": "Hmm, intéressant... 🤔"
        }
        return fallbacks.get(context, fallbacks["general"])
