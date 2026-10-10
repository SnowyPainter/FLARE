"""최소화와 Myhill–Nerode 정리의 핵심: 미래 입력으로 구별되는가?
실행: python examples/07_why_two_states_are_necessary.py
언어: x의 개수가 짝수인 문자열. 일부러 4개 상태로 만들어 봅니다.
"""
from pathlib import Path
from formal_language_engine import DFA, minimize_dfa

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
machine = DFA(
    states={'r0', 'r1', 'r2', 'r3'}, alphabet={'x'}, initial='r0', accepting={'r0', 'r2'},
    transitions={(f'r{i}', 'x'): f'r{(i + 1) % 4}' for i in range(4)},
)
result = minimize_dfa(machine)
assert machine.equivalent_to(result.machine)
assert len(result.machine.states) == 2
machine.render_sheet(OUTPUT / 'before.png', title='Before: four remembered remainders')
result.machine.render_sheet(OUTPUT / 'after.png', title='After: even and odd are enough')
for step in result.trace.steps:
    if step.operation in {'initial_partition', 'refine_partition'}:
        print(step.operation, step.after['partitions'])

# 상한: 위의 2상태 DFA가 이 언어를 인식하므로 2개면 충분합니다.
# 하한: 접두사 ε와 x는 뒤에 ε를 붙였을 때 수락 여부가 다릅니다.
# 같은 상태에 도착했다면 같은 접미사에 대한 결과도 같아야 하므로 모순입니다.
# 따라서 어떤 DFA도 두 접두사를 같은 상태로 합칠 수 없습니다. 최소 상태 수는 정확히 2.
# 이는 u~v ⇔ 모든 접미사 z에 대해 uz∈L ↔ vz∈L 이라는 Nerode 동치의 작은 사례입니다.
assert machine.test('') != machine.test('x')
# 직접 바꾸기: 수락 상태를 {'r0'}로 바꾸면 왜 4상태가 필요할까요?
# 이때 위의 상태 수 assert와 하한 논증도 함께 수정해야 합니다.
print('그림:', OUTPUT)
