# commands/info.py - Info command

import time
from commands.base import Command
from commands import register
from squashfs import CompressionID

@register()
class InfoCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show all superblock information"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Use 'hex' or 'raw' to examine the file data.")
            return
            
        sb = self.explorer.superblock
        print("\nSquashFS Superblock Information:")
        print(f"  Magic:                0x{sb.magic:08x}")
        print(f"  Inode Count:          {sb.inode_count}")
        
        # Format date
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sb.modification_time))
        print(f"  Modification Time:    {date_str} UTC")
        
        print(f"  Block Size:           {sb.block_size} bytes")
        print(f"  Fragment Entry Count: {sb.fragment_entry_count}")
        
        # Get compression name
        comp_name = "Unknown"
        try:
            comp_name = CompressionID(sb.compression_id).name
        except ValueError:
            comp_name = f"Unknown ({sb.compression_id})"
        print(f"  Compression:          {comp_name}")
        
        print(f"  Block Log:            {sb.block_log}")
        print(f"  Flags:                0x{sb.flags:04x}")
        print(f"  ID Count:             {sb.id_count}")
        print(f"  Version:              {sb.version_major}.{sb.version_minor}")
        print(f"  Root Inode Ref:       0x{sb.root_inode_ref:016x}")
        print(f"  Bytes Used:           {sb.bytes_used} ({self._format_size(sb.bytes_used)})")
        print(f"  ID Table Start:       0x{sb.id_table_start:016x}")
        print(f"  XAttr ID Table Start: 0x{sb.xattr_id_table_start:016x}")
        print(f"  Inode Table Start:    0x{sb.inode_table_start:016x}")
        print(f"  Directory Table Start: 0x{sb.directory_table_start:016x}")
        print(f"  Fragment Table Start: 0x{sb.fragment_table_start:016x}")
        print(f"  Export Table Start:   0x{sb.export_table_start:016x}")