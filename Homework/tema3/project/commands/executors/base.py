# commands/executors/base.py
from abc import ABC, abstractmethod


class CommandExecutor(ABC):
    @abstractmethod
    def run_command(self, cmd: str): ...

    def run_commands(self, cmds: list[str]):
        for cmd in cmds:
            self.run_command(cmd)
