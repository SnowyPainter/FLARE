"""첫 머신: 버튼을 누른 횟수가 짝수인지 기억하기.
실행: python examples/01_two_states.py
먼저 예상해 보기: 아무것도 누르지 않은 빈 문자열은 수락해야 할까요?
"""
from pathlib import Path
from formal_language_engine import DFA

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem

# 상태는 '지금까지 읽은 전체 입력' 대신 미래 판단에 필요한 정보만 기억합니다.
# 0회도 짝수이므로 시작 상태 even은 수락 상태입니다.
machine = DFA(
    states={'even', 'odd'},
    alphabet={'x'},
    initial='even',
    accepting={'even'},
    transitions={('even', 'x'): 'odd', ('odd', 'x'): 'even'},
)
machine.render_sheet(OUTPUT / 'machine.png', title='01 | Remember only parity')
for word in ['', 'x', 'xx', 'xxx', 'xxxx']:
    print(repr(word), machine.test(word))
    assert machine.test(word) == (len(word) % 2 == 0)

# 직접 바꾸기: accepting을 {'odd'}로 바꾸면 어떤 언어가 될까요?
# 위 assert도 새로운 조건으로 바꿔 보세요. 시작 상태와 수락 상태는 다른 개념입니다.
print('그림:', OUTPUT / 'machine.png')
