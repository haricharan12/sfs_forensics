# commands/help.py - Help command

from commands.base import Command
from commands import register, COMMAND_REGISTRY

@register()
class HelpCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show this help message"
    
    def execute(self, *args) -> None:
        print("\nAvailable commands:")
        
        # Find the maximum command name length for alignment
        max_length = max(len(cmd) for cmd in COMMAND_REGISTRY.keys())
        
        # Get unique command classes to avoid showing duplicates
        unique_commands = {}
        for cmd_name, cmd_class in COMMAND_REGISTRY.items():
            if cmd_class not in unique_commands.values():
                unique_commands[cmd_name] = cmd_class
        
        # Sort commands alphabetically
        for cmd_name in sorted(unique_commands.keys()):
            cmd_class = unique_commands[cmd_name]
            help_text = cmd_class.get_help()
            print(f"  {cmd_name.ljust(max_length + 2)}- {help_text}")
        
        # List command aliases
        aliases = {}
        for cmd_name, cmd_class in COMMAND_REGISTRY.items():
            for primary_name, primary_class in unique_commands.items():
                if cmd_class == primary_class and cmd_name != primary_name:
                    if primary_name not in aliases:
                        aliases[primary_name] = []
                    aliases[primary_name].append(cmd_name)
        
        if aliases:
            print("\nCommand aliases:")
            for primary_name, alias_list in aliases.items():
                print(f"  {primary_name}: {', '.join(alias_list)}")
        
        print("\nUsage: command [arguments]")