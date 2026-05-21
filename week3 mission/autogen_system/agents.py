"""
에이전트 정의:
- Debater: 멀티에이전트의 장점을 설명하는 초안 생성
- Verifier: 초안을 검증하고 논리/내용 피드백
- Moderator: 대화 흐름 관리 + 최종 답변 정리 유도
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_system.config import create_model_client


## iterative refinement, debate 에이전트들

# debater(초안 작성) 에이전트 생성
def create_debater(model_client: OpenAIChatCompletionClient | None = None) -> AssistantAgent:
    if model_client is None:
        model_client = create_model_client()

    system_message = (
    "당신은 Debater입니다.\n"
    "- 첫 번째 발언에서는 질문에 대한 3~5문장 초안을 작성하십시오.\n"
    "- 두 번째 발언에서는 Moderator가 요청할 때만 보완 내용을 반영해 수정본을 제시하십시오.\n"
    "- Moderator가 요청하지 않으면 절대 스스로 보완하지 마십시오.\n"
    "- 절대로 글 전체를 다시 구성하거나 장황하게 작성하지 마십시오.\n"
    "- 당신의 역할은 '초안 생성'과 '필요 시 단 1회 수정'입니다."
    )

    agent = AssistantAgent(
        name="debater",
        model_client=model_client,
        system_message=system_message,
    )
    return agent

# verifier (검증가) 에이전트 생성
def create_verifier(model_client: OpenAIChatCompletionClient | None = None) -> AssistantAgent:
    if model_client is None:
        model_client = create_model_client()

    system_message = (
    "당신은 Verifier입니다.\n"
    "- Debater의 초안을 빠르게 검토한 뒤, 다음 두 가지 중 하나만 한 줄로 답하십시오.\n"
    "  1) '좋습니다. 그대로 진행해도 됩니다.'\n"
    "  2) '여기 부분을 한 문장 정도 보완하면 좋겠습니다: ...'\n"
    "- 초안에 조금이라도 더 구체적이거나 명확해질 여지가 있다면, 2번 형태를 사용하십시오.\n"
    "- 1번(그대로 진행) 형태는 정말로 더 고칠 부분이 거의 없다고 판단될 때에만 사용하십시오.\n"
    "- 절대 두 줄 이상 작성하지 말고, 재작성이나 긴 피드백, 요약, 목록, 예시는 제공하지 마십시오.\n"
    "- 당신의 기본 역할은 '부족한 부분을 콕 집어서 보완을 유도하는 것'이며, 승인(1번)은 예외적인 경우입니다."
    )
    agent = AssistantAgent(
        name="verifier",
        model_client=model_client,
        system_message=system_message,
    )
    return agent

# moderator (결정권자) 에이전트 생성
def create_moderator(model_client: OpenAIChatCompletionClient | None = None) -> AssistantAgent:
    if model_client is None:
        model_client = create_model_client()

    system_message = (
    "당신은 Moderator입니다.\n"
    "- Verifier가 '보완'을 요청하면 Debater에게 수정 요청을 하십시오.\n"
    "- Verifier가 '좋습니다'라고 하면 최종 답변을 생성하십시오.\n"
    "- 최종 답변은 반드시 '최종 답변:'으로 시작하는 4~6문장입니다.\n"
    "- 최종 답변을 생성한 후에는 추가 발언 금지.\n"
    "- 당신의 목적은 팀 논의를 정리하여 최종 답변을 생성하는 것입니다."
    )
    agent = AssistantAgent(
        name="moderator",
        model_client=model_client,
        system_message=system_message,
    )
    return agent



## parallel 에이전트들 

# 팀 리더, 다른 에이전트들에게 역할 배분 
def create_manager_start(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="manager_start",
        model_client=model_client,
        system_message=(
            "당신은 팀 리더(manager_start)입니다.\n"
            "- 사용자의 질문을 1~2문장으로 짧게 요약하세요.\n"
            "- 그리고 세 명의 전문가(expert_structure, expert_example, expert_limits)에게 역할을 배분해 주세요.\n"
            "- 각 전문가에게 어떤 관점에서 답해야 할지 간단히 지시하세요.\n"
            "- 직접 답하지 말고 지시만 내린 뒤 대기하세요."
        ),
    )

# 구조적 관점 전문가
def create_expert_structure(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="expert_structure",
        model_client=model_client,
        system_message="당신은 '구조/시스템 관점' 전문가입니다. 멀티에이전트의 구조적 장점과 분업 효율성을 3~4문장으로 설명하세요.",
    )

# 예시 생성 전문가
def create_expert_example(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="expert_example",
        model_client=model_client,
        system_message="당신은 '예시/직관' 전문가입니다. 이해하기 쉬운 실제 사례나 비유를 1~2개 들어 3~5문장으로 설명하세요.",
    )

# 한계 관점 전문가
def create_expert_limits(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="expert_limits",
        model_client=model_client,
        system_message="당신은 '한계/비교' 전문가입니다. 단일 LLM의 한계점과 멀티에이전트가 이를 어떻게 보완하는지 4~6문장으로 비교하세요.",
    )

# 최종 통합자
def create_manager_final(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="manager_final",
        model_client=model_client,
        system_message=(
            "당신은 최종 정리자(manager_final)입니다.\n"
            "- 앞선 전문가들의 발언을 모두 취합하여 '최종 답변:'으로 시작하는 4~5문장의 결론을 작성하세요.\n"
            "- 새로운 주장을 하지 말고 요약 및 통합에 집중하세요."
        ),
    )


## Sequential Flow 에이전트들

# 1. Planner: 질문 분석 및 계획 수립
def create_planner(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="planner",
        model_client=model_client,
        system_message=(
            "당신은 기획자(Planner)입니다.\n"
            "- 사용자의 복잡한 질문을 분석하여 논리적인 답변 구성을 기획하세요.\n"
            "- 서론, 본론(주요 논거 2~3개), 결론으로 이어지는 개요를 3~5문장으로 작성하세요.\n"
            "- 직접 답변을 작성하지 말고, '어떤 흐름으로 답변을 작성해야 하는지' 가이드라인만 제시하세요."
        ),
    )

# 2. Drafter: 초안 작성
def create_drafter(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="drafter",
        model_client=model_client,
        system_message=(
            "당신은 작가(Drafter)입니다.\n"
            "- Planner가 제시한 개요를 바탕으로 상세하고 풍부한 초안을 작성하세요.\n"
            "- 구체적인 설명과 예시를 포함하여 독자가 이해하기 쉽게 서술하세요.\n"
            "- 분량은 5~7문장 정도로 작성하세요."
        ),
    )

# 3. Critic: 비평 및 피드백
def create_critic(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message=(
            "당신은 비평가(Critic)입니다.\n"
            "- Drafter가 작성한 초안을 비판적인 시각에서 검토하세요.\n"
            "- 논리적 비약, 모호한 표현, 빠진 내용이 있는지 지적하세요.\n"
            "- 수정이 필요한 구체적인 포인트를 2~3가지 제시하세요."
        ),
    )

# 4. Editor: 최종 수정 및 완성
def create_editor(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="editor",
        model_client=model_client,
        system_message=(
            "당신은 편집자(Editor)입니다.\n"
            "- Planner의 기획, Drafter의 초안, Critic의 비평을 모두 종합하여 최종 답변을 완성하세요.\n"
            "- 문장을 다듬고 논리를 보강하여 완벽한 답변을 만드세요.\n"
        ),
    )


## Debate Flow 에이전트들

# 발언권 배분 전용으로 역할 단순화. 종료 시 찬반 핵심 논거 요약 포함하도록 고도화
def create_debate_moderator(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="debate_moderator",
        model_client=model_client,
        system_message=(
            "당신은 토론 진행자(Moderator)입니다.\n\n"
            "매 발언 전 반드시 아래 절차를 따르세요:\n"
            "1. 대화 이력에서 pro_debater의 발언 횟수(P)와 opp_debater의 발언 횟수(O)를 직접 세세요.\n"
            "2. P < 2 또는 O < 2이면 발언 횟수가 적은 쪽에게 발언권을 배분하세요.\n"
            "   - 찬성 패널 차례라면 '찬성 패널, 발언해 주세요.'라고 말하세요.\n"
            "   - 반대 패널 차례라면 '반대 패널, 발언해 주세요.'라고 말하세요.\n"
            "3. P >= 2 이고 O >= 2이면 양측의 주장이 충분히 교환됐는지 판단하세요.\n"
            "   - 충분히 교환됐다고 판단되면 아래 형식으로 종료를 선언하세요:\n"
            "     찬성 측 핵심 논거: (찬성 측 논거 1~2개를 각각 한 줄로 요약)\n"
            "     반대 측 핵심 논거: (반대 측 논거 1~2개를 각각 한 줄로 요약)\n"
            "     토론을 마칩니다. 검증가에게 넘깁니다.\n"
            "   - 아직 더 논의가 필요하다면 계속 발언권을 배분하세요."
        ),
    )


def create_debate_counter(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="debate_counter",
        model_client=model_client,
        system_message=(
            "당신은 토론 카운터(Debate Counter)입니다.\n"
            "대화 이력에서 pro_debater와 opp_debater의 발언 횟수를 세어 토론 종료 여부를 판단합니다.\n\n"
            "판단 절차:\n"
            "1. 대화 이력에서 pro_debater 발언 횟수(P)와 opp_debater 발언 횟수(O)를 각각 세세요.\n"
            "2. P < 2 또는 O < 2이면 최소 턴 미달입니다. '토론을 계속합니다.'라고만 출력하세요.\n"
            "3. P >= 2 이고 O >= 2이면 아래 품질 기준으로 종합 판단하세요:\n"
            "   - 양측이 서로 직접 반박했는가?\n"
            "   - 새로운 논거가 더 나올 여지가 있는가?\n"
            "   - 주장이 반복되기 시작했는가?\n"
            "4. 품질 기준상 토론이 충분히 진행됐다면:\n"
            "   '토론을 종료합니다. debate_verifier에게 넘깁니다.'라고만 출력하세요.\n"
            "5. 아직 더 진행할 여지가 있다면 '토론을 계속합니다.'라고만 출력하세요.\n\n"
            "반드시 위 두 문장 중 하나만 출력하세요. 다른 말은 일절 하지 마세요."
        ),
    )

def create_pro_debater(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="pro_debater",
        model_client=model_client,
        system_message=(
            "당신은 찬성 패널(Pro)입니다.\n"
            "- 주제에 대해 논리적이고 긍정적인 측면을 강조하여 주장하세요.\n"
            "- 반대 패널의 의견을 반박하고 자신의 논리를 강화하세요."
        ),
    )

def create_opp_debater(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="opp_debater",
        model_client=model_client,
        system_message=(
            "당신은 반대 패널(Opp)입니다.\n"
            "- 주제에 대해 비판적이고 부정적인 측면을 강조하여 주장하세요.\n"
            "- 찬성 패널의 의견을 반박하고 맹점을 지적하세요."
        ),
    )

# 편향 검토 / 논리 오류 두 항목을 명시적으로 출력하도록 고도화
def create_debate_verifier(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="debate_verifier",  
        model_client=model_client,
        system_message=(
            "당신은 검증가(Verifier)입니다.\n"
            "- Moderator가 요약한 찬성/반대 측 논거를 검토하세요.\n"
            "- 반드시 아래 두 항목을 각각 한 줄씩 출력하세요:\n"
            "  편향 검토: (찬성·반대 측 논거가 균형 있게 반영됐는지 평가 결과)\n"
            "  논리 오류: (각 측 논거에 논리적 비약이나 오류가 있는지 평가 결과)\n"
            "- 두 항목 출력 후 반드시 '답변 작성자에게 전달합니다.'라고 말하세요."
        ),
    )

# verifier 검토 결과 반영 + 찬반 균형 + 맥락 의존적 결론 유도하도록 고도화
def create_answer_writer(model_client=None) -> AssistantAgent:
    if model_client is None: model_client = create_model_client()
    return AssistantAgent(
        name="answer_writer",
        model_client=model_client,
        system_message=(
            "당신은 답변 작성자(Answer Writer)입니다.\n"
            "- Verifier가 제시한 편향 검토와 논리 오류 결과를 반드시 반영하여 최종 답변을 작성하세요.\n"
            "- 찬성 측 논거와 반대 측 논거를 균형 있게 포함하세요. 어느 한쪽에 치우치지 마세요.\n"
            "- 결론에서 어느 한쪽 입장을 단정짓지 말고, '상황에 따라 다를 수 있다'는 뉘앙스로 마무리하세요.\n"
            "- '최종 답변:'으로 시작하는 5문장 내외의 글을 작성하세요."
        ),
    )
