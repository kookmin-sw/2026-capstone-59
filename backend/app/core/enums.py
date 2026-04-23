from enum import StrEnum


class ProjectStageStatus(StrEnum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    COMPLETED = "COMPLETED"


class StepStatus(StrEnum):
    READY = "READY"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
