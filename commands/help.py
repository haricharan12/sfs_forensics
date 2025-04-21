# commands/help.py - Help command

from commands.base import Command
# from commands import COMMAND_REGISTRY

class HelpCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show this help message"
    
    def execute(self, *args) -> None:
        print("\nAvailable commands:")
        
        # Find the maximum command name length for alignment
        max_length = max(len(cmd) for cmd in COMMAND_REGISTRY.keys())
        
        # Sort commands alphabetically and exclude duplicates
        unique_commands = {}
        for cmd_name, cmd_class in COMMAND_REGISTRY.items():
            if cmd_class not in unique_commands.values():
                unique_commands[cmd_name] = cmd_class
        
        for cmd_name in sorted(unique_commands.keys()):
            cmd_class = unique_commands[cmd_name]
            help_text = cmd_class.get_help()
            print(f"  {cmd_name.ljust(max_length + 2)}- {help_text}")
        
        print("\nUsage: command [arguments]")