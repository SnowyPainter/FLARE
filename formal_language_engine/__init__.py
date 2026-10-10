"""Python-first formal languages library. Functional algorithms always return Result."""
from .core.automata import DFA, NFA
from .core.parser import parse_regex, parse_machine
from .core.regex_ast import Regex, Union, Concat, Star, Symbol, Epsilon, EmptySet, union, concat, star, simplify
from .core.trace import Trace, Step, Result
from .core.language import EqualBlocks, RepeatedWord, PredicateLanguage
from .algorithms.subset_construction import convert_nfa_to_dfa
from .algorithms.thompson import regex_to_nfa
from .algorithms.gnfa import automaton_to_regex
from .algorithms.minimization import minimize_dfa
from .algorithms.equivalence import check_equivalence
from .algorithms.simulation import simulate
from .algorithms.epsilon_closure import compute_epsilon_closure
from .proof.pumping import prove_nonregular, ProofOutcome
from .proof.decomposition import Block, ParametricWord, decompositions
from .proof.symbolic_verifier import Certificate, verify_certificate

ENFA = NFA

__all__ = [
    "DFA", "NFA", "ENFA", "parse_regex", "parse_machine", "Regex", "Union", "Concat",
    "Star", "Symbol", "Epsilon", "EmptySet", "union", "concat", "star", "simplify",
    "Trace", "Step", "Result", "EqualBlocks", "RepeatedWord", "PredicateLanguage",
    "convert_nfa_to_dfa", "regex_to_nfa", "automaton_to_regex", "minimize_dfa",
    "check_equivalence", "simulate", "compute_epsilon_closure", "prove_nonregular",
    "ProofOutcome", "Block", "ParametricWord", "decompositions", "Certificate", "verify_certificate",
]
