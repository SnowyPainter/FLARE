from dataclasses import dataclass, asdict
from ..core.language import EqualBlocks, RepeatedWord
from ..core.trace import Trace, Result
from .decomposition import Block, ParametricWord
from .symbolic_verifier import Certificate, verify_certificate
from .witness_search import bounded_search


@dataclass(frozen=True)
class ProofOutcome:
    status: str
    explanation: str
    certificate: Certificate | None = None


def prove_nonregular(language, *, witness=None, pumping_exponent=0, **search_bounds):
    if type(pumping_exponent) is not int or pumping_exponent not in (0, 2):
        raise ValueError("Supported symbolic pumping exponents are 0 and 2")
    trace = Trace("pumping", metadata={"language": language.describe(),
                                      "quantifiers": "for every p>=1, exists W in L, |W|>=p, for every valid split, exists i>=0: xy^iz not in L"})
    certificate = None
    if type(language) is EqualBlocks:
        default = ParametricWord((Block(language.a, 1), Block(language.b, 1)))
        certificate = Certificate("equal_blocks", witness if witness is not None else default, language.a, language.b,
                                  pumping_exponent=pumping_exponent)
    elif type(language) is RepeatedWord and language.copies >= 2 and len(language.alphabet) >= 2:
        a, b = sorted(language.alphabet)[:2]
        default = ParametricWord((Block(a, 1), Block(b, 0, 1)) * language.copies)
        certificate = Certificate("repeated_word", witness if witness is not None else default, a, b, language.copies,
                                  pumping_exponent=pumping_exponent)
    derivation = verify_certificate(language, certificate)
    if derivation is not None:
        trace.metadata["certificate"] = asdict(certificate)
        state = {"assumptions": language.describe(), "verified_steps": []}
        for statement in derivation:
            after = {**state, "verified_steps": [*state["verified_steps"], statement]}
            trace.record("symbolic_deduction", state, after, statement,
                         symbol_mapping={"a": certificate.a, "b": certificate.b}, copies=certificate.copies)
            state = after
        outcome = ProofOutcome("proven", "Universal symbolic certificate verified for this language and witness.", certificate)
    else:
        trace.record("symbolic_unavailable", language.describe(), {"certificate_verified": False},
                     "No supported symbolic certificate matched. Bounded search cannot prove nonregularity.")
        status, explanation = bounded_search(language, trace, witness=witness, **search_bounds)
        outcome = ProofOutcome(status, explanation)
    trace.record("conclusion", {}, {"status": outcome.status, "explanation": outcome.explanation},
                 "Only a verified universal symbolic certificate permits status=proven.")
    return Result(outcome, trace)
