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

> **Requires Python 3.12.** Download from [python.org](https://www.python.org/downloads/) if not already installed.

### 1. Clone the repo
```bash
git clone -b beta-with-ai https://github.com/amansingh903/Poketwo-Autocatcher.git
cd Poketwo-Autocatcher
```


### 2. Configure environment variables

Update the .env file in the bot folder.

#### Required
| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Your user token |
| `GUILD_ID` | Guild/server where the bot should operate |

#### Optional
| Variable | Default | Description |
|---|---|---|
| `OWNER_ID` | — | Discord user ID allowed to run owner commands |
| `CATCH_CHANNEL_ID` | — | Channel ID used by hint solver fallback |
| `SPAM_CHANNEL_ID` | — | Channel used by spam loop |
| `CATCH_ENABLED` | `true` | Enable/disable catch flow |
| `SPAM_ENABLED` | `true` | Enable/disable spam loop |
| `START_SLEEPING` | `false` | Start in paused/sleeping mode |
| `AI_CONFIDENCE_THRESHOLD` | `0.72` | Confidence threshold `(0, 1]` |
| `CATCH_COOLDOWN_SECONDS` | `1.2` | Must be `> 0` |
| `HINT_COOLDOWN_SECONDS` | `1.0` | Must be `> 0` |
| `STATE_FILE_PATH` | `bot/runtime_state.json` | Path for persisted runtime state |

### 3. Run the setup script for your platform

The scripts auto-detect your Python 3.12 interpreter, create a virtual environment, and install all dependencies.

| Platform | Command |
|---|---|
| **Linux / macOS** | `bash setup.sh` |
| **Windows — PowerShell** | `powershell -ExecutionPolicy Bypass -File setup.ps1` |
| **Windows — Command Prompt** | `setup.bat` |

<details>
<summary>Manual setup (any platform)</summary>

```bash
# Linux / macOS
python3.12 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate.bat       # Windows CMD
# .venv\Scripts\Activate.ps1       # Windows PowerShell
python -m pip install --upgrade pip
pip install -r bot/main/requirements.txt
```
</details>


### 4. Activate the environment and launch

```bash
# Linux / macOS
source .venv/bin/activate
python bot/main/main.py

# Windows CMD
.venv\Scripts\activate.bat
python bot/main/main.py

# Windows PowerShell
.venv\Scripts\Activate.ps1
python bot/main/main.py
```

## Commands
| Command | Description |
|---|---|
| `!say <text>` | Send a message from your account |
| `!react <message_id> <emoji>` | React to a message in the current channel |
| `!solved` | Resume spam mode after captcha resolution |
| `!togglecatch` | Toggle catch flow on/off |
| `!togglespam` | Toggle spam flow on/off |

## Notes
- The bot validates startup config and model/class compatibility.
- Runtime state (sleeping flag, last captcha time, last caught name) is saved to `STATE_FILE_PATH`.
- Catching only runs in `CATCH_CHANNEL_ID`, and spam only runs in `SPAM_CHANNEL_ID`.
- If a prediction is below threshold, the bot requests a hint instead of forcing a catch.

> **Disclaimer:** Self-bots violate Discord ToS. This is for educational purposes only. Use at your own risk.
