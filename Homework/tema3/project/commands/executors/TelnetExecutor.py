from Homework.tema3.project.commands.executors import CommandExecutor


class TelnetExecutor(CommandExecutor):
    @with_telnet
    def run_command(self, cmd: str):
        pass

    @with_telnet
    def run_commands(self, cmds: list[str]):
        for cmd in cmds:
            self.run_command(cmd)
