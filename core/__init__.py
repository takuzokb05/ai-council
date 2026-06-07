"""AI COUNCIL — core パッケージ。

UI 非依存の討論オーケストレーション・エンジン。
詳細な設計判断はトップ README の「3 大バグを構造で根治」節を参照。
"""

from .personas import (
    Persona,
    persona_from_dict,
    load_personas,
    load_personas_with_paths,
)
from .llm_client import (
    LLMClient,
    AnthropicClient,
    OpenAIClient,
    GeminiClient,
    MockLLMClient,
    DEFAULT_MODEL,
)
from .context import build_context
from .orchestrator import Council, Turn, RoundRobinScheduler

__all__ = [
    "Persona",
    "persona_from_dict",
    "load_personas",
    "load_personas_with_paths",
    "LLMClient",
    "AnthropicClient",
    "OpenAIClient",
    "GeminiClient",
    "MockLLMClient",
    "DEFAULT_MODEL",
    "build_context",
    "Council",
    "Turn",
    "RoundRobinScheduler",
]
