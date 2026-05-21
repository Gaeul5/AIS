"""
SelectorGroupChat 기반 멀티에이전트 워크플로우.

- Debater, Verifier, Moderator 세 에이전트를 SelectorGroupChat 팀으로 구성.
- 다음 발언자는 LLM이 대화 히스토리와 에이전트 설명을 보고 동적으로 선택.
- 종료 조건:
    - Moderator가 '최종 답변:'을 출력하거나
    - 전체 메시지 수가 일정 개수를 넘으면 종료.
"""

from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console 

from autogen_system.agents import create_debater, create_verifier, create_moderator
from autogen_system.config import create_model_client


MAIN_QUESTION = """
다음 질문에 대해, 핵심 내용을 5문장 이내로 명확하게 설명해주세요:
‘왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?’
"""


# SelectorGroupChat에서 사용할 라우팅 프롬프트
ROUTING_PROMPT = (
    "당신은 멀티에이전트 팀에서 '다음 발언자'를 선택하는 조정자입니다.\n\n"
    "아래는 각 에이전트의 역할입니다:\n"
    "{roles}\n\n"
    "현재 참여 가능한 에이전트 목록:\n"
    "{participants}\n\n"
    "지금까지의 대화 히스토리:\n"
    "{history}\n\n"
    "규칙:\n"
    "1. 사용자의 질문에 대한 초안이 아직 없다면, Debater를 우선 선택하여 초안을 작성하게 하십시오.\n"
    "2. Debater가 어느 정도 답변을 제시한 뒤에는, Verifier가 한 번 정도 피드백을 줄 수 있도록 선택하는 것이 좋습니다.\n"
    "3. Debater와 Verifier가 충분히 발언하여 내용이 정리되었다고 판단되면, Moderator를 선택하여 최종 답변을 작성하도록 하십시오.\n"
    "4. 이미 '최종 답변:'이 포함된 발언이 있다면, 더 이상 새로운 에이전트를 선택하지 않는 것이 바람직합니다.\n"
    "5. 같은 에이전트를 불필요하게 여러 번 연속 선택하지 마십시오.\n\n"
    "위 히스토리와 규칙을 참고하여, 다음에 발언해야 할 에이전트의 이름을 {participants} 중에서 정확히 하나만 선택해 반환하십시오.\n"
    "에이전트 이름만 단독으로 출력하고, 다른 문장은 쓰지 마십시오."
)


async def run_routing_workflow(question: str | None = None) -> None:
    """
    SelectorGroupChat을 이용해 멀티에이전트 팀을 구성하고,
    하나의 질문에 대한 동적 협업 대화를 수행한다.
    """
    if question is None:
        question = MAIN_QUESTION.strip()

    # 하나의 model_client를 세 에이전트가 공유
    model_client = create_model_client()

    debater = create_debater(model_client)
    verifier = create_verifier(model_client)
    moderator = create_moderator(model_client)

    # 종료 조건:
    # - Moderator가 '최종 답변:'을 출력하거나
    # - 전체 메시지 수가 12개를 넘으면 종료
    termination = TextMentionTermination(text="최종 답변:") | MaxMessageTermination(
        max_messages=12
    )

    # SelectorGroupChat 팀 구성
    team = SelectorGroupChat(
        participants=[debater, verifier, moderator],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=ROUTING_PROMPT, # selector는 여기서만 제어해주면 됨 (따로 생성할 필요 X)
        allow_repeated_speaker=False,  # 같은 에이전트가 연속 선택되는 것을 막음
    )

    # 사용자 질문 메시지
    task = TextMessage(
        content=(
            "다음 질문에 대해 팀이 협력하여 답변을 만들어주세요.\n\n"
            f"{question}"
        ),
        source="user",
    )

    # 스트리밍 실행
    stream = team.run_stream(task=task)

    await Console(stream)
    await model_client.close()