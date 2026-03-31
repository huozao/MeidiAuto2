from __future__ import annotations

import glob
import os
from pathlib import Path


def resolve_data_dir(argv_value: str | None, default_dir: str = "data") -> Path:
    if argv_value:
        return Path(argv_value).resolve()
    return Path(os.getcwd(), default_dir).resolve()


def find_first_excel(data_dir: Path, pattern: str) -> str | None:
    files = glob.glob(str(data_dir / pattern))
    return files[0] if files else None


def find_latest_excel(data_dir: Path, pattern: str) -> str | None:
    files = glob.glob(str(data_dir / pattern))
    return max(files, key=os.path.getmtime) if files else None

