def validate_machine(machine, *, exact_states=None, min_states=None, max_states=None,
                     complete=False, reachable=False):
    errors = []
    if not machine.states or any(not isinstance(q, str) or not q for q in machine.states):
        errors.append("states must contain nonempty string names")
    if any(not isinstance(a, str) or not a or a == "ε" for a in machine.alphabet):
        errors.append("alphabet must contain nonempty strings other than ε")
    if machine.initial not in machine.states:
        errors.append("initial state is not in states")
    if not machine.accepting <= machine.states:
        errors.append("accepting states must be in states")
    for (q, a), targets in machine.transitions.items():
        if q not in machine.states or not targets <= machine.states:
            errors.append(f"unknown state in transition {(q, a)}")
        if a not in machine.alphabet and a != "ε":
            errors.append(f"unknown symbol {a}")
        if machine.deterministic and (a == "ε" or len(targets) != 1):
            errors.append("DFA transitions require one target and no epsilon edges")
    n = len(machine.states)
    if exact_states is not None and n != exact_states:
        errors.append(f"expected {exact_states} states, got {n}")
    if min_states is not None and n < min_states:
        errors.append(f"expected at least {min_states} states, got {n}")
    if max_states is not None and n > max_states:
        errors.append(f"expected at most {max_states} states, got {n}")
    if complete and any(not machine.transitions.get((q, a)) for q in machine.states for a in machine.alphabet):
        errors.append("transition table is not complete")
    if reachable:
        seen = {machine.initial}
        pending = [machine.initial]
        while pending:
            q = pending.pop()
            for (source, _), targets in machine.transitions.items():
                if source == q:
                    pending.extend(targets - seen)
                    seen.update(targets)
        if seen != machine.states:
            errors.append("machine contains unreachable states")
    if errors:
        raise ValueError("; ".join(errors))
    return True
