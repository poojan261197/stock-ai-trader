from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _read_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppSettings:
    base_dir: Path
    model_path: Path
    data_path: Path
    host: str
    port: int
    debug: bool
    log_level: str

    @classmethod
    def from_env(cls, base_dir: Path | None = None) -> "AppSettings":
        resolved_base_dir = (base_dir or Path(__file__).resolve().parent).resolve()
        model_path = Path(os.getenv("REALTIME_AGENT_MODEL_PATH", resolved_base_dir / "model.pkl")).resolve()
        data_path = Path(os.getenv("REALTIME_AGENT_DATA_PATH", resolved_base_dir / "TWTR.csv")).resolve()
        return cls(
            base_dir=resolved_base_dir,
            model_path=model_path,
            data_path=data_path,
            host=os.getenv("REALTIME_AGENT_HOST", "0.0.0.0"),
            port=int(os.getenv("REALTIME_AGENT_PORT", "8005")),
            debug=_read_bool("REALTIME_AGENT_DEBUG"),
            log_level=os.getenv("REALTIME_AGENT_LOG_LEVEL", "INFO").upper(),
        )
