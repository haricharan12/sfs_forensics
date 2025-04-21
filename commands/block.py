# commands/block.py - Block command

from commands.base import Command
from commands import register

@register()
class BlockCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show block size information"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine block size.")
            return
            
        sb = self.explorer.superblock
        print(f"\nBlock size: {sb.block_size} bytes ({self._format_size(sb.block_size)})")
        print(f"Block log: {sb.block_log} (2^{sb.block_log} = {sb.block_size})")