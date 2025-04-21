# commands/offsets.py - Offsets command

from commands.base import Command
from commands import register

@register()
class OffsetsCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show table offsets"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine table offsets.")
            return
            
        sb = self.explorer.superblock
        print("\nTable offsets:")
        print(f"  ID Table:           0x{sb.id_table_start:016x}")
        print(f"  XAttr ID Table:     0x{sb.xattr_id_table_start:016x}")
        print(f"  Inode Table:        0x{sb.inode_table_start:016x}")
        print(f"  Directory Table:    0x{sb.directory_table_start:016x}")
        print(f"  Fragment Table:     0x{sb.fragment_table_start:016x}")
        print(f"  Export Table:       0x{sb.export_table_start:016x}")