"""ai/schemas — Pydantic 입출력 스키마 (AI Dataset Spec v3 기반)."""

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RequiredStepStatus,
    RetrievedChunk,
    StageInfo,
    StepInfo,
)
from ai.schemas.design_export import (
    AcceptedStepData,
    DesignExportInput,
    DesignExportOutput,
    ProjectStateForExport,
    RequiredStepExportData,
    SidePanelMentoring,
    StageExportData,
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
    "MentoringContent",
    "DictionaryItem",
    # generate
    "GenerateInput",
    "GenerateOutput",
    # accept
    "AcceptInput",
    "AcceptOutput",
    # side_panel
    "SidePanelInput",
    "SidePanelOutput",
    # design_export
    "AcceptedStepData",
    "RequiredStepExportData",
    "StageExportData",
    "ProjectStateForExport",
    "DesignExportInput",
    "DesignExportOutput",
    "SidePanelMentoring",
]
