"""Regex syntax and a JSON text format (never eval user input)."""
import json
from .regex_ast import Symbol, Union, Concat, Star, EMPTY, EPSILON, union, concat, star


def parse_regex(text, *, simplify=True):
    """Set simplify=False to preserve every construction in the input syntax."""
    make_union = union if simplify else Union
    make_star = star if simplify else Star

    def make_concat(parts):
        if simplify:
            return concat(*parts)
        result = parts[0]
        for part in parts[1:]:
            result = Concat(result, part)
        return result
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == '"':
            value, length = json.JSONDecoder().raw_decode(text[i:])
            tokens.append(Symbol(value))
            i += length
            continue
        if c == "\\":
            i += 1
            if i == len(text):
                raise ValueError("Trailing escape")
            tokens.append(Symbol(text[i]))
        elif c in "∪|*()·":
            tokens.append(c)
        else:
            tokens.append(EPSILON if c == "ε" else EMPTY if c == "∅" else Symbol(c))
        i += 1
    pos = 0

    def expression():
        nonlocal pos
        result = sequence()
        while pos < len(tokens) and tokens[pos] in ("∪", "|"):
            pos += 1
            result = make_union(result, sequence())
        return result

    def sequence():
        nonlocal pos
        parts = []
        while pos < len(tokens) and tokens[pos] not in (")", "∪", "|"):
            if tokens[pos] == "·":
                if not parts:
                    raise ValueError("Missing left operand of concatenation")
                pos += 1
                if pos == len(tokens) or tokens[pos] in ("·", ")", "∪", "|"):
                    raise ValueError("Missing right operand of concatenation")
            parts.append(atom())
        if not parts:
            raise ValueError("Missing expression; use ε for the empty word")
        return make_concat(parts)

    def atom():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token == "(":
            result = expression()
            if pos == len(tokens) or tokens[pos] != ")":
                raise ValueError("Unclosed parenthesis")
            pos += 1
        elif isinstance(token, str):
            raise ValueError(f"Unexpected operator {token}")
        else:
            result = token
        while pos < len(tokens) and tokens[pos] == "*":
            result = make_star(result)
            pos += 1
        return result

    result = expression()
    if pos != len(tokens):
        raise ValueError("Unexpected closing parenthesis")
    return result


def parse_machine(text):
    from .automata import DFA, NFA
    data = json.loads(text)
    kind = data.get("type", "NFA").upper()
    if kind not in ("DFA", "NFA", "Ε-NFA", "ε-NFA".upper()):
        raise ValueError("type must be DFA, NFA, or ε-NFA")
    transitions = {}
    for edge in data["transitions"]:
        key = (edge["from"], edge["symbol"])
        if kind == "DFA":
            if key in transitions:
                raise ValueError(f"Duplicate DFA transition {key}")
            transitions[key] = edge["to"]
        else:
            targets = edge["to"]
            transitions.setdefault(key, set()).update([targets] if isinstance(targets, str) else targets)
    cls = DFA if kind == "DFA" else NFA
    return cls(states=data["states"], alphabet=data["alphabet"], initial=data["initial"],
               accepting=data["accepting"], transitions=transitions)
