import asyncio
from autogen_system.workflow_sequential import run_sequential_workflow


def main() -> None:
    asyncio.run(run_sequential_workflow())


if __name__ == "__main__":
    main()
