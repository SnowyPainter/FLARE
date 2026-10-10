from ..core.trace import Trace, Result
from .epsilon_closure import epsilon_closure


def simulate(machine, word):
    if isinstance(word, str) and any(len(a) != 1 for a in machine.alphabet):
        raise ValueError("For multi-character alphabet symbols, supply a sequence of tokens")
    tokens = list(word)
    if any(not isinstance(a, str) for a in tokens):
        raise ValueError("Input symbols must be strings")
    trace = Trace("simulation", metadata={"input": machine.snapshot(), "word": tokens})
    current = epsilon_closure(machine, {machine.initial}, trace)

    def snapshot(offset):
        data = machine.snapshot()
        data.update(active=sorted(current), consumed=tokens[:offset], remaining=tokens[offset:])
        return data

    trace.record("start", machine.snapshot(), snapshot(0), "Begin in the initial epsilon closure.")
    for offset, symbol in enumerate(tokens):
        before = snapshot(offset)
        moved = set().union(*(machine.transitions.get((q, symbol), ()) for q in current)) if symbol in machine.alphabet else set()
        current = epsilon_closure(machine, moved, trace)
        trace.record("consume", before, snapshot(offset + 1),
                     "Consume one symbol, then follow all epsilon transitions.", symbol=symbol,
                     outside_alphabet=symbol not in machine.alphabet)
    accepted = bool(current & machine.accepting)
    trace.record("accept" if accepted else "reject", snapshot(len(tokens)),
                 {**snapshot(len(tokens)), "accepted": accepted},
                 "Accept exactly when the final active set intersects the accepting states.")
    return Result(accepted, trace)
