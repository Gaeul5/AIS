"""
AutoGen 반복 정제(Iterative Refinement) 워크플로우:
Debater, Verifier, Moderator를 RoundRobinGroupChat으로 묶어서
질문 하나에 대해 협력적으로 답변을 만들어내는 흐름을 정의한다.
"""

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage

from autogen_system.agents import create_debater, create_verifier, create_moderator
from autogen_system.config import create_model_client


MAIN_QUESTION = """
다음 질문에 대해, 핵심 내용을 5문장 이내로 명확하게 설명해주세요:
‘왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?’
"""


async def run_iterative_refinement_workflow(question: str | None = None) -> None:
    """
    Iterative Refinement 방식 기반 멀티에이전트 팀을 구성하고,
    하나의 질문에 대한 협업 대화를 수행
    """
    if question is None:
        question = MAIN_QUESTION.strip()

    # 하나의 model_client를 세 에이전트가 공유
    model_client = create_model_client()

    debater = create_debater(model_client)
    verifier = create_verifier(model_client)
    moderator = create_moderator(model_client)

    # 대화 종료 조건: '최종 답변:'이 언급되거나, 9개 이상의 메시지가 오가면 종료
    termination = TextMentionTermination(text="최종 답변:") | MaxMessageTermination(max_messages=10)

    # 팀 구성: Debater -> Verifier -> Moderator 순환
    # RoundRobinGroupChat 클래스 자체는 그대로 사용하되, 개념적으로 Iterative Refinement를 수행
    team = RoundRobinGroupChat(
        participants=[debater, verifier, moderator], # 멤버 정의
        termination_condition=termination, # 종료 조건
    )

    # TextMessage를 사용해 질문 전달
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