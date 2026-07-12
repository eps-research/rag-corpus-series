from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    success: bool
    tool: str
    data: Any
    human_text: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, tool: str, data: Any):
        return cls(
            success=True,
            tool=tool,
            data=data,
            human_text=data.get("human_text") if isinstance(data, dict) else None,
            error=None,
        )

    @classmethod
    def fail(cls, tool: str, error: str):
        return cls(
            success=False,
            tool=tool,
            data=None,
            human_text=None,
            error=error,
        )
