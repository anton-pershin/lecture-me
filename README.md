# Lecture me
An LLM-backed Telegram bot for self-education over your own notes

## Getting started

1. Create a virtual environment, e.g.
```bash
conda create -n myenv python=3.12
conda activate myenv
```
2. Install necessary packages
```bash
pip install -r requirements.txt
```
3. Set up tokens in `/config/user_settings/user_settings.yaml` and an LLM in `/config/llm`
4. Run `/lecture_me/scripts/main.py` and do not forget to modify the corresponding config file in `/config/config_main.yaml'
```bash
python lecture_me/scripts/main.py
```

⚠️  DO NOT commit your `user_settings.yaml`

## Scripts

### `main.py`

Runs a Telegram bot server handling user requests

#### Configuration

1. In `user_settings.yaml`, set up your bot token and notes directory:
   ```yaml
    telegram_bot_token: YOUR_TOKEN
    notes_directory: /path/to/notes
   ```

2. In `config_main.yaml`, choose your LLM:
    ```yaml
    llm: ...
    ```
