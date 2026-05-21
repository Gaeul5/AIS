"""
Sequential Flow 기반 멀티에이전트 워크플로우
구조:
  [planner] -> [drafter] -> [critic] -> [editor]
"""

from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage

from autogen_system.config import create_model_client
from autogen_system.agents import (
    create_planner,
    create_drafter,
    create_critic,
    create_editor
)


MAIN_QUESTION = """
다음 질문에 대해, 핵심 내용을 5문장 이내로 명확하게 설명해주세요:
‘왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?’
""".strip()


async def run_sequential_workflow(question: str | None = None) -> None:
    """
    planner -> drafter -> critic -> editor 순서로 진행되는
    Sequetial Workflow를 실행한다.
    """
    if question is None:
        question = MAIN_QUESTION

    # 1) 공용 모델 클라이언트 생성
    model_client = create_model_client()

    # 2) 에이전트 생성
    planner = create_planner(model_client)
    drafter = create_drafter(model_client)
    critic = create_critic(model_client)
    editor = create_editor(model_client)

    # 3) 그래프 정의 (Linear Chain)
    builder = DiGraphBuilder()

    # 노드 추가
    builder.add_node(planner)
    builder.add_node(drafter)
    builder.add_node(critic)
    builder.add_node(editor)

    # 엣지 연결 (순차적 흐름)
    builder.add_edge(planner, drafter)
    builder.add_edge(drafter, critic)
    builder.add_edge(critic, editor)

    graph = builder.build()

    # 4) 종료 조건
    # Editor가 최종 답변을 내놓으면 종료, 혹은 최대 메시지 수 도달 시 종료
    termination = TextMentionTermination(text="최종 답변:") | MaxMessageTermination(
        max_messages=10
    )

    # 5) GraphFlow 팀 구성
    flow = GraphFlow(
        participants=builder.get_participants(), # [planner, drafter, critic, editor]
        graph=graph,
        termination_condition=termination,
    )

    # 6) 시작 Task
    task = TextMessage(
        content=(
            "다음 질문에 대해 팀이 협력하여 최고의 답변을 만들어주세요.\n"
            "Planner가 먼저 계획을 세우고 시작하세요.\n\n"
            f"[사용자 질문]\n{question}\n"
        ),
        source="user",
    )

    # 7) 실행
    # 첫 턴은 graph 구조상 planner(진입점)가 받게 하려면, 
    # run_stream 호출 시에는 user 메시지만 던지고, 
    # 그래프 상에서 planner가 최초 노드이므로 자연스럽게 planner부터 시작.
    # 하지만 DiGraphBuilder로 명시적 진입점을 지정하지 않으면 
    # 모든 노드가 후보가 될 수 있으나, 여기서는 엣지 구조상 
    # planner -> ... 이므로 planner가 먼저 반응할 가능성이 높음.
    # 확실히 하기 위해 task에서 planner를 호출하거나 할 수도 있으나,
    # AutoGen GraphFlow는 topology 기반으로 다음 화자를 찾음.
    # (planner는 들어오는 엣지가 없으므로 시작점으로 적합)
    
    stream = flow.run_stream(task=task)

    await Console(stream)
    await model_client.close()
