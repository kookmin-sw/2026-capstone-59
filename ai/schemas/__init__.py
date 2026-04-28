"""ai/schemas — Pydantic 입출력 스키마 (AI Dataset Spec v3 기반)."""

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    GeneratedStep,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RequiredStepStatus,
    RetrievedChunk,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput

__all__ = [
    # common
    "ProjectInfo",
    "StageInfo",
    "StepInfo",
    "DecisionHistoryItem",
    "RequiredStepInfo",
    "RequiredStepStatus",
    "GeneratedStep",
    "RecommendedMethod",
    "CommonMistake",
    "RetrievedChunk",
    # generate
    "GenerateInput",
    "GenerateOutput",
    # accept
    "AcceptInput",
    "AcceptOutput",
    # side_panel
    "SidePanelInput",
    "SidePanelOutput",
]
