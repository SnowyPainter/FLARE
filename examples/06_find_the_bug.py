"""그럴듯한 식을 반례로 반박하기.
실행: python examples/06_find_the_bug.py
질문: a*(b∪c)와 a*b∪c는 정말 같은 언어일까요?
"""
from pathlib import Path
from formal_language_engine import parse_regex, check_equivalence

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
left = parse_regex('a*(b∪c)').to_nfa()
wrong = parse_regex('a*b∪c').to_nfa()
result = check_equivalence(left, wrong)
word = result.value.counterexample
assert word is not None
print('가장 짧은 반례:', repr(word))  # ac: 오른쪽 c 앞에는 a*가 없습니다.
print('왼쪽:', left.test(word), '오른쪽:', wrong.test(word))
assert left.test(word) != wrong.test(word)

# 올바른 분배법칙: R(S∪T) = RS∪RT.
# 언어 차원에서, 뒤 단어가 S 또는 T에 속한다는 두 경우로 나누면 증명됩니다.
# 아래 호출은 그 일반 법칙 전체가 아니라 이 구체적 식의 동치성을 판정합니다.
fixed = parse_regex('a*b∪a*c').to_nfa()
assert left.equivalent_to(fixed)
left.render_sheet(OUTPUT / 'left.png', title='a*(b∪c)')
wrong.render_sheet(OUTPUT / 'wrong.png', title='a*b∪c: counterexample = ' + repr(word))
fixed.render_sheet(OUTPUT / 'fixed.png', title='a*b∪a*c: equivalent')
# 직접 바꾸기: a∪b와 ab, (ab)*와 a*b*를 비교해 보세요.
# 주의: 반례가 ''일 수 있습니다. `if word`가 아니라 `word is not None`으로 확인합니다.
print('그림:', OUTPUT)
