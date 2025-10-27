"""See docs/api/intelligence_handler.md"""

import logging
import random
import httpx
from typing import Dict, Optional

class ModelPromptOptimizer:
    """See docs/api/intelligence_handler.md"""
    
    @staticmethod
    def get_system_prompt(provider: str, context: str, bot_name: str, model_type: str = "") -> str:
        """See docs/api/intelligence_handler.md"""
        import logging
        logger = logging.getLogger(__name__)
        
        provider_lower = provider.lower()
        logger.info(f"🧠 ModelPromptOptimizer: Provider '{provider}' -> '{provider_lower}' (model: {model_type})")
        
        if "ollama" in provider_lower or "local" in provider_lower:
            prompt = f"Tu es {bot_name}, bot Twitch gaming. Réponds en français, factuel et concis, max 150 chars. {context}"
            logger.info(f"🦙 Prompt OLLAMA/LOCAL optimisé sélectionné")
            return prompt
            
        elif "openai" in provider_lower or "gpt" in provider_lower:
            prompt = f"You are {bot_name}, a sarcastic assistant on Twitch. Be helpful and concise. Context: {context}"
            logger.info(f"� Prompt OPENAI optimisé sélectionné")
            return prompt
            
        elif "lm_studio" in provider_lower or "lmstudio" in provider_lower:
            prompt = f"Tu es {bot_name}, assistant sarcastique Twitch. Réponds précisément en français, max 150 chars. {context}"
            logger.info(f"🔥 Prompt LM_STUDIO optimisé sélectionné")
            return prompt
            
        else:
            prompt = f"Tu es {bot_name}, bot Twitch gaming. Réponds en français, max 150 chars. {context}"
            logger.info(f"🔧 Prompt GENERIQUE utilisé (provider '{provider}' non reconnu)")
            return prompt

class LLMHandler:
    """See docs/api/intelligence_handler.md"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        apis_config = config.get('apis', {})
        llm_config = config.get('llm', {})
        
        self.provider = llm_config.get('provider', 'local')
        self.local_llm_enabled = llm_config.get('local_llm', True)
        self.local_endpoint = llm_config.get('model_endpoint') if self.local_llm_enabled else None
        self.local_model = llm_config.get('model_name', 'qwen2.5-7b-instruct')
        self.openai_key = apis_config.get('openai_key')
        self.openai_model = llm_config.get('openai_model', 'gpt-3.5-turbo')
        
        self.max_tokens_ask = llm_config.get('max_tokens_ask', 150)
        self.max_tokens_mention = llm_config.get('max_tokens_mention', 80)
        self.temperature_ask = llm_config.get('temperature_ask', 0.7)
        self.temperature_mention = llm_config.get('temperature_mention', 0.9)
        
        self.bot_name = config.get('bot', {}).get('name', 'UnknownBot')
        self.personality = config.get('bot', {}).get('personality', 'sympa, direct, et passionné de tech')
        
        self.use_personality_on_mention = llm_config.get('use_personality_on_mention', True)
        self.use_personality_on_ask = llm_config.get('use_personality_on_ask', False)
        self.personality_only_on_cloud = llm_config.get('personality_only_on_cloud', True)
        
        self.failed_endpoints: set[str] = set()
        
        self.enabled = bool(self.local_endpoint or self.openai_key)
        if self.enabled:
            local_status = "✅ ON" if self.local_llm_enabled else "❌ OFF"
            openai_status = "✅" if self.openai_key else "❌"
            self.logger.info(f"🤖 LLM configuré - Local: {local_status} | OpenAI: {openai_status} | Provider: {self.provider}")

        else:
            self.logger.warning("⚠️ Aucun LLM configuré - Mode répliques fun uniquement")
    
    def update_bot_name(self, twitch_name: str) -> None:
        """See docs/api/intelligence_handler.md"""
        old_name = self.bot_name
        self.bot_name = twitch_name
        self.logger.info(f"🏷️ Bot name updated: '{old_name}' → '{twitch_name}'")
    
    async def generate_response(self, prompt: str, context: str = "general", user_name: str = "") -> Optional[str]:
        """See docs/api/intelligence_handler.md"""
        
        if not self.enabled:
            return self.get_fallback_response(context, user_name)
        
        if context == "ask":
            max_tokens = self.max_tokens_ask
            temperature = self.temperature_ask
        else:
            max_tokens = self.max_tokens_mention
            temperature = self.temperature_mention
        
        model_type = self._detect_model_type()
        system_prompt = ModelPromptOptimizer.get_system_prompt(
            model_type, context, self.bot_name, self.provider
        )
        self.logger.info(f"🚀 Optimisation activée: provider={self.provider}, model={model_type}, context={context}")
        
        if self.local_llm_enabled:
            response = await self._try_local(prompt, system_prompt, max_tokens, temperature)
            if response:
                return response
            self.logger.warning("LLM local échoué, tentative OpenAI...")
        
        if self.openai_key:
            response = await self._try_openai(prompt, system_prompt, max_tokens, temperature)
            if response:
                return response
            self.logger.warning("OpenAI échoué, fallback statique...")
        
        return self.get_fallback_response(context, user_name)
    async def _try_openai(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """See docs/api/intelligence_handler.md"""
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
            error_str = str(e).lower()
            if any(word in error_str for word in ['quota', 'rate limit', 'billing', 'insufficient']):
                self.logger.warning("🚨 OpenAI quota/rate limit atteint!")
        
        return None
    
    async def _check_local_health(self) -> bool:
        """See docs/api/intelligence_handler.md"""
        try:
            base_url = self.local_endpoint.replace('/chat/completions', '/models') if self.local_endpoint else "http://127.0.0.1:1234/v1/models"
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(base_url)
                return response.status_code == 200
        except Exception:
            return False

    async def _try_local(self, prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """See docs/api/intelligence_handler.md"""
        if not self.local_llm_enabled:
            self.logger.debug("🔇 Local LLM désactivé via config")
            return None
        
        if not await self._check_local_health():
            self.logger.warning("💀 Local LLM health check échoué - skip direct")
            return None
            
        try:
            payload = {
                "model": self.local_model,
                "messages": [
                    {"role": "user", "content": f"{system_prompt}\n\n{prompt}"}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            self.logger.info(f"🔍 LM Studio payload: model={self.local_model}, temp={temperature}, max_tokens={max_tokens}")
            self.logger.debug(f"📝 Messages: {payload['messages']}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.local_endpoint, json=payload)
                
                self.logger.info(f"🌐 LM Studio status: {response.status_code}")
                if response.status_code != 200:
                    self.logger.error(f"❌ LM Studio error response: {response.text}")
                
                response.raise_for_status()
                
                data = response.json()
                if "choices" in data and data["choices"]:
                    raw_response = data["choices"][0]["message"]["content"]
                    cleaned_response = raw_response.strip() if raw_response else ""
                    
                    if cleaned_response:
                        self.failed_endpoints.discard("local")
                        return cleaned_response
                    else:
                        self.logger.warning("⚠️ LLM a retourné une réponse vide!")
                        return None
                
        except Exception as e:
            self.logger.error(f"Local LLM error: {e}")
        
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
        """See docs/api/intelligence_handler.md"""
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
