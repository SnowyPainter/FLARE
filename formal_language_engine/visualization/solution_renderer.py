"""Readable worksheets: one construction step, its diagram and its table per PNG."""
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
import textwrap

from .automata_renderer import graphviz_module, add_automaton, save_png


def _text(value, width=110):
    return '<BR ALIGN="LEFT"/>'.join(escape(line) for paragraph in str(value).splitlines()
                                    for line in (textwrap.wrap(paragraph, width, break_long_words=False) or [""]))


def _table(headers, rows):
    def row(values, header=False):
        color = "#e9eff8" if header else "#ffffff"
        return '<TR>' + ''.join(f'<TD BGCOLOR="{color}" ALIGN="LEFT">{_text(v)}</TD>' for v in values) + '</TR>'
    return '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" COLOR="#cbd5e1">' + row(headers, True) + ''.join(row(r) for r in rows) + '</TABLE>'


def transition_table(snapshot, *, pending=False):
    labels = snapshot.get("state_labels", {})
    alphabet = list(snapshot.get("alphabet", []))
    if any(e["symbol"] == "ε" for e in snapshot["transitions"]):
        alphabet.append("ε")
    transitions = {(e["from"], e["symbol"]): e["to"] for e in snapshot["transitions"]}
    headers = ["State"] + (["NFA subset"] if labels else []) + alphabet + ["Accept"]
    rows = []
    for q in snapshot["states"]:
        row = [("→ " if q == snapshot.get("initial") else "") + q]
        if labels:
            row.append(labels[q])
        for symbol in alphabet:
            targets = transitions.get((q, symbol))
            row.append(("—" if pending else "∅") if targets is None else ", ".join(targets) or "∅")
        row.append("Yes" if q in snapshot["accepting"] else "No")
        rows.append(row)
    return headers, rows


