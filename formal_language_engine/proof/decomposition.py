from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
    symbol: str
    coefficient: int = 0
    constant: int = 0

    def __post_init__(self):
        if not isinstance(self.symbol, str) or len(self.symbol) != 1:
            raise ValueError("A block requires one character")
        if type(self.coefficient) is not int or type(self.constant) is not int:
            raise ValueError("Block exponents must be integer affine expressions")
        if self.coefficient < 0 or self.coefficient + self.constant < 0:
            raise ValueError("Block exponents must be nonnegative for every integer p >= 1")

    def describe(self):
        return {"symbol": self.symbol, "coefficient": self.coefficient, "constant": self.constant}


@dataclass(frozen=True)
class ParametricWord:
    blocks: tuple[Block, ...]

    def __post_init__(self):
        object.__setattr__(self, "blocks", tuple(self.blocks))
        if any(type(block) is not Block for block in self.blocks):
            raise ValueError("ParametricWord requires Block instances")

    def at(self, p):
        if type(p) is not int or p < 1:
            raise ValueError("p must be a positive integer")
        return "".join(block.symbol * (block.coefficient * p + block.constant) for block in self.blocks)

    def describe(self):
        return {"blocks": [b.describe() for b in self.blocks], "parameter": "integer p >= 1"}


def decompositions(word, p):
    if type(p) is not int or p < 1:
        raise ValueError("p must be a positive integer")
    for end in range(1, min(p, len(word)) + 1):
        for start in range(end):
            yield word[:start], word[start:end], word[end:]
