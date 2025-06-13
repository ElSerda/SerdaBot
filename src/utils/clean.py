# src/utils/clean.py

import re


# Nettoyage général d'une réponse générée par un modèle
def clean_response(text: str, max_length: int = None) -> str:
    if not text:
        return ''

    # Supprimer balises ChatML ou tokens résiduels
    text = re.sub(r'<\|im_start\|>.*?<\|im_end\|>', '', text, flags=re.DOTALL)
    text = text.replace('<|im_end|>', '').replace('<|im_start|>', '')
    text = re.sub(r'^assistant: ?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^user: ?', '', text, flags=re.IGNORECASE)

    # Nettoyage Markdown ou artefacts
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # gras
    text = re.sub(r'`(.*?)`', r'\1', text)  # inline code
    text = text.replace('##', '').replace('#', '')
    text = text.strip()

    # Tronquer si nécessaire
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip()

    return text
