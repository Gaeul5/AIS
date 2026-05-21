import asyncio
from autogen_system.workflow_parallel import run_parallel_workflow


def main() -> None:
    asyncio.run(run_parallel_workflow())


if __name__ == "__main__":
    main()