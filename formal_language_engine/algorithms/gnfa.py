from ..core.regex_ast import EMPTY, EPSILON, Symbol, union, concat, star, EmptySet
from ..core.trace import Trace, Result


def automaton_to_regex(machine, *, elimination_order=None):
    remaining = sorted(machine.states)
    if elimination_order is not None:
        elimination_order = list(elimination_order)
        if len(elimination_order) != len(remaining) or set(elimination_order) != set(remaining):
            raise ValueError("elimination_order must contain every original state exactly once")
    used = set(remaining)
    def fresh(base):
        while base in used:
            base += "_"
        used.add(base)
        return base
    start, end = fresh("__start"), fresh("__accept")
    states = [start, *remaining, end]
    labels = {(i, j): EMPTY for i in states for j in states}
    labels[start, machine.initial] = EPSILON
    for q in machine.accepting:
        labels[q, end] = EPSILON
    for (q, a), targets in machine.transitions.items():
        for r in targets:
            labels[q, r] = union(labels[q, r], EPSILON if a == "ε" else Symbol(a))
    trace = Trace("gnfa", metadata={"input": machine.snapshot(), "elimination_order": []})

    def snapshot():
        return {"kind": "automaton", "type": "GNFA", "states": list(states), "initial": start,
                "accepting": [end], "transitions": [
                    {"from": i, "symbol": str(labels[i, j]), "to": [j]}
                    for i in states for j in states if not isinstance(labels[i, j], EmptySet)],
                "label_matrix": {i: {j: str(labels[i, j]) for j in states} for i in states}}

    trace.record("initialize_gnfa", machine.snapshot(), snapshot(),
                 "Add a fresh start and accept state; missing edges carry ∅ and parallel edges use union.")
    while remaining:
        if elimination_order is not None:
            k = elimination_order[len(trace.metadata["elimination_order"])]
        else:
            def cost(q):
                incoming = sum(not isinstance(labels[i, q], EmptySet) for i in states if i != q)
                outgoing = sum(not isinstance(labels[q, j], EmptySet) for j in states if j != q)
                return incoming * outgoing, len(str(labels[q, q])), q
            k = min(remaining, key=cost)
        trace.metadata["elimination_order"].append(k)
        survivors = [q for q in states if q != k]
        # Copy the previous matrix: every formula uses the same pre-elimination labels.
        old = dict(labels)
        for i in survivors:
            for j in survivors:
                before = snapshot()
                via = concat(old[i, k], star(old[k, k]), old[k, j])
                labels[i, j] = union(old[i, j], via)
                trace.record("update_label", before, snapshot(),
                             "R'ij = Rij ∪ Rik(Rkk)*Rkj; paths either avoid k or pass through k.",
                             eliminated=k, source=i, target=j, direct=str(old[i, j]),
                             incoming=str(old[i, k]), loop=str(old[k, k]), outgoing=str(old[k, j]),
                             via=str(via), result=str(labels[i, j]))
        before = snapshot()
        states.remove(k)
        remaining.remove(k)
        trace.record("eliminate_state", before, snapshot(),
                     "All paths through this state have been absorbed into the surviving labels.", state=k)
    value = labels[start, end]
    trace.record("complete", snapshot(), {**snapshot(), "regex": str(value)},
                 "The sole start-to-accept label denotes the original language.")
    return Result(value, trace)
