# AutoGen 멀티에이전트 패턴 실습

AutoGen(`autogen-agentchat 0.7.5`)을 이용해 **4가지 멀티에이전트 협업 패턴**을 구현한 실습 코드입니다.  
모든 예제는 동일한 질문("왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?")을 각기 다른 방식으로 풀어냅니다.

---

## 프로젝트 구조

```
.
├── sequential.py              # Sequential 패턴 실행 진입점
├── parallel.py                # Parallel 패턴 실행 진입점
├── routing.py                 # Routing 패턴 실행 진입점
├── debate.py                  # Debate 패턴 실행 진입점
├── iterative_refinement.py    # Iterative Refinement 패턴 실행 진입점
├── requirements.txt
├── .env                       # OPENAI_API_KEY 설정 (직접 작성 필요)
└── autogen_system/
    ├── config.py              # 모델 클라이언트 생성
    ├── agents.py              # 모든 에이전트 정의 (프롬프트 수정은 여기서)
    ├── workflow_sequential.py
    ├── workflow_parallel.py
    ├── workflow_routing.py
    ├── workflow_debate.py
    └── workflow_iterative_refinement.py
```

---

## 시작하기

**1. 패키지 설치**
```bash
pip install -r requirements.txt
```

**2. API 키 설정**  
`.env` 파일에 OpenAI API 키를 입력합니다.
```
OPENAI_API_KEY=sk-...
```

**3. 실행**
```bash
python sequential.py
python parallel.py
python routing.py
python debate.py
python iterative_refinement.py
```

---

## 패턴별 설명

### 0. 입력 질문(Query) 수정
autogen_system/에 위치한 각 코드 파일 내 "MAIN_QUESTION"이 사용자 입력 질문 부분입니다!
사용자 입력 질문을 수정하려면 이쪽을 수정하면 됩니다.

### 1. Sequential (순차 실행)
**실행:** `python sequential.py`  
**워크플로우 정의:** `autogen_system/workflow_sequential.py`

```
[Planner] → [Drafter] → [Critic] → [Editor]
```

`DiGraphBuilder`로 선형 DAG를 구성하고 `GraphFlow`로 실행합니다.  
각 에이전트가 이전 에이전트의 출력을 받아 순서대로 처리하는 가장 기본적인 패턴입니다.

| 에이전트 | 역할 |
|---|---|
| Planner | 질문 분석 후 서론-본론-결론 개요 작성 (직접 답변 X) |
| Drafter | Planner의 개요를 바탕으로 5~7문장 초안 작성 |
| Critic | 초안의 논리적 비약·모호한 표현 등 2~3가지 지적 |
| Editor | 기획·초안·비평을 종합해 최종 답변 완성 |

> **프롬프트 수정:** `autogen_system/agents.py` → `create_planner`, `create_drafter`, `create_critic`, `create_editor`

---

### 2. Parallel (병렬 실행)
**실행:** `python parallel.py`  
**워크플로우 정의:** `autogen_system/workflow_parallel.py`

```
              [manager_start]
             /       |        \
  [expert_structure] [expert_example] [expert_limits]
             \       |        /
              [manager_final]
```

`DiGraphBuilder`로 fan-out → fan-in 구조의 DAG를 구성합니다.  
`manager_start`가 역할을 배분하면 세 전문가가 각자의 관점에서 병렬로 답변하고, `manager_final`이 통합합니다.

| 에이전트 | 역할 |
|---|---|
| manager_start | 질문 요약 후 세 전문가에게 관점 배분 (직접 답변 X) |
| expert_structure | 구조/시스템 관점: 분업 효율성 중심 3~4문장 |
| expert_example | 예시/직관 관점: 실사례·비유 중심 3~5문장 |
| expert_limits | 한계/비교 관점: 단일 LLM의 한계와 보완점 4~6문장 |
| manager_final | 세 전문가 발언 취합 후 `최종 답변:` 으로 시작하는 결론 작성 |

> **프롬프트 수정:** `autogen_system/agents.py` → `create_manager_start`, `create_expert_structure`, `create_expert_example`, `create_expert_limits`, `create_manager_final`

---

### 3. Routing (동적 라우팅)
**실행:** `python routing.py`  
**워크플로우 정의:** `autogen_system/workflow_routing.py`

```
[Debater] ↔ [Verifier] ↔ [Moderator]
  (다음 발언자를 LLM이 동적으로 선택)
```

`SelectorGroupChat`을 사용합니다. 고정된 순서 없이, `ROUTING_PROMPT`를 받은 LLM이 대화 히스토리를 보고 다음 발언자를 매 턴 선택합니다.  
종료 조건은 `최종 답변:` 언급 또는 12개 메시지 초과입니다.

| 에이전트 | 역할 |
|---|---|
| Debater | 질문에 대한 3~5문장 초안 생성, Moderator 요청 시 1회 수정 |
| Verifier | 초안 검토 후 한 줄 피드백 (보완 요청 또는 승인) |
| Moderator | Verifier 판단에 따라 수정 요청 또는 `최종 답변:` 작성 |

> **프롬프트 수정:**
> - 에이전트 역할: `autogen_system/agents.py` → `create_debater`, `create_verifier`, `create_moderator`
> - 라우팅 로직: `autogen_system/workflow_routing.py` → `ROUTING_PROMPT`

---

### 4. Debate (토론)
**실행:** `python debate.py`  
**워크플로우 정의:** `autogen_system/workflow_debate.py`

