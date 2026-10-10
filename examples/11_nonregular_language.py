"""유한 상태로 셀 수 없는 것: 고전적인 {a^n b^n | n≥0}의 비정규성.
실행: python examples/11_nonregular_language.py
Pumping Lemma는 정규성의 필요조건이므로, 그 조건을 깨면 비정규성을 증명할 수 있습니다.
"""
from pathlib import Path
from formal_language_engine import EqualBlocks, prove_nonregular, verify_certificate

OUTPUT = Path(__file__).resolve().parents[1] / 'outputs' / Path(__file__).stem
language = EqualBlocks('a', 'b')
proof = prove_nonregular(language, pumping_exponent=0)
assert proof.value.status == 'proven'
assert verify_certificate(language, proof.value.certificate) is not None
proof.export_png(OUTPUT)

# p는 고정된 실험값이 아니라 임의의 양의 정수입니다. witness는 a^p b^p.
# |xy|≤p, |y|>0이면 모든 유효한 분할에서 y=a^t, 1≤t≤p입니다.
# i=0으로 펌핑하면 a^(p-t)b^p가 되어 개수가 달라집니다.
# '내가 선택한 분할 하나'가 아니라 '가능한 모든 분할'을 처리해야 합니다.
# 양화 순서: 모든 p → witness 선택 → 모든 유효 분할 → 깨뜨리는 i 선택.
for step in proof.trace.steps:
    if step.operation == 'symbolic_deduction':
        print(step.reason)

# 현재 커널은 명시적으로 지원하는 언어 계열과 witness의 기호적 스키마를 검사합니다.
# 임의의 언어에 대해 자동으로 새로운 증명을 발명하는 범용 증명기는 아닙니다.
# 직접 바꾸기: i=2로도 같은 개수 불일치가 생기는지 확인해 보세요.
print('기호적 증명 그림:', OUTPUT / 'answer.png')
