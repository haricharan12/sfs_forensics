# commands/date.py - Date command

import time
from commands.base import Command
from commands import register

@register()
class DateCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show filesystem creation date"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine date.")
            return
            
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.explorer.superblock.modification_time))
        print(f"\nFilesystem creation date: {date_str} UTC")
        print(f"Unix timestamp: {self.explorer.superblock.modification_time}")