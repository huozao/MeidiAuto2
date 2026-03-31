from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineStep:
    """A script step executed by the orchestrator."""

    filename: str
    required: bool = True

