"""경로를 정규표현식으로 요약하기: 상태 제거.
실행: python examples/08_state_elimination.py
언어: 길이가 3의 배수인 x 문자열. 결과 식의 모양은 제거 순서에 따라 달라집니다.
"""
from pathlib import Path
from formal_language_engine import DFA, automaton_to_regex, parse_regex

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
machine = DFA(states={'r0', 'r1', 'r2'}, alphabet={'x'}, initial='r0', accepting={'r0'},
              transitions={('r0', 'x'): 'r1', ('r1', 'x'): 'r2', ('r2', 'x'): 'r0'})
ORDER = ['r1', 'r2', 'r0']  # 직접 바꾸기: 세 상태의 다른 순열을 넣어 보세요.
result = automaton_to_regex(machine, elimination_order=ORDER)
result.export_png(OUTPUT)
assert result.regex.to_nfa().equivalent_to(parse_regex('(xxx)*').to_nfa())
print('최종 식:', result.regex)

# k를 제거할 때 R'ij = Rij ∪ Rik(Rkk)*Rkj.
# 경로는 k를 거치지 않거나, k로 들어가 0번 이상 돌고 나오는 두 경우입니다.
# 라벨이 '이미 제거한 상태를 내부에서 거칠 수 있는 경로'를 나타낸다는 불변식을
# 유지하면, 마지막 시작→종료 라벨이 원래 언어를 나타냅니다.
# PNG는 초기 GNFA 한 장 + 상태 제거마다 한 장입니다. 세부 라벨 계산은 JSON에도 남습니다.
print('상태 제거 그림과 계산표:', OUTPUT)
