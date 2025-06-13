import os
from datetime import datetime


def log_response(
    prompt: str,
    response: str,
    user: str = 'unknown',
    score: int = -1,
    enabled: bool = True,
    log_dir: str = 'logs',
):
    if not enabled:
        return

    try:
        os.makedirs(log_dir, exist_ok=True)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        filepath = os.path.join(log_dir, f'{today}_responses.log')

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.utcnow().isoformat()}] @{user}\n')
            f.write(f'Prompt: {prompt}\n')
            f.write(f'Response: {response}\n')
            f.write(f'Score: {score}/5\n')
            f.write('-' * 40 + '\n')
    except Exception as e:
        print(f'❌ Failed to log response: {e}')
