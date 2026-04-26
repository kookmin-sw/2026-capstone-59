"""ai/config.py 단위 테스트."""

import os

import pytest

from ai.config import AISettings


class TestAISettings:
    """AISettings 환경 변수 로드 및 기본값 테스트."""

    def test_default_values(self):
        settings = AISettings(_env_file=None)
        assert settings.AWS_REGION == "ap-northeast-2"
        assert settings.MODEL_ID == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert settings.KB_A_ID == ""
        assert settings.KB_B_ID == ""
        assert settings.MAX_TOKENS == 4096
        assert settings.TEMPERATURE == 0.7

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        monkeypatch.setenv("KB_A_ID", "kb-a-123")
        monkeypatch.setenv("KB_B_ID", "kb-b-456")
        monkeypatch.setenv("MAX_TOKENS", "2048")
        monkeypatch.setenv("TEMPERATURE", "0.3")

        settings = AISettings(_env_file=None)
        assert settings.AWS_REGION == "us-east-1"
        assert settings.MODEL_ID == "anthropic.claude-3-haiku-20240307-v1:0"
        assert settings.KB_A_ID == "kb-a-123"
        assert settings.KB_B_ID == "kb-b-456"
        assert settings.MAX_TOKENS == 2048
        assert settings.TEMPERATURE == pytest.approx(0.3)

    def test_partial_env_override(self, monkeypatch):
        monkeypatch.setenv("KB_A_ID", "kb-only-a")
        settings = AISettings(_env_file=None)
        assert settings.KB_A_ID == "kb-only-a"
        assert settings.KB_B_ID == ""  # default preserved
