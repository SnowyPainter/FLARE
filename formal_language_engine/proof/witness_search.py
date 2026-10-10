from itertools import product
from .decomposition import decompositions, ParametricWord


def bounded_search(language, trace, *, witness=None, max_p=3, max_word_length=8,
                   max_i=3, max_candidates=10000):
    """Finite evidence only. This function can never return a proof certificate."""
    for name, value in {"max_p": max_p, "max_word_length": max_word_length,
                        "max_i": max_i, "max_candidates": max_candidates}.items():
        if type(value) is not int or value < (0 if name in ("max_i", "max_word_length") else 1):
            raise ValueError(f"Invalid search bound: {name}")
    tested = 0
    found = []
    for p in range(1, max_p + 1):
        if witness is not None:
            candidates = [witness.at(p) if isinstance(witness, ParametricWord) else witness(p)]
        else:
            candidates = ("".join(tokens) for n in range(p, max_word_length + 1)
                          for tokens in product(sorted(language.alphabet), repeat=n))
        success = False
        for word in candidates:
            if tested >= max_candidates:
                return "unknown", "Candidate budget exhausted; no universal conclusion is possible."
            tested += 1
            if not isinstance(word, str):
                raise ValueError("Witness must produce a string")
            eligible = len(word) >= p and language.contains(word)
            trace.record("candidate", {"p": p}, {"word": word, "eligible": eligible},
                         "A witness must belong to L and have length at least p.")
            if not eligible:
                continue
            defeats_all = True
            for x, y, z in decompositions(word, p):
                refuted = False
                for i in range(max_i + 1):
                    pumped = x + y * i + z
                    member = language.contains(pumped)
                    trace.record("pump_trial", {"p": p, "word": word, "x": x, "y": y, "z": z},
                                 {"i": i, "pumped": pumped, "member": member},
                                 "A finite trial tests this split only; it is not a universal proof.")
                    if not member:
                        refuted = True
                        break
                if not refuted:
                    defeats_all = False
                    break
            if defeats_all:
                found.append({"p": p, "word": word})
                success = True
                break
        if not success:
            trace.metadata["bounded_witnesses"] = found
            return "search_failed", f"No defeating witness found for p={p} within the supplied bounds/candidates. This does not establish regularity."
    trace.metadata["bounded_witnesses"] = found
    return "unknown", "Finite witnesses found, but no certificate quantifies over every p and split."
