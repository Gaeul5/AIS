"""
Mission 1: Zero-shot vs Few-shot Prompting

Reference: Brown et al. (2020) "Language Models are Few-Shot Learners"
https://arxiv.org/abs/2005.14165

[실험 목표]
동일한 GSM8K 문제에 예시 유무가 어떤 영향을 주는지 비교합니다.

[과제]
1. 코드를 실행하고 두 방식의 출력을 비교하세요.
2. PROBLEM_IDX를 0~4로 바꿔가며 여러 문제를 실험해보세요.
3. FEW_SHOT_EXAMPLES의 예시 수를 1개로 줄이거나 늘렸을 때 차이가 있는지 확인하세요.
4. 실험 결과 확인해보기
   - 어떤 문제에서 두 방식의 차이가 가장 컸나요?
   - 예시 수가 늘어날수록 항상 성능이 좋아졌나요?
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api import chat, print_result
from utils.data import PROBLEMS, FEW_SHOT_EXAMPLES

# =====================
# 여기를 수정하세요
PROBLEM_IDX = 2  # 1~5

# 사용할 예시 수 (1 ~ len(FEW_SHOT_EXAMPLES))
# 예: 1이면 예시 1개, 3이면 예시 3개
N_EXAMPLES = 3
# =====================

problem = PROBLEMS[PROBLEM_IDX]


def zero_shot(question):
    messages = [{"role": "user", "content": question}]
    return chat(messages)


def few_shot(question, examples):
    # 예시를 대화 형식으로 구성
    messages = []
    for ex in examples:
        user_msg = ex["question"]
        assistant_msg = f"{ex['cot']} The answer is {ex['answer']}."
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": question})
    return chat(messages)


if __name__ == "__main__":
    q = problem["question"]
    examples = FEW_SHOT_EXAMPLES[:N_EXAMPLES]  # N_EXAMPLES개만 사용
    print(f"\n정답: {problem['answer']}")
    print(f"사용 예시 수: {N_EXAMPLES}개")

    print_result("Zero-shot", q, zero_shot(q))
    print_result(f"Few-shot ({N_EXAMPLES}개 예시)", q, few_shot(q, examples))
