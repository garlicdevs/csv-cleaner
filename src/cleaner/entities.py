from dataclasses import dataclass, field
from typing import Optional, List
from pandas.api.types import infer_dtype


@dataclass
class ColumnInference:
    name: str
    pandas_type: str
    friendly_name: str


@dataclass
class InferenceResult:
    columns: List[ColumnInference] = field(default_factory=list)
