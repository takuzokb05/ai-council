"""AI COUNCIL — HTTP API（FastAPI + SSE）。

core エンジンは UI 非依存なので、`council.run()` の yield を Server-Sent Events で
そのまま流すだけで「途中経過が見える」ストリーミング討論になる（"完了するまで何も見えない" を構造的に解消）。
"""
