"""ε는 입력을 소비하지 않는 이동이고, ∅는 가능한 단어가 없는 언어입니다.
실행: python examples/04_epsilon_is_not_empty_set.py
작은 토큰 언어: d 또는 +d. d는 실제 숫자 전체가 아니라 한 글자 기호입니다.
"""
from pathlib import Path
from formal_language_engine import NFA, compute_epsilon_closure, convert_nfa_to_dfa, regex_to_nfa

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
nfa = NFA(
    states={'start', 'body', 'done'}, alphabet={'+', 'd'}, initial='start', accepting={'done'},
    transitions={('start', 'ε'): {'body'}, ('start', '+'): {'body'}, ('body', 'd'): {'done'}},
)
closure = compute_epsilon_closure(nfa, {'start'})
assert closure.value == {'start', 'body'}
print('입력을 읽기 전 가능한 상태:', sorted(closure.value))
convert_nfa_to_dfa(nfa).export_png(OUTPUT / 'conversion')
assert nfa.test('d') and nfa.test('+d') and not nfa.test('')

# ε 이동이 있다고 해서 빈 문자열을 무조건 수락하지는 않습니다.
# 시작점의 ε-closure가 수락 상태를 포함해야만 빈 문자열을 수락합니다.
empty_word = regex_to_nfa('ε').machine
empty_language = regex_to_nfa('∅').machine
assert empty_word.test('') and not empty_language.test('')
empty_word.render_sheet(OUTPUT / 'epsilon.png', title='ε: one word, of length zero')
empty_language.render_sheet(OUTPUT / 'empty_set.png', title='∅: no words at all')
# 직접 바꾸기: body도 accepting에 넣고 빈 문자열의 결과를 예상해 보세요.
print('그림:', OUTPUT)
