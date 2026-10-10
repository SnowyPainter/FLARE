from ..core.regex_ast import Regex, EmptySet, Epsilon, Symbol, Union, Concat, Star
from ..core.parser import parse_regex
from ..core.automata import NFA
from ..core.trace import Trace, Result


def regex_to_nfa(expression):
    if isinstance(expression, str):
        expression = parse_regex(expression, simplify=False)
    if not isinstance(expression, Regex):
        raise TypeError("Expected a regex string or AST")
    trace = Trace("thompson", metadata={"expression": str(expression)})
    states, alphabet, transitions = set(), set(), {}

    def fresh():
        q = f"q{len(states)}"
        states.add(q)
        return q

    def edge(q, symbol, r):
        transitions.setdefault((q, symbol), set()).add(r)

    def snapshot(initial=None, accepting=()):
        return {"kind": "automaton", "type": "ε-NFA", "states": sorted(states),
                "alphabet": sorted(alphabet), "initial": initial, "accepting": list(accepting),
                "transitions": [{"from": q, "symbol": a, "to": sorted(rs)}
                                for (q, a), rs in sorted(transitions.items())]}

    def build(r):
        # Child fragments are recorded before the parent connection is added.
        children = []
        if isinstance(r, (Union, Concat)):
            children = [build(r.left), build(r.right)]
        elif isinstance(r, Star):
            children = [build(r.child)]
        before = snapshot()
        if isinstance(r, Concat):
            # Concatenation connects existing exits/entries; it adds no states.
            (start, left_end), (right_start, end) = children
            edge(left_end, "ε", right_start)
        else:
            start, end = fresh(), fresh()
        if isinstance(r, Symbol):
            alphabet.add(r.value)
            edge(start, r.value, end)
        elif isinstance(r, Epsilon):
            edge(start, "ε", end)
        elif isinstance(r, EmptySet):
            pass
        elif isinstance(r, Union):
            for a, b in children:
                edge(start, "ε", a)
                edge(b, "ε", end)
        elif isinstance(r, Concat):
            pass
        elif isinstance(r, Star):
            a, b = children[0]
            edge(start, "ε", end)
            edge(start, "ε", a)
            edge(b, "ε", a)
            edge(b, "ε", end)
        else:
            raise TypeError(f"Unsupported regex node: {type(r)}")
        after = snapshot(start, [end])
        # Store the current subexpression on its own, excluding unrelated fragments.
        fragment_states = {start}
        pending = [start]
        while pending:
            q = pending.pop()
            for (source, _), targets in transitions.items():
                if source == q:
                    for target in targets - fragment_states:
                        fragment_states.add(target)
                        pending.append(target)
        fragment_states.add(end)  # ∅ has an intentionally unreachable exit.
        # ∅* also contains unreachable child states; preserve its construction.
        fragment_states.update(set(after["states"]) - set(before["states"]))
        for child_start, child_end in children:
            fragment_states.update(fragments[child_start])
        fragments[start] = fragment_states
        fragment = {**after, "states": sorted(fragment_states),
                    "transitions": [e for e in after["transitions"] if e["from"] in fragment_states]}
        trace.record("construct_" + type(r).__name__, before, after,
                     "Thompson fragments have one entry and one exit and recognize their subexpression.",
                     expression=str(r), entry=start, exit=end, children=children, fragment=fragment)
        return start, end

    fragments = {}
    start, end = build(expression)
    machine = NFA(states=states, alphabet=alphabet, initial=start, accepting={end}, transitions=transitions)
    machine.trace = trace
    return Result(machine, trace)
