# Poketwo Autocatcher

Discord self-bot for Poketwo with AI-based image prediction, hint fallback, cooldown guards, and runtime safety controls.

## Features

- AI catch predictions with configurable confidence threshold.
- Automatic fallback to hint requests when confidence is low or AI processing fails.
- Regex hint solver using local Pokemon name data.
- Cooldown-based send control for catch/hint commands.
- Captcha-aware pause mode with runtime-state persistence across restarts.
- Owner controls: `!say`, `!react`, and `!solved`.

## Project layout

- `bot/main/main.py` - Main runtime and event handlers.
- `bot/main/config.py` - Environment-based configuration loader.
- `bot/main/requirements.txt` - Pinned Python dependencies.
- `bot/class_names.json` - Class label map for AI model output.
- `bot/pokemon_model_lite.pth` - Trained model weights.
- `bot/data.txt` - Name list used by hint solver.

## Quick start

1. Clone:

```bash
git clone https://github.com/amansingh903/Poketwo-Autocatcher.git
cd Poketwo-Autocatcher
```

2. Install dependencies (Python 3.12 only):

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r bot/main/requirements.txt
```

This project supports Python `3.12` only.

3. Configure environment variables (or a `.env` file in repo root).

### Required

- `DISCORD_TOKEN` - your user token.
- `GUILD_ID` - Guild/server where the bot should operate.

### Optional

- `OWNER_ID` - Discord user ID allowed to run owner commands (`!say`, `!react`, `!solved`).
- `CATCH_CHANNEL_ID` - Channel ID used by hint solver fallback.
- `SPAM_CHANNEL_ID` - Channel used by spam loop.
- `CATCH_ENABLED` - `true/false`, default `true`.
- `SPAM_ENABLED` - `true/false`, default `true`.
- `START_SLEEPING` - `true/false`, default `false`.
- `AI_CONFIDENCE_THRESHOLD` - default `0.72`, range `(0, 1]`.
- `CATCH_COOLDOWN_SECONDS` - default `1.2`, must be `> 0`.
- `HINT_COOLDOWN_SECONDS` - default `1.0`, must be `> 0`.
- `STATE_FILE_PATH` - default `bot/runtime_state.json`.



4. Launch:

```bash
python bot/main/main.py
```

## Commands

- `!say <text>` - Send a message from your account.
- `!react <message_id> <emoji>` - React to a message in the current channel.
- `!solved` - Resume spam mode after captcha resolution.
- `!togglecatch` - Toggle catch flow on/off.
- `!togglespam` - Toggle spam flow on/off.

## Notes

- The bot validates startup config and model/class compatibility.
- Runtime state (sleeping flag, last captcha time, last caught name) is saved to `STATE_FILE_PATH`.
- Catching only runs in `CATCH_CHANNEL_ID`, and spam only runs in `SPAM_CHANNEL_ID`.
- If a prediction is below threshold, the bot requests a hint instead of forcing a catch.

> **Disclaimer:** Self-bots violate Discord ToS. This is for educational Purposes only and use at your own risk. 
