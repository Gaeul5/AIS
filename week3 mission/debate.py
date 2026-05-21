import asyncio
from autogen_system.workflow_debate import run_debate_workflow


def main() -> None:
    asyncio.run(run_debate_workflow())


if __name__ == "__main__":
    main()
