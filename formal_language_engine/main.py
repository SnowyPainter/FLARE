"""Optional command line entry point; Python scripts are the primary interface."""
import argparse
from pathlib import Path
from . import parse_machine, regex_to_nfa, convert_nfa_to_dfa, minimize_dfa, automaton_to_regex


def main():
    parser = argparse.ArgumentParser(description="Run automata conversions and export every step as PNG + JSON")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--regex", help="Regular expression, e.g. (a∪b)*abb")
    source.add_argument("--machine", type=Path, help="JSON machine file")
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--gnfa", action="store_true", help="Also run GNFA elimination (potentially large output)")
    parser.add_argument("--word", action="append", default=[], help="Simulate a word; repeat as needed")
    args = parser.parse_args()
    if args.regex is not None:
        result = regex_to_nfa(args.regex)
        result.export_png(args.output / "thompson")
        machine = result.machine
    else:
        machine = parse_machine(args.machine.read_text(encoding="utf-8"))
    machine.render(args.output / "original.png")
    result = convert_nfa_to_dfa(machine)
    result.export_png(args.output / "nfa_to_dfa")
    minimal = minimize_dfa(result.machine)
    minimal.export_png(args.output / "minimization")
    minimal.machine.render(args.output / "minimal.png")
    for index, word in enumerate(args.word):
        simulation = machine.simulate(word)
        simulation.export_png(args.output / f"simulation_{index:03d}")
        print(f"{word!r}: {'ACCEPT' if simulation.value else 'REJECT'}")
    if args.gnfa:
        converted = automaton_to_regex(minimal.machine)
        converted.export_png(args.output / "gnfa")
        print(f"Regular expression: {converted.regex}")
    print(f"Outputs: {args.output.resolve()}")


if __name__ == "__main__":
    main()
