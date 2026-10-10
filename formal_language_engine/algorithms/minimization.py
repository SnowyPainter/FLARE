from collections import deque
from ..core.automata import DFA
from ..core.trace import Trace, Result


def minimize_dfa(machine):
    if not isinstance(machine, DFA):
        raise TypeError("DFA minimization requires a DFA; first call to_dfa()")
    trace = Trace("minimization", metadata={"input": machine.snapshot()})
    alphabet = sorted(machine.alphabet)
    states = set(machine.states)
    delta = {key: next(iter(targets)) for key, targets in machine.transitions.items()}
    sink = "__sink"
    while sink in states:
        sink += "_"
    missing = [(q, a) for q in sorted(states) for a in alphabet if (q, a) not in delta]
    if missing:
        states.add(sink)
        for q, a in missing + [(sink, a) for a in alphabet]:
            delta[q, a] = sink
    completed = DFA(states=states, alphabet=alphabet, initial=machine.initial,
                    accepting=machine.accepting, transitions=delta)
    trace.record("complete_transition_table", machine.snapshot(), completed.snapshot(),
                 "Missing DFA transitions enter a rejecting sink.", added_sink=sink if missing else None)
    reached = {machine.initial}
    queue = deque([machine.initial])
    while queue:
        q = queue.popleft()
        for a in alphabet:
            before = {"reachable": sorted(reached)}
            target = delta[q, a]
            if target not in reached:
                reached.add(target)
                queue.append(target)
            trace.record("reachability_transition", before, {"reachable": sorted(reached)},
                         "Only reachable states affect the recognized language.", source=q, symbol=a, target=target)
    parts = [s for s in (reached & machine.accepting, reached - machine.accepting) if s]

    def snapshot():
        return {"partitions": [sorted(p) for p in parts], "reachable": sorted(reached)}

    trace.record("initial_partition", completed.snapshot(), snapshot(),
                 "The empty suffix distinguishes accepting and rejecting states.", removed=sorted(states - reached))
    while True:
        block = {q: i for i, group in enumerate(parts) for q in group}
        refined = []
        before = snapshot()
        signatures = {}
        for group in parts:
            buckets = {}
            for q in sorted(group):
                signature = tuple(block[delta[q, a]] for a in alphabet)
                signatures[q] = list(signature)
                buckets.setdefault(signature, set()).add(q)
            refined.extend(buckets.values())
        changed = len(refined) != len(parts)
        parts = refined
        trace.record("refine_partition", before, snapshot(),
                     "States stay together iff their transitions lead to the same blocks for every symbol.",
                     alphabet=alphabet, signatures=signatures, changed=changed)
        if not changed:
            break
    names = {q: f"M{i}" for i, group in enumerate(parts) for q in group}
    transitions = {(f"M{i}", a): names[delta[min(group), a]]
                   for i, group in enumerate(parts) for a in alphabet}
    result = DFA(states=set(names.values()), alphabet=alphabet, initial=names[machine.initial],
                 accepting={names[q] for q in machine.accepting & reached}, transitions=transitions)
    trace.record("quotient", snapshot(), result.snapshot(),
                 "The stable reachable partition defines the minimal complete DFA.", state_mapping=names)
    result.trace = trace
    return Result(result, trace)
