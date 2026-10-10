from collections import deque
from dataclasses import dataclass
from ..core.trace import Trace, Result
from .epsilon_closure import epsilon_closure


@dataclass(frozen=True)
class Equivalence:
    equivalent: bool
    counterexample: str | tuple[str, ...] | None
    tokens: tuple[str, ...] | None


def check_equivalence(left, right):
    trace = Trace("equivalence", metadata={"left": left.snapshot(), "right": right.snapshot()})
    alphabet = sorted(left.alphabet | right.alphabet)
    initial = (epsilon_closure(left, {left.initial}, trace), epsilon_closure(right, {right.initial}, trace))
    queue = deque([initial])
    parents = {initial: None}

    def state(pair):
        return {"left": sorted(pair[0]), "right": sorted(pair[1])}

    def move(machine, subset, a):
        targets = set().union(*(machine.transitions.get((q, a), ()) for q in subset))
        return epsilon_closure(machine, targets, trace)

    while queue:
        pair = queue.popleft()
        lfinal, rfinal = bool(pair[0] & left.accepting), bool(pair[1] & right.accepting)
        trace.record("compare_acceptance", state(pair), {**state(pair), "left_accepts": lfinal, "right_accepts": rfinal},
                     "A product state distinguishes the languages iff exactly one component accepts.")
        if lfinal != rfinal:
            word = []
            cursor = pair
            while parents[cursor] is not None:
                cursor, a = parents[cursor]
                word.append(a)
            tokens = tuple(reversed(word))
            counterexample = "".join(tokens) if all(len(a) == 1 for a in alphabet) else tokens
            trace.record("counterexample", state(pair), {"equivalent": False, "tokens": list(tokens)},
                         "Breadth-first search finds a counterexample of minimum token length.")
            return Result(Equivalence(False, counterexample, tokens), trace)
        for a in alphabet:
            target = (move(left, pair[0], a), move(right, pair[1], a))
            discovered = target not in parents
            if discovered:
                parents[target] = (pair, a)
                queue.append(target)
            trace.record("product_transition", state(pair), state(target),
                         "Explore the synchronized subset product over the union alphabet.",
                         symbol=a, discovered=discovered)
    trace.record("equivalent", {}, {"equivalent": True, "visited_pairs": len(parents)},
                 "Every reachable product state agrees on acceptance.")
    return Result(Equivalence(True, None, None), trace)
