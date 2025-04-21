# commands/size.py - Size command

import os
from commands.base import Command

class SizeCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show filesystem size information"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Limited size information available.")
            try:
                file_size = os.path.getsize(self.explorer.squashfs_file)
                print(f"File size: {file_size} bytes ({self._format_size(file_size)})")
            except OSError as e:
                print(f"Error getting file size: {e}")
            return
            
        sb = self.explorer.superblock
        fs_size = sb.bytes_used
        
        print(f"\nFilesystem size: {fs_size} bytes ({self._format_size(fs_size)})")
        print(f"Block size: {sb.block_size} bytes ({self._format_size(sb.block_size)})")
        print(f"Inode count: {sb.inode_count}")
        print(f"Fragment entry count: {sb.fragment_entry_count}")
        
        # Calculate compression ratio if possible
        try:
            file_size = os.path.getsize(self.explorer.squashfs_file)
            if file_size > 0:
                print(f"SquashFS file size: {file_size} bytes ({self._format_size(file_size)})")
        except OSError:
            pass