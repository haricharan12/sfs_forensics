# commands/flags.py - Flags command

from commands.base import Command
from commands import register

@register()
class FlagsCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show superblock flags"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine flags.")
            return
            
        flags = self.explorer.superblock.flags
        print(f"\nSuperblock flags: 0x{flags:04x}")
        
        # Define known flags
        flag_descriptions = {
            0x0001: "UNCOMPRESSED_INODES",
            0x0002: "UNCOMPRESSED_DATA",
            0x0004: "CHECK",
            0x0008: "UNCOMPRESSED_FRAGMENTS",
            0x0010: "NO_FRAGMENTS",
            0x0020: "ALWAYS_FRAGMENTS",
            0x0040: "DUPLICATES",
            0x0080: "EXPORTABLE",
            0x0100: "UNCOMPRESSED_XATTRS",
            0x0200: "NO_XATTRS",
            0x0400: "COMPRESSOR_OPTIONS",
            0x0800: "UNCOMPRESSED_IDS"
        }
        
        # Print active flags
        active_flags = []
        for flag_bit, description in flag_descriptions.items():
            if flags & flag_bit:
                active_flags.append(f"  - {description} (0x{flag_bit:04x})")
        
        if active_flags:
            print("Active flags:")
            for flag in active_flags:
                print(flag)
        else:
            print("No flags are set.")