# GSM8K 벤치마크 샘플
# Cobbe et al. (2021) "Training Verifiers to Solve Math Word Problems"
# https://arxiv.org/abs/2110.14168

PROBLEMS = [
    {
        "id": 0,
        "question": (
            "What is the angle between the hour and minute hands of a clock "
            "at 3:40?"
        ),
        "answer": "130",
    },
    {
        "id": 1,
        "question": (
            "How many two-digit numbers have digits that sum to 10?"
        ),
        "answer": "9",
    },
    {
        "id": 2,
        "question": (
            "In how many ways can 5 people be seated around a circular table? "
            "(Rotations are considered the same.)"
        ),
        "answer": "24",
    },
    {
        "id": 3,
        "question": (
            "The sum of all integers from 1 to n equals 210. "
            "Find n."
        ),
        "answer": "20",
    },
    {
        "id": 4,
        "question": (
            "Two dice are rolled. Given that the sum is 8, "
            "how many of the possible outcomes have both dice showing even numbers?"
        ),
        "answer": "3",
    },
]

# Few-shot CoT에서 사용할 예시 (GSM8K 학습셋 기반)
FEW_SHOT_EXAMPLES = [
    {
        "question": "There are 3 cars in the parking lot. 2 more cars arrive. How many cars are in the parking lot?",
        "cot": "There are 3 cars already. 2 more arrive. Now there are 3 + 2 = 5 cars.",
        "answer": "5",
    },
    {
        "question": "Olivia has $23. She bought five bagels for $3 each. How much money does she have left?",
        "cot": "5 bagels for $3 each costs 5 × 3 = $15. 23 - 15 = $8 left.",
        "answer": "8",
    },
    {
        "question": "A train travels 120 miles in 2 hours. What is its average speed in miles per hour?",
        "cot": "Speed = Distance ÷ Time. 120 miles ÷ 2 hours = 60 mph.",
        "answer": "60",
    },
    {
        "question": "A rectangle has a length of 8 cm and a width of 5 cm. What is its area?",
        "cot": "Area = length × width. 8 × 5 = 40 cm².",
        "answer": "40",
    },
    {
        "question": "Mike had 50 dollars. He spent 30% on lunch. How much does he have left?",
        "cot": "30% of 50 = 50 × 0.3 = 15 dollars spent. 50 - 15 = 35 dollars left.",
        "answer": "35",
    },
]
