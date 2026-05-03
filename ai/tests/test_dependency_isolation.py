"""Property 9: AI 모듈 의존성 격리.

ai/ 내 모든 Python 모듈이 백엔드 전용 패키지를 import하지 않는지 정적 분석.
"""

import ast
from pathlib import Path

import pytest

_AI_ROOT = Path(__file__).parent.parent
_BANNED = {"fastapi", "sqlalchemy", "uvicorn", "alembic", "starlette", "mangum"}


def _collect_modules() -> list[Path]:
    return [
        p
        for p in _AI_ROOT.rglob("*.py")
        if "tests" not in p.relative_to(_AI_ROOT).parts
    ]


def _imported_top_level_packages(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    packages: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                packages.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                packages.add(node.module.split(".")[0])
    return packages


@pytest.mark.parametrize("module_path", _collect_modules())
def test_no_backend_imports(module_path: Path):
    imported = _imported_top_level_packages(module_path)
    violations = imported & _BANNED
    assert not violations, (
        f"{module_path.relative_to(_AI_ROOT)} 에서 금지된 패키지 import 발견: {violations}"
    )
