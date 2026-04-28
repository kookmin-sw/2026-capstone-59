"""ai/config.py 단위 테스트."""

import pytest

from ai.config import AISettings


class TestAISettings:
    """AISettings 환경 변수 로드 및 기본값 테스트."""

    def test_default_values(self):
        settings = AISettings(_env_file=None)
        assert settings.AWS_REGION == "us-east-1"
        assert settings.MODEL_ID == "us.anthropic.claude-sonnet-4-20250514-v1:0"
        assert settings.KB_ID == ""
        assert settings.MAX_TOKENS == 4096
        assert settings.TEMPERATURE == 0.7

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("AWS_REGION", "us-west-2")
        monkeypatch.setenv("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
        monkeypatch.setenv("KB_ID", "kb-test-123")
        monkeypatch.setenv("MAX_TOKENS", "2048")
        monkeypatch.setenv("TEMPERATURE", "0.3")

        settings = AISettings(_env_file=None)
        assert settings.AWS_REGION == "us-west-2"
        assert settings.MODEL_ID == "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        assert settings.KB_ID == "kb-test-123"
        assert settings.MAX_TOKENS == 2048
        assert settings.TEMPERATURE == pytest.approx(0.3)

    def test_partial_env_override(self, monkeypatch):
        monkeypatch.setenv("KB_ID", "kb-override")
        settings = AISettings(_env_file=None)
        assert settings.KB_ID == "kb-override"
        assert settings.AWS_REGION == "us-east-1"  # default preserved
