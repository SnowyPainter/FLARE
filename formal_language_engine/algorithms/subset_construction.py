from collections import deque
from ..core.automata import DFA
from ..core.trace import Trace, Result
from .epsilon_closure import epsilon_closure


def convert_nfa_to_dfa(machine):
    trace = Trace("nfa_to_dfa", metadata={"input": machine.snapshot()})
    initial = epsilon_closure(machine, {machine.initial}, trace)
    names = {initial: "D0"}
    pending = deque([initial])
    transitions = {}
    accepting = set()
    if initial & machine.accepting:
        accepting.add("D0")

    def snapshot():
        return {"kind": "automaton", "type": "DFA", "states": list(names.values()),
                "alphabet": sorted(machine.alphabet), "initial": "D0",
                "accepting": sorted(accepting),
                "state_labels": {name: "{" + ", ".join(sorted(states)) + "}"
                                 for states, name in names.items()},
                "transitions": [{"from": q, "symbol": a, "to": [r]}
                                for (q, a), r in sorted(transitions.items())]}

    trace.record("initialize_subset", machine.snapshot(), snapshot(),
                 "The DFA starts in the epsilon closure of the NFA initial state.")
    while pending:
        subset = pending.popleft()
        before_expansion = snapshot()
        rows = []
        for symbol in sorted(machine.alphabet):
            before = snapshot()
            moved = set().union(*(machine.transitions.get((q, symbol), ()) for q in subset))
            target = epsilon_closure(machine, moved, trace)
            new = target not in names
            if new:
                names[target] = f"D{len(names)}"
                pending.append(target)
                if target & machine.accepting:
                    accepting.add(names[target])
            transitions[names[subset], symbol] = names[target]
            rows.append({"symbol": symbol, "move": sorted(moved), "closure": sorted(target),
                         "target": names[target]})
            trace.record("subset_transition", before, snapshot(),
                         "δD(S,a) = epsilon-closure(union of δN(q,a) for q in S).",
                         source=sorted(subset), symbol=symbol, move=sorted(moved),
                         closure=sorted(target), discovered=new)
        trace.record("subset_expanded", before_expansion, snapshot(),
                     "Compute every alphabet column for this subset, then mark its row complete.",
                     source=names[subset], subset=sorted(subset), calculations=rows)
    result = DFA(states=names.values(), alphabet=machine.alphabet, initial="D0",
                 accepting=accepting, transitions=transitions)
    trace.record("complete", snapshot(), result.snapshot(),
                 "All reachable subsets have been expanded, including the empty subset when reachable.")
    result.trace = trace
    return Result(result, trace)
