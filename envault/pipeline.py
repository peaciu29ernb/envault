"""Pipeline: chain multiple env transformations in sequence."""

from typing import Any, Callable, Dict, List, Optional

EnvDict = Dict[str, str]
Step = Callable[[EnvDict], EnvDict]


class PipelineError(Exception):
    """Raised when a pipeline step fails."""

    def __init__(self, step_name: str, message: str):
        self.step_name = step_name
        self.message = message
        super().__init__(f"[{step_name}] {message}")


class Pipeline:
    """Ordered sequence of transformation steps applied to an env dict."""

    def __init__(self, name: str = "pipeline"):
        self.name = name
        self._steps: List[Dict[str, Any]] = []

    def add_step(self, name: str, fn: Step) -> "Pipeline":
        """Append a named step. Returns self for chaining."""
        if not callable(fn):
            raise TypeError(f"Step '{name}' must be callable")
        self._steps.append({"name": name, "fn": fn})
        return self

    def remove_step(self, name: str) -> bool:
        """Remove a step by name. Returns True if found."""
        before = len(self._steps)
        self._steps = [s for s in self._steps if s["name"] != name]
        return len(self._steps) < before

    def step_names(self) -> List[str]:
        """Return ordered list of step names."""
        return [s["name"] for s in self._steps]

    def run(self, env: EnvDict, stop_on_error: bool = True) -> EnvDict:
        """Execute all steps in order, returning the final env dict."""
        result = dict(env)
        for step in self._steps:
            try:
                result = step["fn"](result)
                if not isinstance(result, dict):
                    raise PipelineError(step["name"], "Step must return a dict")
            except PipelineError:
                raise
            except Exception as exc:
                err = PipelineError(step["name"], str(exc))
                if stop_on_error:
                    raise err from exc
        return result

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        return f"Pipeline(name={self.name!r}, steps={self.step_names()})"


def build_pipeline(name: str, steps: Optional[List[Dict[str, Any]]] = None) -> Pipeline:
    """Convenience factory to build a Pipeline from a list of step dicts.

    Each dict must have 'name' (str) and 'fn' (callable).
    """
    p = Pipeline(name=name)
    for s in (steps or []):
        p.add_step(s["name"], s["fn"])
    return p
