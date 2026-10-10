"""상태에 의미 붙이기: 이진수의 나머지 계산.
실행: python examples/02_binary_remainders.py
핵심: 이진수 뒤에 bit를 붙이면 값이 2*n + bit가 됩니다.
"""
from pathlib import Path
from formal_language_engine import DFA

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
DIVISOR = 3  # 직접 바꾸기: 5나 7로 바꿔도 같은 원리로 작동합니다.
assert DIVISOR >= 1
states = {f'r{r}' for r in range(DIVISOR)}
transitions = {}
for r in range(DIVISOR):
    for bit in ('0', '1'):
        transitions[f'r{r}', bit] = f'r{(2 * r + int(bit)) % DIVISOR}'

# 불변식: 접두사를 읽은 뒤 상태 r은 그 접두사 수치의 DIVISOR에 대한 나머지입니다.
# 처음에는 0이고, 위 전이가 불변식을 보존합니다. 따라서 r0에서 끝나면 배수입니다.
# 여기서는 빈 문자열의 수치를 0으로 약속하며, 앞쪽 0도 허용합니다.
machine = DFA(states=states, alphabet={'0', '1'}, initial='r0', accepting={'r0'}, transitions=transitions)
machine.validate(complete=True)
machine.render_sheet(OUTPUT / 'machine.png', title=f'02 | Binary value modulo {DIVISOR}')
for word in ['', '0', '11', '101', '110', '1001']:
    value = int(word or '0', 2)
    assert machine.test(word) == (value % DIVISOR == 0)
    print(repr(word), '값:', value, '수락:', machine.test(word))
print('그림:', OUTPUT)
