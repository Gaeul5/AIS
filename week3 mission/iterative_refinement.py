"""
실행하면,
Debater / Verifier / Moderator가 AutoGen RoundRobinGroupChat으로
질문에 대해 협력적으로 답변을 생성하는 과정을 콘솔에 출력한다.
"""

import asyncio
from autogen_system.workflow_iterative_refinement import run_iterative_refinement_workflow


def main():
    asyncio.run(run_iterative_refinement_workflow())


if __name__ == "__main__":
    main()
