"""Serializable, independent snapshots shared by every algorithm."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class Step:
    index: int
    operation: str
    before: dict
    after: dict
    reason: str
    details: dict = field(default_factory=dict)


@dataclass
class Trace:
    algorithm: str
    steps: list[Step] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def record(self, operation, before, after, reason, **details):
        self.steps.append(Step(len(self.steps), operation, deepcopy(before),
                               deepcopy(after), reason, deepcopy(details)))

    def to_dict(self):
        from dataclasses import asdict
        return {"schema_version": 1, "algorithm": self.algorithm,
                "metadata": deepcopy(self.metadata),
                "steps": [asdict(step) for step in self.steps]}

    def export_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def export_png(self, directory, *, detail="steps"):
        from ..visualization.trace_renderer import render_trace
        return render_trace(self, directory, detail=detail)


@dataclass
class Result:
    value: Any
    trace: Trace

    @property
    def machine(self):
        return self.value

    @property
    def regex(self):
        return self.value

    def export_png(self, directory, *, detail="steps"):
        paths = self.trace.export_png(directory, detail=detail)
        if self.trace.algorithm == "gnfa":
            Path(directory, "final_regex.txt").write_text(str(self.value) + "\n", encoding="utf-8")
        return paths


def finish(result, trace=False, output_dir=None):
    """Convenience methods return values; functional API always returns Result."""
    if hasattr(result.value, "trace"):
        result.value.trace = result.trace
    if trace or output_dir is not None:
        result.export_png(output_dir or Path("outputs") / result.trace.algorithm)
    return result.value
