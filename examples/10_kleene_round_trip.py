"""Kleene 정리의 구성적 두 방향을 따라가기.
실행: python examples/10_kleene_round_trip.py
정리: 정규표현식으로 나타낼 수 있는 언어와 유한 오토마타가 인식하는 언어는 같습니다.
"""
from pathlib import Path
from formal_language_engine import regex_to_nfa, convert_nfa_to_dfa, minimize_dfa, automaton_to_regex

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
EXPRESSION = '(ab)*'  # 작게 시작합니다. 직접 바꾸기: a(b∪c)*.

# 첫 방향: 정규표현식 → ε-NFA. 기호와 합집합/연결/star에 대한 구조적 귀납.
forward = regex_to_nfa(EXPRESSION)
forward.export_png(OUTPUT / '01_regex_to_nfa')

# 비결정성이 표현력을 늘리지 않는다는 정리의 구성: ε-NFA → DFA.
deterministic = convert_nfa_to_dfa(forward.machine)
deterministic.export_png(OUTPUT / '02_nfa_to_dfa')

# 최소화는 정리의 필수 단계가 아닙니다. 뒤의 상태 제거 그림을 읽기 쉽게 줄입니다.
small = minimize_dfa(deterministic.machine).machine
small.render_sheet(OUTPUT / '03_minimal.png', title='Same language, fewer states')

# 반대 방향: DFA → GNFA → 정규표현식. 제거된 상태를 거치는 경로를 라벨로 요약.
backward = automaton_to_regex(small)
backward.export_png(OUTPUT / '04_dfa_to_regex')
assert forward.machine.equivalent_to(backward.regex.to_nfa())
print('처음:', EXPRESSION)
print('돌아온 식:', backward.regex)
print('표기가 달라도 언어는 정확히 같습니다.')

# 중요한 구분: 이 실행은 한 입력에 대한 검증입니다.
# 일반 정리는 05의 구조적 귀납, 03의 부분집합 불변식, 08의 경로 불변식으로 논증합니다.
# 유한한 예제를 많이 실행했다는 이유만으로 모든 정규표현식에 대한 정리가 증명되지는 않습니다.
print('두 방향의 구성 과정:', OUTPUT)
