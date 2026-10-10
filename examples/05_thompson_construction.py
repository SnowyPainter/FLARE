"""정규표현식을 작은 회로처럼 조립하기: Thompson 구성.
실행: python examples/05_thompson_construction.py
언어: ab 블록과 c 블록을 원하는 순서로 0번 이상 연결한 문자열.
"""
from pathlib import Path
from formal_language_engine import regex_to_nfa

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
EXPRESSION = '(ab∪c)*'  # 직접 바꾸기: ab(c∪ε), (a∪b)c, ∅*도 비교해 보세요.

# 문자열을 직접 넘겨야 원래 연산 구조가 남습니다.
# 미리 단순화한 AST를 넘기면, 없어진 연산을 그림에서 다시 복원할 수 없습니다.
result = regex_to_nfa(EXPRESSION)
result.export_png(OUTPUT)
for step in result.trace.steps:
    print(step.operation, '→', step.details['expression'])

# 기호: 한 간선. 연결: 앞 출구와 뒤 입구를 ε로 연결.
# 합집합: 두 조각 중 하나로 갈 수 있게 분기. star: 생략 경로와 반복 경로 추가.
# 각 조각의 입구→출구 경로가 그 부분식의 언어와 일치한다는 불변식을 사용합니다.
# 기호의 기초 사례와 세 조립 규칙을 정당화하면 구조적 귀납법의 뼈대가 됩니다.
print('빈 문자열 수락:', result.machine.test(''))
print('한 연산당 한 그림. 마지막 그림이 전체 NFA:', OUTPUT)
