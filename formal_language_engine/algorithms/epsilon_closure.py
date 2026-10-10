from ..core.trace import Trace, Result


def epsilon_closure(machine, states, trace=None):
    seen = set(states)
    if not seen <= machine.states:
        raise ValueError("Closure seeds must be machine states")
    pending = sorted(seen, reverse=True)
    if trace is not None:
        trace.record("closure_start", {}, {"states": sorted(seen)},
                     "Every seed is reachable by zero epsilon transitions.")
    while pending:
        q = pending.pop()
        before = {"states": sorted(seen), "pending": list(pending)}
        targets = machine.transitions.get((q, "ε"), frozenset())
        new = targets - seen
        seen.update(new)
        pending.extend(sorted(new, reverse=True))
        if trace is not None:
            trace.record("epsilon_expand", before,
                         {"states": sorted(seen), "pending": list(pending)},
                         "Epsilon transitions consume no input.", source=q,
                         targets=sorted(targets), discovered=sorted(new))
    return frozenset(seen)


def compute_epsilon_closure(machine, states):
    trace = Trace("epsilon_closure")
    value = epsilon_closure(machine, states, trace)
    return Result(value, trace)
