"""작은 실험이 정반대 결론을 암시하는 사례.
실행: python examples/12_experiments_are_not_proofs.py
정규 언어인 {a^(3n) | n≥0}도 잘못 잡은 작은 p에 대해서는 펌핑 조건이 깨집니다.
"""
from pathlib import Path
from formal_language_engine import PredicateLanguage, prove_nonregular, parse_regex

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
language = PredicateLanguage('length divisible by three', {'a'}, lambda w: len(w) % 3 == 0)
regular_machine = parse_regex('(aaa)*').to_nfa()
regular_machine.render_sheet(OUTPUT / 'regular.png', title='A regular language: (aaa)*')

# p=1, witness=aaa에서는 y가 첫 a 하나일 수밖에 없습니다.
# i=0이면 aa이므로 언어 밖입니다. 그러나 p=1만 확인해서는 아무 일반 결론도 못 냅니다.
small = prove_nonregular(language, witness=lambda p: 'a' * 3, max_p=1, max_i=3)
assert small.value.status == 'unknown'
print('p=1까지만 탐색:', small.value.status)

# p=3이라면 y=aaa라는 합법적 분할이 있습니다. 어느 i≥0으로 펌핑해도 길이는 3의 배수입니다.
# 정규 언어에는 '어떤 적절한 p가 존재'하면 되며, 모든 작은 p가 작동할 필요는 없습니다.
larger = prove_nonregular(language, witness=lambda p: 'a' * 3, max_p=3, max_i=3)
assert larger.value.status == 'search_failed'
print('p=3까지 탐색:', larger.value.status)

# search_failed 자체가 정규성 증명은 아닙니다. 여기서는 위의 정규표현식이 정규성을 증명합니다.
# 세부 실험이 필요할 때만 로그를 저장합니다. 내부 시도마다 PNG를 잔뜩 만들지는 않습니다.
small.trace.export_json(OUTPUT / 'small_search.json')
larger.trace.export_json(OUTPUT / 'larger_search.json')
# 직접 바꾸기: 배수를 4로 바꾸고 witness, 정규표현식, max_p도 함께 수정해 보세요.
print('그림과 탐색 기록:', OUTPUT)
