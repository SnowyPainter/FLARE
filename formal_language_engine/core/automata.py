from __future__ import annotations
from types import MappingProxyType
from .trace import finish

EPSILON_SYMBOL = "ε"


class NFA:
    deterministic = False

    def __init__(self, *, states, alphabet, initial, accepting, transitions):
        self.states = frozenset(states)
        self.alphabet = frozenset(alphabet)
        self.initial = initial
        self.accepting = frozenset(accepting)
        normalized = {}
        for key, targets in transitions.items():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError("Transition keys must be (state, symbol) pairs")
            source, symbol = key
            symbol = EPSILON_SYMBOL if symbol == "" else symbol
            if self.deterministic:
                if not isinstance(targets, str):
                    raise ValueError("DFA targets must be state names")
                targets = {targets}
            elif isinstance(targets, str):
                targets = {targets}
            normalized.setdefault((source, symbol), set()).update(targets)
        self.transitions = MappingProxyType({k: frozenset(v) for k, v in normalized.items()})
        self.trace = None
        self.validate()

    def validate(self, **constraints):
        from ..validation.machine_validator import validate_machine
        return validate_machine(self, **constraints)

    def snapshot(self):
        return {"kind": "automaton", "type": "DFA" if self.deterministic else "NFA",
                "states": sorted(self.states), "alphabet": sorted(self.alphabet),
                "initial": self.initial, "accepting": sorted(self.accepting),
                "transitions": [{"from": q, "symbol": a, "to": sorted(targets)}
                                for (q, a), targets in sorted(self.transitions.items())]}

    def to_json(self):
        import json
        data = self.snapshot()
        if self.deterministic:
            for edge in data["transitions"]:
                edge["to"] = edge["to"][0]
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_text(cls, text):
        from .parser import parse_machine
        machine = parse_machine(text)
        if cls is DFA and not isinstance(machine, DFA):
            raise ValueError("Expected a DFA definition")
        return machine

    def render(self, path):
        from ..visualization.automata_renderer import render_automaton
        return render_automaton(self.snapshot(), path)

    def render_sheet(self, path, *, title="Automaton", notes=()):
        """Render the state diagram and transition table on one PNG worksheet."""
        from ..visualization.solution_renderer import render_machine_sheet
        return render_machine_sheet(self, path, title=title, notes=notes)

    def simulate(self, word, trace=False, output_dir=None):
        from ..algorithms.simulation import simulate
        result = simulate(self, word)
        if trace or output_dir is not None:
            result.export_png(output_dir or "outputs/simulation")
        return result

    def test(self, word):
        return self.simulate(word).value

    def to_dfa(self, trace=False, output_dir=None):
        from ..algorithms.subset_construction import convert_nfa_to_dfa
        return finish(convert_nfa_to_dfa(self), trace, output_dir)

    def to_regex(self, method="gnfa", trace=False, output_dir=None, elimination_order=None):
        from ..algorithms.gnfa import automaton_to_regex
        if method != "gnfa":
            raise ValueError("Only the gnfa method is supported")
        return finish(automaton_to_regex(self, elimination_order=elimination_order), trace, output_dir)

    def equivalent_to(self, other):
        from ..algorithms.equivalence import check_equivalence
        return check_equivalence(self, other).value.equivalent

    def find_counterexample(self, other):
        from ..algorithms.equivalence import check_equivalence
        return check_equivalence(self, other).value.counterexample


class DFA(NFA):
    """Partial transitions are allowed and mean rejection; complete=True enforces totality."""
    deterministic = True

    def minimize(self, trace=False, output_dir=None):
        from ..algorithms.minimization import minimize_dfa
        return finish(minimize_dfa(self), trace, output_dir)
