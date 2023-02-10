from typing import Any, Literal
from dataclasses import dataclass

@dataclass
class QueryRule:
    column: str
    operator: Literal["eq", "in", "between"]
    value: Any