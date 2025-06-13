#!/bin/bash

echo "🔁 [SerdaBot] Reload des serveurs..."

bash tools/stop_servers.sh
sleep 1
bash tools/start_servers.sh
