# commands/exit.py - Exit command

import sys
from commands.base import Command

class ExitCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Exit the explorer"
    
    def execute(self, *args) -> None:
        print("Exiting SquashFS Explorer. Goodbye!")
        sys.exit(0)