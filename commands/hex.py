# commands/hex.py - Hex dump command

from commands.base import Command
from commands import register

@register()
class HexCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show hex dump of the first bytes (default: 64)"
    
    def execute(self, *args) -> None:
        bytes_to_show = 64  # Default
        
        if args and args[0].isdigit():
            bytes_to_show = min(int(args[0]), len(self.explorer.raw_data))
        
        print(f"\nHex dump of first {bytes_to_show} bytes:")
        
        # Simple hex dump
        for i in range(0, bytes_to_show, 16):
            chunk = self.explorer.raw_data[i:min(i+16, bytes_to_show)]
            hex_values = ' '.join(f'{b:02x}' for b in chunk)
            ascii_values = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            
            print(f"{i:04x}: {hex_values:<48} |{ascii_values}|")