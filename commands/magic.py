# commands/magic.py - Magic command

import struct
from commands.base import Command
from commands import register
from squashfs import SQUASHFS_MAGIC

@register()
class MagicCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Check magic number"
    
    def execute(self, *args) -> None:
        if len(self.explorer.raw_data) < 4:
            print("File is too small to contain a magic number.")
            return
            
        magic = struct.unpack("<I", self.explorer.raw_data[:4])[0]
        print(f"\nMagic number: 0x{magic:08x}")
        
        if magic == SQUASHFS_MAGIC:
            print("This is a valid SquashFS magic number (hsqs in ASCII).")
        else:
            print(f"Invalid magic number. Expected 0x{SQUASHFS_MAGIC:08x} (hsqs).")
            
            # Try to interpret as ASCII
            try:
                ascii_magic = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in self.explorer.raw_data[:4])
                print(f"ASCII interpretation: '{ascii_magic}'")
            except:
                pass