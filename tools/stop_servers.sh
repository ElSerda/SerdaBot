#!/bin/bash

echo "🛑 [SerdaBot] Arrêt des serveurs..."

# Kill Uvicorn
UVICORN_PIDS=$(ps aux | grep "uvicorn src.core.server.api_server:app" | grep -v grep | awk '{print $2}')
if [ -n "$UVICORN_PIDS" ]; then
    echo "🔪 Arrêt de Uvicorn (PID: $UVICORN_PIDS)"
    kill $UVICORN_PIDS
else
    echo "✅ Aucun processus Uvicorn à arrêter."
fi

# Kill LibreTranslate
LT_PIDS=$(ps aux | grep "[l]ibretranslate" | awk '{print $2}')
if [ -n "$LT_PIDS" ]; then
    echo "🔪 Arrêt de LibreTranslate (PID: $LT_PIDS)"
    kill $LT_PIDS
else
    echo "✅ Aucun processus LibreTranslate à arrêter."
fi

echo "✅ Tous les serveurs ont été arrêtés."
