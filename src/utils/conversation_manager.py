# src/utils/conversation_manager.py

import time
import threading
from collections import defaultdict
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class ConversationState:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    pending: Optional[Dict[str, Any]] = None
    last_activity_monotonic: float = field(default_factory=time.monotonic)
    lock: threading.Lock = field(default_factory=threading.Lock)

class ConversationManager:
    def __init__(self, ttl_seconds: int = 420, max_messages: int = 12):
        self._ttl_seconds = ttl_seconds
        self._max_messages = max_messages
        self._states: Dict[str, ConversationState] = {}
        # On ne stocke pas les locks ici séparément — ils sont dans ConversationState
        self._cache: Dict[Tuple[str, int], Tuple[float, Any]] = {}  # (key) -> (time.time(), value)
        self._cache_lock = threading.Lock()
        self._global_lock = threading.RLock()  # pour accès à _states

        self.start_cleanup_thread()

    def get(self, user_id: str) -> ConversationState:
        with self._global_lock:
            if user_id not in self._states:
                self._states[user_id] = ConversationState()
            state = self._states[user_id]
        # Mettre à jour l'activité à chaque accès
        state.last_activity_monotonic = time.monotonic()
        return state

    def add_message(self, user_id: str, role: str, content: str, ts: Optional[float] = None):
        state = self.get(user_id)
        with state.lock:
            state.messages.append({
                "role": role,
                "content": content,
                "timestamp_monotonic": ts or time.monotonic()
            })
            self.prune_messages(user_id, keep_last=self._max_messages)

    def set_pending(self, user_id: str, type_: str, data: dict, ts: Optional[float] = None):
        state = self.get(user_id)
        with state.lock:
            state.pending = {
                "type": type_,
                "data": data,
                "asked_at_monotonic": ts or time.monotonic()
            }

    def consume_pending(self, user_id: str) -> Optional[dict]:
        state = self.get(user_id)
        with state.lock:
            pending = state.pending
            state.pending = None
            return pending

    def touch(self, user_id: str):
        state = self.get(user_id)
        with state.lock:
            state.last_activity_monotonic = time.monotonic()

    def prune_messages(self, user_id: str, keep_last: int = 12):
        state = self.get(user_id)
        with state.lock:
            if len(state.messages) > keep_last:
                state.messages = state.messages[-keep_last:]

    def cleanup_expired(self, now_mono: float):
        with self._global_lock:
            expired_users = [
                uid for uid, state in self._states.items()
                if now_mono - state.last_activity_monotonic > self._ttl_seconds
            ]
            for uid in expired_users:
                # Acquérir le lock utilisateur avant suppression (sécurité)
                with self._states[uid].lock:
                    del self._states[uid]

    # --- Cache L1 (mémoire, 60s TTL) ---
    def cache_get(self, key: Tuple[str, int]) -> Optional[Any]:
        with self._cache_lock:
            if key in self._cache:
                ts, value = self._cache[key]
                if time.time() - ts <= 60:
                    return value
                else:
                    del self._cache[key]
        return None

    def cache_set(self, key: Tuple[str, int], value: Any, ttl: int = 60):
        with self._cache_lock:
            self._cache[key] = (time.time(), value)

    def _prune_cache(self):
        now = time.time()
        with self._cache_lock:
            expired_keys = [k for k, (ts, _) in self._cache.items() if now - ts > 60]
            for k in expired_keys:
                del self._cache[k]

    # --- Thread de cleanup ---
    def start_cleanup_thread(self):
        def cleanup_loop():
            while True:
                time.sleep(60)
                now = time.monotonic()
                self.cleanup_expired(now)
                self._prune_cache()

        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
