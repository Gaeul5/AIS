"""
Debate Flow 멀티에이전트 워크플로우
구조:
  Query -> [Moderator] <-> [Pro/Opp] (Dynamic Loop)
              |
              v
          [Verifier] -> [Answer Writer]
"""

from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console

from autogen_system.config import create_model_client
from autogen_system.agents import (
    create_debate_moderator,
    create_pro_debater,
    create_opp_debater,
    create_debate_verifier,
    create_answer_writer
)


MAIN_QUESTION = """
다음 질문에 대해, 핵심 내용을 5문장 이내로 명확하게 설명해주세요:
‘왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?’
""".strip()

# 토론 진행을 위한 라우팅 프롬프트
# moderator가 턴을 직접 카운팅하고 종료 판단하도록 구조 변경.
# debate_counter 에이전트 제거하고 moderator 프롬프트에 로직 통합.
# Moderator -> Pro/Opp (Loop) -> Moderator -> Verifier -> Answer Writer -> Terminate
DEBATE_PROMPT = (
    "당신은 토론 흐름을 관리하는 조정자입니다.\n\n"
    "에이전트 역할:\n"
    "{roles}\n\n"
    "참여 가능 에이전트:\n"
    "{participants}\n\n"
    "대화 이력:\n"
    "{history}\n\n"
    "규칙:\n"
    "1. 시작 시에는 debate_moderator를 선택하십시오.\n"
    "2. debate_moderator가 발언한 직후에는 대화 이력에서 pro_debater와 opp_debater의 발언 횟수를 세어, "
    "아직 덜 발언한 쪽을 선택하십시오. 발언 횟수가 같다면 pro_debater를 선택하십시오.\n"
    "3. pro_debater 또는 opp_debater가 발언한 직후에는 debate_moderator를 선택하십시오.\n"
    "4. debate_moderator가 '검증가'에게 넘긴다고 하면 debate_verifier를 선택하십시오.\n"
    "5. debate_verifier가 '답변 작성자'에게 전달한다고 하면 answer_writer를 선택하십시오.\n"
    "6. answer_writer가 '최종 답변:'을 완료하면 더 이상 선택하지 마십시오 (종료).\n\n"
    "주의사항:\n"
    "- debate_verifier가 발언한 직후에는 반드시 answer_writer를 선택하라.\n"
    "- answer_writer가 한 번이라도 발언했으면 그 이후로는 어떤 에이전트도 선택하지 마라.\n"
    "- debate_moderator가 '검증가에게 넘깁니다'를 언급한 이후에는 "
    "debate_moderator, pro_debater, opp_debater를 절대 선택하지 마라.\n\n"
    "다음에 발언할 에이전트 이름을 정확히 하나만 반환하세요."
)


async def run_debate_workflow(question: str | None = None) -> None:
    if question is None:
        question = MAIN_QUESTION

    model_client = create_model_client()

    # 에이전트 생성
    moderator = create_debate_moderator(model_client)
    pro = create_pro_debater(model_client)
    opp = create_opp_debater(model_client)
    verifier = create_debate_verifier(model_client)
    answer_writer = create_answer_writer(model_client) # agent name 'answer_writer'

    # 종료 조건
    termination = TextMentionTermination(text="최종 답변:") | MaxMessageTermination(max_messages=25)

    # SelectorGroupChat으로 구성
    team = SelectorGroupChat(
        participants=[moderator, pro, opp, verifier, answer_writer],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=DEBATE_PROMPT,
        allow_repeated_speaker=False
    )

    task = TextMessage(
        content=(
            "다음 주제에 대해 토론을 시작합니다. Moderator가 먼저 진행해 주세요.\n\n"
            f"[토론 주제]\n{question}\n"
        ),
        source="user",
    )

    stream = team.run_stream(task=task)
    await Console(stream)
    await model_client.close()
