import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.config import load_config
from src.utils.llm import query_model
from src.utils.log import log_response

# === Détection ROOT_DIR dynamique ===
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT_DIR, 'pyproject.toml')) and ROOT_DIR != '/':
    ROOT_DIR = os.path.dirname(ROOT_DIR)
sys.path.insert(0, ROOT_DIR)
print('📁 ROOT_DIR =', ROOT_DIR)

# === Imports projet ===


# === Chargement config ===
CONFIG = load_config()
print('✅ config.yaml chargé :', CONFIG)

# === Initialisation FastAPI ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# === Classes ===
class ChatRequest(BaseModel):
    prompt: str
    user: str = 'user'


class ChatResponse(BaseModel):
    response: str


# === Endpoints ===
@app.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest):
    response = await query_model(req.prompt, config=CONFIG)
    log_response(req.prompt, response, user=req.user)
    return {'response': response}


@app.get('/')
async def root():
    return {'message': '🧠 SerdaBot API ready.'}


# === Lancement manuel ===
if __name__ == '__main__':
    print('🧠 Modèle exécuté sur :', 'GPU' if CONFIG['bot'].get('use_gpu') else 'CPU')
    print('🚀 Serveur API actif sur http://127.0.0.1:8000')
    uvicorn.run(
        'src.core.server.api_server:app', host='127.0.0.1', port=8000, reload=False
    )
