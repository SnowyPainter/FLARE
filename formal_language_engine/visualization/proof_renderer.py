"""Proof deductions and bounded-search branches as Graphviz diagrams."""
from .automata_renderer import graphviz_module, save_png
from .trace_renderer import text_label


def render_proof_tree(trace, path):
    gv = graphviz_module()
    graph = gv.Digraph(graph_attr={"rankdir": "TB", "bgcolor": "white"})
    graph.node("root", text_label(trace.metadata["language"]), shape="box")
    previous = "root"
    candidates, splits = {}, {}
    for step in trace.steps:
        identifier = f"step_{step.index}"
        if step.operation == "symbolic_deduction":
            graph.node(identifier, text_label(step.reason), shape="box")
            graph.edge(previous, identifier)
            previous = identifier
        elif step.operation == "candidate":
            key = (step.before["p"], step.after["word"])
            candidates[key] = identifier
            graph.node(identifier, text_label({"p": key[0], **step.after}), shape="box")
            graph.edge("root", identifier)
        elif step.operation == "pump_trial":
            data = step.before
            key = (data["p"], data["word"], data["x"], data["y"], data["z"])
            if key not in splits:
                split = f"split_{step.index}"
                splits[key] = split
                graph.node(split, text_label({k: data[k] for k in ("x", "y", "z")}), shape="box")
                graph.edge(candidates[key[:2]], split, label="valid split")
            graph.node(identifier, text_label(step.after), shape="box", style="filled",
                       fillcolor="mistyrose" if step.after["member"] else "honeydew")
            graph.edge(splits[key], identifier)
        elif step.operation == "conclusion":
            graph.node(identifier, text_label(step.after), shape="box", style="filled", fillcolor="lightyellow")
            graph.edge(previous, identifier)
    certificate = trace.metadata.get("certificate")
    if certificate:
        with graph.subgraph(name="cluster_decomposition") as panel:
            panel.attr(label="Every valid decomposition: p >= 1, s >= 0, t >= 1, s+t <= p", rank="same")
            a, b = certificate["a"], certificate["b"]
            panel.node("x", gv.escape(f"x = {a}^s"), shape="box")
            panel.node("y", gv.escape(f"y = {a}^t"), shape="box", style="filled", fillcolor="lightblue")
            z = f"{a}^(p-s-t){b}^p" if certificate["scheme"] == "equal_blocks" else f"{a}^(p-s-t){b}({a}^p{b})^{certificate['copies'] - 1}"
            panel.node("z", gv.escape("z = " + z), shape="box")
            panel.edge("x", "y", label="concatenate")
            panel.edge("y", "z", label="concatenate")
        graph.edge("root", "x", label=f"W = xyz; pump y with i = {certificate['pumping_exponent']}")
    return save_png(graph, path)


def render_proof(proof_result, directory):
    from .trace_renderer import render_trace
    return render_trace(proof_result.trace, directory)
