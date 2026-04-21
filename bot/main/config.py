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


token = _required_str("DISCORD_TOKEN")
OwnerId = _required_int("OWNER_ID")
GuildId = _required_int("GUILD_ID")
SpamId = _optional_int("SPAM_CHANNEL_ID")
CatchId = _required_int("CATCH_CHANNEL_ID")
sleep = _optional_bool("START_SLEEPING", default=False)
