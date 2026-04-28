"""프롬프트 템플릿 로드 및 변수 치환 모듈.

ai/prompts/ 디렉토리의 .txt 파일을 로드하고,
{variable_name} 플레이스홀더를 치환하여 최종 프롬프트를 생성한다.
"""

import re
from pathlib import Path

from ai.exceptions import PromptTemplateNotFoundError

_PROMPTS_DIR = Path(__file__).parent


class PromptTemplate:
    """프롬프트 템플릿 로더 및 렌더러."""

    @staticmethod
    def load(scenario: str) -> str:
        """시나리오 이름으로 프롬프트 템플릿 파일을 로드한다.

        Args:
            scenario: 시나리오 이름 (예: "generate", "accept", "side_panel")

        Returns:
            템플릿 파일 내용 (str)

        Raises:
            PromptTemplateNotFoundError: 파일이 존재하지 않을 때
        """
        path = _PROMPTS_DIR / f"{scenario}.txt"
        if not path.exists():
            raise PromptTemplateNotFoundError(
                message=f"프롬프트 템플릿 '{scenario}.txt'를 찾을 수 없습니다.",
                details={"scenario": scenario, "path": str(path)},
            )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def render(template: str, **variables: str) -> str:
        """템플릿의 {variable_name} 플레이스홀더를 치환한다.

        Python str.format_map 호환. 제공되지 않은 변수는 그대로 유지.

        Args:
            template: 플레이스홀더가 포함된 템플릿 문자열
            **variables: 치환할 변수 맵

        Returns:
            치환된 최종 프롬프트 문자열
        """

        class _SafeDict(dict):
            """누락된 키를 원본 플레이스홀더로 유지."""

            def __missing__(self, key: str) -> str:
                return "{" + key + "}"

        return template.format_map(_SafeDict(variables))

    @classmethod
    def load_and_render(cls, scenario: str, **variables: str) -> str:
        """로드 + 렌더를 한 번에 수행하는 편의 메서드.

        Args:
            scenario: 시나리오 이름
            **variables: 치환할 변수 맵

        Returns:
            치환된 최종 프롬프트 문자열
        """
        template = cls.load(scenario)
        return cls.render(template, **variables)
