import os


def _required_str(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _required_int(name: str) -> int:
    value = _required_str(name)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


def _optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


def _optional_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on"}


def _optional_float(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float.") from exc


def _optional_positive_float(name: str, default: float) -> float:
    value = _optional_float(name, default)
    if value <= 0:
        raise ValueError(f"Environment variable {name} must be greater than 0.")
    return value


token = _required_str("DISCORD_TOKEN")
OwnerId = _required_int("OWNER_ID")
GuildId = _required_int("GUILD_ID")
SpamId = _optional_int("SPAM_CHANNEL_ID")
CatchId = _required_int("CATCH_CHANNEL_ID")
sleep = _optional_bool("START_SLEEPING", default=False)
AiConfidenceThreshold = _optional_float("AI_CONFIDENCE_THRESHOLD", default=0.72)
CatchCooldownSeconds = _optional_positive_float("CATCH_COOLDOWN_SECONDS", default=1.2)
HintCooldownSeconds = _optional_positive_float("HINT_COOLDOWN_SECONDS", default=1.0)
StateFilePath = os.getenv("STATE_FILE_PATH", "bot/runtime_state.json").strip() or "bot/runtime_state.json"
