import json
import textwrap
from pathlib import Path
from .automata_renderer import graphviz_module, add_automaton, save_png, render_automaton


def text_label(value):
    gv = graphviz_module()
    raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return "\n".join(gv.escape(line) for paragraph in raw.splitlines()
                     for line in (textwrap.wrap(paragraph, width=100, replace_whitespace=False) or [""]))


def render_step(step, path):
    gv = graphviz_module()
    graph = gv.Digraph(graph_attr={"rankdir": "TB", "bgcolor": "white", "pad": "0.3"})
    graph.node("operation", label=text_label(f"Step {step.index:03d}: {step.operation}\n{step.reason}"),
               shape="box", style="filled", fillcolor="lightyellow")
    for label, data in (("before", step.before), ("after", step.after)):
        with graph.subgraph(name=f"cluster_{label}") as panel:
            panel.attr(label=label)
            if data.get("kind") == "automaton":
                add_automaton(panel, data, prefix=label)
                extra = {k: v for k, v in data.items() if k not in {
                    "kind", "type", "states", "alphabet", "initial", "accepting", "transitions", "state_labels", "label_matrix"}}
                panel.node(label + "_info", text_label(extra or data.get("type", "")), shape="plaintext")
            else:
                panel.node(label + "_info", text_label(data), shape="box")
        graph.edge("operation" if label == "before" else "before_info", label + "_info")
    if step.details:
        graph.node("details", text_label(step.details), shape="note")
        graph.edge("after_info", "details")
    return save_png(graph, path)


def render_trace(trace, directory, *, detail="steps"):
    if detail not in ("steps", "full"):
        raise ValueError("detail must be 'steps' or 'full'")
    if detail == "steps":
        from .solution_renderer import render_solution_trace
        return render_solution_trace(trace, directory)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # Write machine-readable evidence first, even when the external renderer is unavailable.
    trace.export_json(directory / "trace.json")
    paths = []
    original = trace.metadata.get("input")
    if isinstance(original, dict) and original.get("kind") == "automaton":
        paths.append(render_automaton(original, directory / "original.png"))
    for step in trace.steps:
        paths.append(render_step(step, directory / f"step_{step.index:03d}.png"))
    if trace.algorithm == "pumping":
        from .proof_renderer import render_proof_tree
        paths.append(render_proof_tree(trace, directory / "proof_tree.png"))
    # A shorter rerun must not leave steps from the previous execution behind.
    expected = {f"step_{step.index:03d}.png" for step in trace.steps}
    for old in directory.glob("step_*.png"):
        if old.stem[5:].isdigit() and old.name not in expected:
            old.unlink()
    return paths
