import os


def load_prompt_template(name, lang='en'):
    """
    Load a prompt template by name and language (default = 'en').
    """
    # Toujours basé sur le chemin réel du fichier prompt_loader.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f'prompt_{name}_{lang}.txt'
    path = os.path.join(current_dir, filename)

    if not os.path.isfile(path):
        fallback_path = os.path.join(current_dir, f'prompt_{name}_en.txt')
        if os.path.isfile(fallback_path):
            path = fallback_path
        else:
            raise FileNotFoundError(
                f'Prompt file not found: {path} or fallback {fallback_path}'
            )

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
