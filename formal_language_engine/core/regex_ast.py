"""Immutable regular expression AST with canonical local simplification."""
from __future__ import annotations
from dataclasses import dataclass
import json


class Regex:
    def __or__(self, other):
        return union(self, other)

    def __add__(self, other):
        return concat(self, other)

    def star(self):
        return star(self)

    def to_nfa(self, trace=False, output_dir=None):
        from ..algorithms.thompson import regex_to_nfa
        from .trace import finish
        return finish(regex_to_nfa(self), trace, output_dir)

    def matches(self, word):
        return self.to_nfa().test(word)


@dataclass(frozen=True)
class EmptySet(Regex):
    def __str__(self):
        return "∅"


@dataclass(frozen=True)
class Epsilon(Regex):
    def __str__(self):
        return "ε"


@dataclass(frozen=True)
class Symbol(Regex):
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not self.value or self.value == "ε":
            raise ValueError("A symbol must be nonempty and cannot be ε")

    def __str__(self):
        if len(self.value) == 1 and self.value not in '∪|*()·\\ε∅\"' and not self.value.isspace():
            return self.value
        return json.dumps(self.value, ensure_ascii=False)


@dataclass(frozen=True)
class Union(Regex):
    left: Regex
    right: Regex

    def __str__(self):
        return f"{self.left}∪{self.right}"


@dataclass(frozen=True)
class Concat(Regex):
    left: Regex
    right: Regex

    def __str__(self):
        def wrap(r):
            return f"({r})" if isinstance(r, Union) else str(r)
        return wrap(self.left) + wrap(self.right)


@dataclass(frozen=True)
class Star(Regex):
    child: Regex

    def __str__(self):
        r = self.child
        return (f"({r})" if isinstance(r, (Union, Concat)) else str(r)) + "*"


EMPTY = EmptySet()
EPSILON = Epsilon()


def union(*expressions):
    terms = set()
    def collect(r):
        if isinstance(r, Union):
            collect(r.left)
            collect(r.right)
        elif not isinstance(r, EmptySet):
            terms.add(r)
    for r in expressions:
        collect(r)
    ordered = sorted(terms, key=str)
    if not ordered:
        return EMPTY
    result = ordered[0]
    for r in ordered[1:]:
        result = Union(result, r)
    return result


def concat(*expressions):
    terms = []
    def collect(r):
        if isinstance(r, Concat):
            collect(r.left)
            collect(r.right)
        elif not isinstance(r, Epsilon):
            terms.append(r)
    for r in expressions:
        collect(r)
    if any(isinstance(r, EmptySet) for r in terms):
        return EMPTY
    if not terms:
        return EPSILON
    result = terms[0]
    for r in terms[1:]:
        result = Concat(result, r)
    return result


def star(r):
    if isinstance(r, (EmptySet, Epsilon)):
        return EPSILON
    return r if isinstance(r, Star) else Star(r)


def simplify(r):
    if isinstance(r, Union):
        return union(simplify(r.left), simplify(r.right))
    if isinstance(r, Concat):
        return concat(simplify(r.left), simplify(r.right))
    if isinstance(r, Star):
        return star(simplify(r.child))
    if not isinstance(r, (Symbol, Epsilon, EmptySet)):
        raise TypeError("Expected a regular expression AST")
    return r
