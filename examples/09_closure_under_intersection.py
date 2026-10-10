"""정규 언어의 교집합 닫힘: 두 머신을 동시에 실행하는 곱 구성.
실행: python examples/09_closure_under_intersection.py
사례: 길이가 2의 배수이면서 3의 배수인 x 문자열 = 길이가 6의 배수인 문자열.
"""
from pathlib import Path
from formal_language_engine import DFA, parse_regex

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
LEFT_MODULUS = 2
RIGHT_MODULUS = 3
assert LEFT_MODULUS >= 1 and RIGHT_MODULUS >= 1

# 일반 구성 Q = Q1×Q2, δ((p,q),a) = (δ1(p,a),δ2(q,a)).
# 두 좌표가 같은 입력을 각각 기억하므로, 둘 다 수락할 때만 수락하면 교집합입니다.
# 유한 집합 둘의 곱은 유한하므로 결과도 유한 오토마타입니다. 이것이 닫힘 증명의 핵심입니다.
pairs = [(i, j) for i in range(LEFT_MODULUS) for j in range(RIGHT_MODULUS)]
name = lambda i, j: f'{i},{j}'
machine = DFA(
    states={name(i, j) for i, j in pairs}, alphabet={'x'}, initial=name(0, 0), accepting={name(0, 0)},
    transitions={(name(i, j), 'x'): name((i + 1) % LEFT_MODULUS, (j + 1) % RIGHT_MODULUS) for i, j in pairs},
)
machine.render_sheet(OUTPUT / 'intersection.png', title='Product construction: both coordinates accept')
from math import lcm
period = lcm(LEFT_MODULUS, RIGHT_MODULUS)
assert machine.equivalent_to(parse_regex('(' + 'x' * period + ')*').to_nfa())
print('수락하는 길이의 주기:', period)

# 여집합도 만들어 보기: 완전 DFA에서 수락/비수락을 뒤집으면 됩니다.
# 누락 전이가 있는 부분 DFA는 먼저 sink를 추가해 완전하게 만들어야 합니다.
machine.validate(complete=True)
complement = DFA(states=machine.states, alphabet=machine.alphabet, initial=machine.initial,
                 accepting=machine.states - machine.accepting,
                 transitions={key: next(iter(value)) for key, value in machine.transitions.items()})
complement.render_sheet(OUTPUT / 'complement.png', title='Complement over {x}*: not both accepting')
for n in range(13):
    assert complement.test('x' * n) != machine.test('x' * n)
# 직접 바꾸기: 모듈러스를 2와 4로 바꾸고 도달 불가능한 상태가 생기는 이유를 찾아보세요.
print('그림:', OUTPUT)
