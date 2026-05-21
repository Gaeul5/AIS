import asyncio
import logging


from autogen_system.workflow_routing import run_routing_workflow


def main() -> None:
    asyncio.run(run_routing_workflow())


if __name__ == "__main__":
    main()
