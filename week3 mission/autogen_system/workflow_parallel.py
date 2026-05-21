r"""
GraphFlow 기반 멀티에이전트 워크플로우 (Parallel Execution)
구조:

  [manager_start]
        |
        v
 [expert_structure]   [expert_example]   [expert_limits]
        \                |                /
         \               |               /
          \              v              /
              [manager_final]

"""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

from autogen_system.config import create_model_client
from autogen_system.agents import (
    create_manager_start,
    create_expert_structure,
    create_expert_example,
    create_expert_limits,
    create_manager_final
)


MAIN_QUESTION = """
다음 질문에 대해, 핵심 내용을 5문장 이내로 명확하게 설명해주세요:
‘왜 멀티에이전트 시스템이 단일 LLM보다 복잡한 문제 해결에 더 적합할 수 있는가?’
""".strip()


async def run_parallel_workflow(question: str | None = None) -> None:
    """
    manager_start → (expert_structure, expert_example, expert_limits) → manager_final
    구조의 GraphFlow 워크플로우를 실행한다. (Parallel Execution)
    """
    if question is None:
        question = MAIN_QUESTION

    # 1) 공용 모델 클라이언트 생성 (Gemini 래핑하는 기존 함수 그대로 사용)
    model_client = create_model_client()

    # 2) 에이전트 정의 ──────────────────────────────────────
    manager_start = create_manager_start(model_client)
    expert_structure = create_expert_structure(model_client)
    expert_example = create_expert_example(model_client)
    expert_limits = create_expert_limits(model_client)
    manager_final = create_manager_final(model_client)

    # 3) 그래프 정의 (manager_start → 3 expert → manager_final) ─────────────
    builder = DiGraphBuilder()

    # node (에이전트) 추가 
    (
        builder.add_node(manager_start)
        .add_node(expert_structure)
        .add_node(expert_example)
        .add_node(expert_limits)
        .add_node(manager_final)
    )

    # manager_start → 3개의 expert (fan-out)
    builder.add_edge(manager_start, expert_structure)
    builder.add_edge(manager_start, expert_example)
    builder.add_edge(manager_start, expert_limits)

    # 세 expert → manager_final (fan-in)
    # activation_group을 주지 않아도,
    # 각 expert 발화 이후 manager_final이 후보로 올라오고,
    # '최종 답변:'을 출력하면 termination 조건으로 종료됨.
    builder.add_edge(expert_structure, manager_final)
    builder.add_edge(expert_example, manager_final)
    builder.add_edge(expert_limits, manager_final)

    graph = builder.build()

    # 4) 종료 조건 ─────────────────────────────────────────
    termination = TextMentionTermination(text="최종 답변:") | MaxMessageTermination(
        max_messages=20
    )

    # 5) GraphFlow 팀 구성 ─────────────────────────────────
    flow = GraphFlow(
        participants=builder.get_participants(),  # [manager_start, expert_*, manager_final]
        graph=graph,
        termination_condition=termination,
    )

    # 6) 시작 task: manager_start가 먼저 팀에게 브리핑하도록 함 ─────────────
    task = (
        "다음은 사용자가 제시한 질문입니다. 팀이 협력하여 답변을 만들어 주세요.\n\n"
        f"[사용자 질문]\n{question}\n"
    )

    # 첫 노드는 manager_start가 담당하게 됨
    stream = flow.run_stream(task=task)

    # 7) 콘솔에 대화 내용을 순서대로 출력
    await Console(stream)

    # 8) 리소스 정리
    await model_client.close()