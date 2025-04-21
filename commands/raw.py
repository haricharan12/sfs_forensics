# commands/raw.py - Raw bytes command

from commands.base import Command
from commands import register

@register()
class RawCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show raw bytes as integers (default: 64)"
    
    def execute(self, *args) -> None:
        bytes_to_show = 64  # Default
        
        if args and args[0].isdigit():
            bytes_to_show = min(int(args[0]), len(self.explorer.raw_data))
        
        print(f"\nRaw bytes (as integers) of first {bytes_to_show} bytes:")
        
        for i in range(0, bytes_to_show, 8):
            chunk = self.explorer.raw_data[i:min(i+8, bytes_to_show)]
            values = ' '.join(f'{b:3d}' for b in chunk)
            print(f"{i:04x}: {values}")