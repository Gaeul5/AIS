========================================
LLM Prompting 과제 - GSM8K 실험
========================================

[프로젝트 구조]

code/
├── .env                            # API 키 설정
├── requirements.txt
├── utils/
│   ├── api.py                      # API 호출 공통 함수
│   └── data.py                     # 문제 및 Few-shot 예시
└── missions/
    ├── mission1_zero_few_shot.py   # Zero-shot vs Few-shot
    ├── mission2_cot.py             # Chain-of-Thought
    └── mission3_self_consistency.py # Self-Consistency


[시작하기]

1. 패키지 설치
   pip install -r requirements.txt

2. API 키 설정
   .env 파일에 아래와 같이 입력
   OPENAI_API_KEY=발급받은_키_입력
   발급: https://platform.openai.com/api-keys

3. 실행
   python missions/mission1_zero_few_shot.py
   python missions/mission2_cot.py
   python missions/mission3_self_consistency.py


[실험 변수 가이드]

수정 위치: 각 미션 파일 상단 "여기를 수정하세요" 블록
           + utils/data.py의 FEW_SHOT_EXAMPLES

  PROBLEM_IDX (0~4)
  - 실험할 문제 선택
  - 단순 문제(1,2번)보다 다단계 문제(3,4,5번)에서 기법 차이가 뚜렷함

  N_EXAMPLES (Mission 1)
    - 사용할 Few-shot 예시 수 (1 ~ 5)
    - 숫자가 클수록 예시 많이 제공, 적을수록 적게 제공

  COT_TRIGGER (Mission 2)
  - "Let's think step by step."  <- 원 논문 표현
  - "Think carefully."
  - "단계별로 생각해보자."

  N_SAMPLES (Mission 3)
  - Self-Consistency 샘플링 횟수
  - 홀수 권장 (동점 방지), 많을수록 API 비용 증가

  FEW_SHOT_EXAMPLES (utils/data.py)
  - 예시 문제/풀이/답을 자유롭게 교체 가능
  - 예시 난이도, 풀이 스타일, 문제 유형을 바꿔가며 실험

[참고 논문]

- Mission 1: Brown et al. (2020) "Language Models are Few-Shot Learners" https://arxiv.org/abs/2005.14165
- Mission 2: Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning in LLMs" https://arxiv.org/abs/2201.11903
- Mission 3: Wang et al. (2022) "Self-Consistency Improves Chain of Thought Reasoning" https://arxiv.org/abs/2203.11171
- 데이터: Cobbe et al. (2021) "Training Verifiers to Solve Math Word Problems" https://arxiv.org/abs/2110.14168

[제출 안내]

제출 경로:
  Mentoring Drive > 2. Large Language Models > assignment > 본인이름 폴더 생성 후 업로드

제출 파일:
  1. 폴더 전체 (.env 제외)
  2. 미션별 터미널 출력 스크린샷 각 1장 이상 (총 3장, 가장 마음에 드는 결과 올려주세요)

제출 기한: 2026년 5월 17일 (일) 자정까지

[주의사항]

- Mission 3은 N_SAMPLES만큼 API를 호출하므로 비용 주의
- .env 파일은 절대 외부에 공유하지 마세요.
========================================
