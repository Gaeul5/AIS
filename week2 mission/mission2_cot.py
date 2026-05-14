"""
Mission 2: Chain-of-Thought (CoT) Prompting

Reference: Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
https://arxiv.org/abs/2201.11903

[실험 목표]
CoT("Let's think step by step")가 추론 과정에 어떤 영향을 주는지 확인합니다.

[과제]
1. 코드를 실행하고 세 방식의 출력을 비교해보기.
2. PROBLEM_IDX를 0~4로 바꿔가며 실험해보세요.
3. COT_TRIGGER를 아래 문장들로 바꿔보고 어떤 표현이 가장 효과적인지 확인해보기.
   - "Let's think step by step."      <- 원 논문 표현
   - "Think carefully."
   - "단계별로 생각해보자."
4. 실험 결과 확인해보기.
   - COT_TRIGGER 문구에 따라 출력 결과가 달라졌나요?
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api import chat, print_result
from utils.data import PROBLEMS, FEW_SHOT_EXAMPLES

# =====================
# 여기를 수정하세요
PROBLEM_IDX = 4  # 0~4
COT_TRIGGER = "Let's think step by step."
# =====================

problem = PROBLEMS[PROBLEM_IDX]


def zero_shot(question):
    messages = [{"role": "user", "content": question}]
    return chat(messages)


def zero_shot_cot(question, trigger):
    # 질문 뒤에 CoT 트리거 한 줄만 추가
    messages = [{"role": "user", "content": f"{question}\n\n{trigger}"}]
    return chat(messages)


def few_shot_cot(question, examples):
    # 풀이 과정이 포함된 예시를 제공 (논문의 Few-shot CoT 세팅)
    messages = []
    for ex in examples:
        assistant_msg = f"{ex['cot']} The answer is {ex['answer']}."
        messages.append({"role": "user", "content": ex["question"]})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": question})
    return chat(messages)


if __name__ == "__main__":
    q = problem["question"]
    print(f"\n정답: {problem['answer']}")

    print_result("Zero-shot", q, zero_shot(q))
    print_result(f"Zero-shot CoT ({COT_TRIGGER})", q, zero_shot_cot(q, COT_TRIGGER))
    print_result("Few-shot CoT", q, few_shot_cot(q, FEW_SHOT_EXAMPLES))
