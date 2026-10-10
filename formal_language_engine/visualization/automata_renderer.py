from pathlib import Path


def graphviz_module():
    try:
        import graphviz
    except ImportError as error:
        raise RuntimeError("Install the Python renderer with: pip install -e .") from error
    return graphviz


def add_automaton(graph, snapshot, prefix="q"):
    gv = graphviz_module()
    ids = {q: f"{prefix}_{i}" for i, q in enumerate(snapshot["states"])}
    active = set(snapshot.get("active", []))
    labels = snapshot.get("state_labels", {})
    for q, identifier in ids.items():
        options = {"shape": "doublecircle" if q in snapshot["accepting"] else "circle"}
        if q in active:
            options.update(style="filled", fillcolor="lightblue")
        graph.node(identifier, label=gv.escape(labels.get(q, q)), **options)
    initial = snapshot.get("initial")
    if initial in ids:
        graph.node(f"{prefix}_entry", label="", shape="point")
        graph.edge(f"{prefix}_entry", ids[initial])
    edges = {}
    for edge in snapshot["transitions"]:
        for target in edge["to"]:
            edges.setdefault((edge["from"], target), []).append(edge["symbol"])
    for (source, target), symbols in edges.items():
        graph.edge(ids[source], ids[target], label=gv.escape(", ".join(symbols)))


def save_png(graph, path):
    gv = graphviz_module()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        png = graph.pipe(format="png")
    except gv.backend.ExecutableNotFound as error:
        raise RuntimeError("Graphviz 'dot' is required. Install Graphviz using your OS package manager.") from error
    path.write_bytes(png)
    return path


def render_automaton(snapshot, path):
    gv = graphviz_module()
    graph = gv.Digraph(graph_attr={"rankdir": "LR", "bgcolor": "white"})
    add_automaton(graph, snapshot)
    return save_png(graph, path)
