from __future__ import annotations

from .models import PipelineStep

PRODUCTION_STEPS: tuple[PipelineStep, ...] = (
    PipelineStep("020 Email download.py"),
    PipelineStep("021 Merge excel.py"),
    PipelineStep("030 Warehousing at home.py"),
    PipelineStep("032 Warehousing at out.py"),
    PipelineStep("033 list insertion.py"),
    PipelineStep("041 operation.py"),
    PipelineStep("042 Color display.py"),
    PipelineStep("050 mailtxt.py"),
    PipelineStep("051 Send an email.py"),
)

CLEANUP_STEP = PipelineStep("010 clean.py", required=False)

