import os
from pathlib import Path


def _load_dotenv() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    candidate_paths = [
        repo_root / ".env",
        repo_root / "bot" / ".env",
        Path(__file__).resolve().parent / ".env",
    ]

    for env_path in candidate_paths:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


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
OwnerId = _optional_int("OWNER_ID")
GuildId = _required_int("GUILD_ID")
SpamId = _optional_int("SPAM_CHANNEL_ID")
CatchId = _optional_int("CATCH_CHANNEL_ID")
sleep = _optional_bool("START_SLEEPING", default=False)
CatchEnabled = _optional_bool("CATCH_ENABLED", default=True)
SpamEnabled = _optional_bool("SPAM_ENABLED", default=True)
AiConfidenceThreshold = _optional_float("AI_CONFIDENCE_THRESHOLD", default=0.72)
CatchCooldownSeconds = _optional_positive_float("CATCH_COOLDOWN_SECONDS", default=1.2)
HintCooldownSeconds = _optional_positive_float("HINT_COOLDOWN_SECONDS", default=1.0)
StateFilePath = os.getenv("STATE_FILE_PATH", "bot/runtime_state.json").strip() or "bot/runtime_state.json"
