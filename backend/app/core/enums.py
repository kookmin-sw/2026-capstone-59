from enum import StrEnum


class StepStatus(StrEnum):
    READY = "READY"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"
