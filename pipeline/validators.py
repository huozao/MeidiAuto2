from __future__ import annotations

import glob
from pathlib import Path
from typing import Iterable

from .models import PipelineStep


def missing_step_files(script_dir: Path, steps: Iterable[PipelineStep]) -> list[str]:
    missing: list[str] = []
    for step in steps:
        if step.required and not (script_dir / step.filename).exists():
            missing.append(step.filename)
    return missing


def validate_step_output(step: PipelineStep, data_dir: Path) -> tuple[bool, str]:
    """关键步骤产物校验，防止子脚本误返回 0 导致级联失败。"""
    if step.filename == "020 Email download.py":
        meta_path = data_dir / "mail_meta.json"
        stock_files = glob.glob(str(data_dir / "存量查询*.xlsx"))
        if not meta_path.exists():
            return False, "缺少 mail_meta.json（邮件元数据未生成）"
        if not stock_files:
            return False, "缺少 存量查询*.xlsx（邮件表格未导出）"
    if step.filename == "021 Merge excel.py":
        merged_files = glob.glob(str(data_dir / "总库存*.xlsx"))
        if not merged_files:
            return False, "缺少 总库存*.xlsx（合并文件未生成）"
    return True, ""

