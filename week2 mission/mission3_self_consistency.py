"""
Mission 3: Self-Consistency

Reference: Wang et al. (2022) "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
https://arxiv.org/abs/2203.11171

[실험 목표]
동일한 문제를 여러 번 풀게 하고 가장 많이 나온 답을 채택하는 Self-Consistency 확인해보기. 
단일 CoT 대비 얼마나 안정적인지 확인합니다.

[과제]
1. 코드를 실행하고 N_SAMPLES번의 추론 과정과 최종 채택 답을 확인하세요.
2. N_SAMPLES를 3, 5, 7로 바꾸며 결과가 달라지는지 실험해보세요.
3. PROBLEM_IDX를 0~4로 바꿔가며 실험해보세요.
4. 실험 결과 확인해보기
   - N_SAMPLES가 늘어날수록 항상 더 좋은 결과가 나왔나요?
   - Self-Consistency가 단일 CoT보다 효과적이었던 문제는 무엇인가요?
"""

import sys, os
import re
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api import chat, print_result
from utils.data import PROBLEMS, FEW_SHOT_EXAMPLES

# =====================
# 여기를 수정하세요
PROBLEM_IDX = 2  # 0~4
N_SAMPLES = 10    # 샘플링 횟수 (많을수록 API 비용 증가)
# =====================

problem = PROBLEMS[PROBLEM_IDX]


def few_shot_cot(question, examples):
    messages = []
    for ex in examples:
        assistant_msg = f"{ex['cot']} The answer is {ex['answer']}."
        messages.append({"role": "user", "content": ex["question"]})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": question})
    # temperature=0.7로 다양한 추론 경로 생성
    return chat(messages, temperature=0.7)


def extract_answer(text):
    """응답에서 숫자 답 추출 (마지막에 등장하는 숫자)"""
    numbers = re.findall(r'\d+\.?\d*', text.replace(',', ''))
    return numbers[-1] if numbers else None


def self_consistency(question, examples, n):
    answers = []
    responses = []

    for i in range(n):
        response = few_shot_cot(question, examples)
        answer = extract_answer(response)
        answers.append(answer)
        responses.append(response)
        print(f"\n[Sample {i+1}] 추출된 답: {answer}")
        print(response)

    # Majority voting
    counter = Counter(answers)
    majority_answer = counter.most_common(1)[0][0]

    print(f"\n{'='*60}")
    print(f"[투표 결과] {dict(counter)}")
    print(f"[최종 채택 답] {majority_answer}")
    print(f"[정답] {problem['answer']}")

    return majority_answer


if __name__ == "__main__":
    q = problem["question"]
    print(f"\n문제: {q}")
    print(f"정답: {problem['answer']}")
    print(f"\nSelf-Consistency 실행 중... (총 {N_SAMPLES}회 샘플링)")
    self_consistency(q, FEW_SHOT_EXAMPLES, N_SAMPLES)
