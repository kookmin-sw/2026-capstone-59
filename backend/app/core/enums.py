from enum import StrEnum


class StepStatus(StrEnum):
    READY = "READY"
    ACCEPTED = "ACCEPTED"
    CANCELED = "CANCELED"


class OAuthProvider(StrEnum):
    GOOGLE = "google"
    NAVER = "naver"
    KAKAO = "kakao"
