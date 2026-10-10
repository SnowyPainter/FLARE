"""NFA는 추측하고, DFA는 가능한 추측을 전부 기억합니다.
실행: python examples/03_nondeterminism.py
언어: a와 b로 된 문자열 중 마지막 두 글자가 ab인 것.
"""
from pathlib import Path
from formal_language_engine import NFA, convert_nfa_to_dfa

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
nfa = NFA(
    states={'scan', 'last_a', 'done'}, alphabet={'a', 'b'},
    initial='scan', accepting={'done'},
    transitions={
        # a를 읽을 때 계속 탐색하거나, 이 a가 끝에서 두 번째라고 추측합니다.
        ('scan', 'a'): {'scan', 'last_a'},
        ('scan', 'b'): {'scan'},
        ('last_a', 'b'): {'done'},
        # done에서 더 읽을 수 없어야 '포함'이 아니라 '끝남'을 검사합니다.
    },
)
result = convert_nfa_to_dfa(nfa)
result.export_png(OUTPUT)
assert nfa.equivalent_to(result.machine)  # 유한 샘플이 아니라 도달 가능한 상태 쌍 전체를 검사합니다.
for word in ['ab', 'aab', 'aba', 'b', '']:
    assert result.machine.test(word) == word.endswith('ab')

# 부분집합 구성의 불변식:
# 입력 u를 읽은 DFA 상태 = NFA가 u를 읽고 있을 수 있는 모든 상태의 집합.
# 초기 집합에서 출발해 각 기호마다 모든 이동을 합치면 이 성질이 보존됩니다.
# 따라서 '수락 상태가 하나라도 있음'이라는 수락 조건까지 일치합니다.
# 직접 바꾸기: done에 a,b self-loop를 넣으면 언어가 어떻게 바뀔까요?
print('step_00부터 마지막까지: DFA 그림, 누적 전이표, 집합 계산표', OUTPUT)
