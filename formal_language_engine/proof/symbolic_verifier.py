"""Small trusted proof kernel for two explicit universally quantified schemas.

This is deliberately not a general theorem prover. No bounded observations or
user-supplied explanations are accepted as proof. Certificates are checked
against exact symbolic language and witness structures, then instantiated into
the algebraic arguments below for arbitrary integers p, s and t.
"""
from dataclasses import dataclass
from ..core.language import EqualBlocks, RepeatedWord
from .decomposition import Block, ParametricWord


@dataclass(frozen=True)
class Certificate:
    scheme: str
    witness: ParametricWord
    a: str
    b: str
    copies: int = 1
    pumping_exponent: int = 0


def verify_certificate(language, certificate):
    """Return a checked symbolic derivation, or None when the certificate is invalid."""
    if type(certificate) is not Certificate or type(certificate.witness) is not ParametricWord:
        return None
    c = certificate
    if type(c.pumping_exponent) is not int or c.pumping_exponent not in (0, 2) or c.a == c.b:
        return None
    i = c.pumping_exponent
    exponent = "p-t" if i == 0 else "p+t"
    comparison = "p-t < p" if i == 0 else "p+t > p"
    if type(c.copies) is not int:
        return None
    if c.scheme == "equal_blocks" and type(language) is EqualBlocks:
        expected = ParametricWord((Block(language.a, 1), Block(language.b, 1)))
        if (c.a, c.b, c.copies, c.witness) != (language.a, language.b, 1, expected):
            return None
        return [
            "Let p >= 1 be arbitrary. Choose W(p) = a^p b^p. It belongs to L and |W| = 2p >= p.",
            "For every W = xyz with |xy| <= p and |y| > 0, x = a^s and y = a^t, where s >= 0, t >= 1, s+t <= p.",
            f"Choose i = {i}. Then xy^{i}z = a^({exponent})b^p. The exponents are nonnegative and {comparison}, so xy^{i}z is not in L.",
            "Thus for every p >= 1 this witness defeats every valid split; the pumping lemma implies L is nonregular.",
        ]
    if c.scheme == "repeated_word" and type(language) is RepeatedWord:
        if c.copies != language.copies or c.copies < 2 or not {c.a, c.b} <= language.alphabet:
            return None
        expected = ParametricWord((Block(c.a, 1), Block(c.b, 0, 1)) * c.copies)
        if c.witness != expected:
            return None
        return [
            "Let p >= 1 be arbitrary and k = copies >= 2. Choose W(p) = (a^p b)^k. This belongs to L and |W| = k(p+1) >= p.",
            "For every valid split, |xy| <= p forces x = a^s and y = a^t, with s >= 0, t >= 1, s+t <= p.",
            f"Choose i = {i}. The pumped string is V = a^({exponent})b(a^p b)^(k-1), with exactly k occurrences of b, and ends in b.",
            "If V = u^k, then u has exactly one b (counts multiply by k). Since V ends in b, u ends in b. Since V uses only a and b, u = a^r b for some r >= 0.",
            f"Consequently all k a-runs before successive b symbols must have equal length r. But V has run lengths {exponent},p,...,p; k >= 2 and t >= 1 make them unequal." + (" This also covers t = p and an empty first run." if i == 0 else ""),
            "Therefore V is not in L for every valid split and every p >= 1. By the pumping lemma L is nonregular.",
        ]
    return None