```
[debate_moderator] ↔ [pro_debater] / [opp_debater]  (동적 루프)
        ↓
    [verifier]
        ↓
  [answer_writer]
```

`SelectorGroupChat` + `DEBATE_PROMPT`로 토론 흐름을 제어합니다.  
Moderator가 찬반 패널에게 번갈아 발언권을 주고, 6턴 이상 진행되면 Verifier → Answer Writer 순으로 이관합니다.  
종료 조건은 `최종 답변:` 언급 또는 25개 메시지 초과입니다.

| 에이전트 | 역할 |
|---|---|
| debate_moderator | 발언 횟수를 직접 카운팅해 발언권 배분. 각 2회 이상 발언 후 찬반 핵심 논거 요약과 함께 종료 선언 |
| pro_debater | 주제의 긍정적 측면 주장, 반대 패널 반박 |
| opp_debater | 주제의 비판적 측면 주장, 찬성 패널 반박 |
| debate_verifier | `편향 검토:` / `논리 오류:` 두 항목을 명시적으로 출력한 뒤 Answer Writer 이관 |
| answer_writer | verifier 검토 결과 반영, 찬반 균형 유지, 맥락 의존적 결론으로 `최종 답변:` 작성 |

> **프롬프트 수정:**
> - 에이전트 역할: `autogen_system/agents.py` → `create_debate_moderator`, `create_pro_debater`, `create_opp_debater`, `create_debate_verifier`, `create_answer_writer`
> - 라우팅 로직: `autogen_system/workflow_debate.py` → `DEBATE_PROMPT`

### 변경 사항

**변경 전 구조**
```
[debate_moderator] → [pro_debater / opp_debater] → [debate_counter] → (계속/종료 판단)
                                                                              ↓
                                                                      [debate_verifier] → [answer_writer]
```

**변경 후 구조**
```
[debate_moderator] ↔ [pro_debater / opp_debater]  (moderator가 직접 턴 카운팅 + 종료 판단)
        ↓
  [debate_verifier]
        ↓
  [answer_writer]
```

**변경 이유**

| # | 항목 | 내용 |
|---|---|---|
| 1 | 턴 카운팅 모호성 | 별도 `debate_counter` 에이전트가 매 턴 종료 여부를 판단하는 구조에서 라우팅 선택 오류가 발생할 수 있었음. moderator 프롬프트에 카운팅 로직을 직접 통합해 책임을 단일화함 |
| 2 | verifier 역할 형식화 | 기존 verifier는 자유 형식으로 검토 의견을 출력해 answer_writer가 결과를 정확히 반영하기 어려웠음. `편향 검토:` / `논리 오류:` 두 항목을 명시적으로 출력하도록 구조화함 |
| 3 | answer_writer 균형 개선 | verifier 검토 결과를 의무적으로 반영하고, 찬반 논거를 균형 있게 포함하며, 어느 한쪽으로 단정 짓지 않는 맥락 의존적 결론을 유도하도록 프롬프트를 강화함 |

---

### 5. Iterative Refinement (반복 정제)
**실행:** `python iterative_refinement.py`  
**워크플로우 정의:** `autogen_system/workflow_iterative_refinement.py`

```
[Debater] → [Verifier] → [Moderator] → [Debater] → ...  (Round Robin)
```

`RoundRobinGroupChat`으로 세 에이전트가 고정 순서로 순환합니다.  
Routing 패턴과 동일한 에이전트(Debater/Verifier/Moderator)를 사용하지만, 발언 순서가 고정되어 있다는 점이 다릅니다.  
종료 조건은 `최종 답변:` 언급 또는 10개 메시지 초과입니다.

| 에이전트 | 역할 |
|---|---|
| Debater | 초안 작성 → Moderator 요청 시 1회 수정 |
| Verifier | 한 줄 피드백 (보완 요청 또는 승인) |
| Moderator | 흐름 조율 및 최종 답변 작성 |

> **프롬프트 수정:** `autogen_system/agents.py` → `create_debater`, `create_verifier`, `create_moderator`  
> ※ Routing 패턴과 동일한 함수를 공유합니다.

---

## 에이전트 프롬프트 수정 가이드

**모든 에이전트의 시스템 프롬프트는 `autogen_system/agents.py` 한 곳에 집중**되어 있습니다.  
각 `create_*` 함수 내부의 `system_message` 문자열을 수정하면 됩니다.

```python
# 예시: Debater의 초안 문장 수를 바꾸고 싶다면
# autogen_system/agents.py → create_debater()

system_message = (
    "당신은 Debater입니다.\n"
    "- 첫 번째 발언에서는 질문에 대한 3~5문장 초안을 작성하십시오.\n"  # ← 여기 수정
    ...
)
```

라우팅/토론 흐름 자체를 바꾸고 싶다면 각 `workflow_*.py`의 `ROUTING_PROMPT` 또는 `DEBATE_PROMPT`를 수정합니다.

---

## 패턴 비교 요약

| 패턴 | AutoGen 클래스 | 발언 순서 | 특징 |
|---|---|---|---|
| Sequential | `GraphFlow` (선형 DAG) | 고정 | 단방향 파이프라인 |
| Parallel | `GraphFlow` (fan-out/in DAG) | 고정 | 병렬 처리 후 통합 |
| Routing | `SelectorGroupChat` | LLM이 동적 선택 | 유연한 흐름 제어 |
| Debate | `SelectorGroupChat` | LLM이 동적 선택 | 찬반 구도 + 순차 이관 |
| Iterative Refinement | `RoundRobinGroupChat` | 고정 순환 | 반복 정제 |
