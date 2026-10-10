"""Symbolic language families and an unrestricted membership-predicate interface."""
from dataclasses import dataclass
from typing import Callable


def _letter(symbol):
    if not isinstance(symbol, str) or len(symbol) != 1:
        raise ValueError("Symbolic string languages require single-character symbols")


@dataclass(frozen=True)
class EqualBlocks:
    """{a^n b^n | n >= 0}, for two distinct characters."""
    a: str = "a"
    b: str = "b"

    def __post_init__(self):
        _letter(self.a)
        _letter(self.b)
        if self.a == self.b:
            raise ValueError("EqualBlocks requires two distinct symbols")

    @property
    def alphabet(self):
        return frozenset((self.a, self.b))

    def contains(self, word):
        return len(word) % 2 == 0 and word == self.a * (len(word) // 2) + self.b * (len(word) // 2)

    def describe(self):
        return {"family": "equal_blocks", "a": self.a, "b": self.b, "n": "integer >= 0"}


@dataclass(frozen=True)
class RepeatedWord:
    """{w^copies | w in alphabet*}; includes {www} with copies=3."""
    alphabet: frozenset[str] = frozenset(("a", "b"))
    copies: int = 3

    def __post_init__(self):
        object.__setattr__(self, "alphabet", frozenset(self.alphabet))
        for symbol in self.alphabet:
            _letter(symbol)
        if type(self.copies) is not int or self.copies < 1:
            raise ValueError("copies must be a positive integer")

    def contains(self, word):
        if not set(word) <= self.alphabet or len(word) % self.copies:
            return False
        return word == word[:len(word) // self.copies] * self.copies

    def describe(self):
        return {"family": "repeated_word", "alphabet": sorted(self.alphabet), "copies": self.copies}


@dataclass(frozen=True)
class PredicateLanguage:
    name: str
    alphabet: frozenset[str]
    predicate: Callable[[str], bool]

    def __post_init__(self):
        object.__setattr__(self, "alphabet", frozenset(self.alphabet))
        for symbol in self.alphabet:
            _letter(symbol)

    def contains(self, word):
        return set(word) <= self.alphabet and bool(self.predicate(word))

    def describe(self):
        return {"family": "predicate", "name": self.name, "alphabet": sorted(self.alphabet)}