def render_machine_sheet(machine_or_snapshot, path, *, title="Automaton", notes=(), table=True,
                         extra_table=None, pending=False, source=None):
    snapshot = machine_or_snapshot.snapshot() if hasattr(machine_or_snapshot, "snapshot") else machine_or_snapshot
    gv = graphviz_module()
    with TemporaryDirectory(prefix="fle-diagram-") as tmp:
        diagram = gv.Digraph(graph_attr={"rankdir": "LR", "bgcolor": "white", "pad": ".2",
                                         "size": "13,8", "dpi": "100", "nodesep": ".35"},
                             node_attr={"fontname": "DejaVu Sans", "fontsize": "12", "color": "#334155"},
                             edge_attr={"fontname": "DejaVu Sans", "fontsize": "11", "color": "#475569"})
        add_automaton(diagram, snapshot)
        diagram_path = save_png(diagram, Path(tmp) / "diagram.png")
        rows = [f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="21" COLOR="#162d50"><B>{_text(title)}</B></FONT></TD></TR>']
        rows.extend(f'<TR><TD ALIGN="LEFT">{_text(note)}</TD></TR>' for note in notes)
        if source:
            original = gv.Digraph(graph_attr=dict(diagram.graph_attr), node_attr=dict(diagram.node_attr),
                                  edge_attr=dict(diagram.edge_attr))
            add_automaton(original, source)
            original_path = save_png(original, Path(tmp) / "source.png")
            rows.append('<TR><TD ALIGN="LEFT"><B>Input machine</B></TD></TR>')
            rows.append(f'<TR><TD><IMG SRC="{escape(str(original_path))}"/></TD></TR>')
            rows.append('<TR><TD>' + _table(*transition_table(source)) + '</TD></TR>')
            rows.append('<TR><TD ALIGN="LEFT"><B>Construction begins</B></TD></TR>')
        rows.append(f'<TR><TD><IMG SRC="{escape(str(diagram_path))}"/></TD></TR>')
        if table:
            rows.append('<TR><TD>' + _table(*transition_table(snapshot, pending=pending)) + '</TD></TR>')
        if extra_table:
            rows.append('<TR><TD>' + _table(*extra_table) + '</TD></TR>')
        sheet = gv.Digraph(graph_attr={"bgcolor": "white", "pad": ".25", "dpi": "110"},
                           node_attr={"shape": "plain", "fontname": "DejaVu Sans", "fontsize": "11"})
        sheet.node("sheet", '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="10">' + ''.join(rows) + '</TABLE>>')
        return save_png(sheet, path)


def render_solution_trace(trace, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    trace.export_json(directory / "trace.json")
    problem = trace.metadata.get("problem", trace.algorithm)
    paths = []
    if trace.algorithm == "pumping":
        from .proof_renderer import render_proof_tree
        paths.append(render_proof_tree(trace, directory / "answer.png"))
    elif trace.algorithm in ("nfa_to_dfa", "thompson", "gnfa"):
        updates = []
        for step in trace.steps:
            notes, extra, table = [], None, True
            snapshot = step.after
            if trace.algorithm == "nfa_to_dfa":
                if step.operation not in ("initialize_subset", "subset_expanded"):
                    continue
                if step.operation == "initialize_subset":
                    title = "Initial epsilon closure"
                    notes = ["D0 = E({start}); a DFA subset accepts iff it contains an NFA accepting state.",
                             "— means not yet computed. {} is the empty subset (dead state)."]
                else:
                    title = f"Expand {step.details['source']} = {{{', '.join(step.details['subset'])}}}"
                    extra = (["Input", "move(S, input)", "epsilon-closure(move)", "DFA target"], [
                        [r["symbol"], "{" + ", ".join(r["move"]) + "}", "{" + ", ".join(r["closure"]) + "}", r["target"]]
                        for r in step.details["calculations"]])
                    notes = ["δD(S, c) = E(∪ δN(q, c)), q ∈ S. Complete one row of the subset table."]
            elif trace.algorithm == "thompson":
                if not step.operation.startswith("construct_"):
                    continue
                snapshot = step.details["fragment"]
                operation = step.operation.removeprefix("construct_")
                title = f"{operation}: {step.details['expression']}"
                table = False
                rules = {"Symbol": "Create one symbol edge between entry and exit.",
                         "EmptySet": "Create entry and exit with no connecting edge: the empty language.",
                         "Epsilon": "Connect entry to exit with an ε edge.",
                         "Union": "Add a new entry and exit; branch to both children with ε edges.",
                         "Concat": "Connect the left exit to the right entry with ε; no new states.",
                         "Star": "Add entry and exit, an ε bypass, and an ε loop around the child."}
                notes = [rules[operation], f"Entry: {step.details['entry']}; exit: {step.details['exit']}; fragment states: {len(snapshot['states'])}"]
            else:
                if step.operation == "update_label":
                    d = step.details
                    if d["direct"] != d["result"]:
                        updates.append([f"{d['source']} → {d['target']}",
                                        f"{d['direct']} ∪ ({d['incoming']})({d['loop']})*({d['outgoing']})",
                                        d["result"]])
                    continue
                if step.operation not in ("initialize_gnfa", "eliminate_state"):
                    continue
                table = False
                title = "Add fresh start and accept states" if step.operation == "initialize_gnfa" else f"Eliminate state {step.details['state']}"
                notes = ["R'ij = Rij ∪ Rik(Rkk)*Rkj. Omitted edges denote ∅."]
                if updates:
                    extra = (["Updated edge", "Substitution", "Simplified label"], updates)
                if len(snapshot["states"]) == 2:
                    notes.append("Final regular expression: " + snapshot["label_matrix"][snapshot["initial"]][snapshot["accepting"][0]])
            path = directory / f"step_{len(paths):02d}.png"
            paths.append(render_machine_sheet(snapshot, path, title=f"{problem} | {len(paths)}. {title}",
                                              notes=notes, table=table, extra_table=extra,
                                              pending=trace.algorithm == "nfa_to_dfa",
                                              source=step.before if step.operation in ("initialize_subset", "initialize_gnfa") else None))
            updates = []
    else:
        # Non-construction algorithms retain their detailed trace renderer.
        from .trace_renderer import render_trace
        return render_trace(trace, directory, detail="full")
    expected = {p.name for p in paths}
    for old in directory.glob("step_*.png"):
        if old.stem[5:].isdigit() and old.name not in expected:
            old.unlink()
    return paths
