# commands/mount.py - Mount the SquashFS filesystem

from commands.base import Command
from squashfs_fs import SquashFSParser

class MountCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Mount the SquashFS filesystem for browsing"
    
    def execute(self, *args) -> None:
        try:
            # Initialize the filesystem parser
            self.explorer.fs_parser = SquashFSParser(self.explorer.squashfs_file)
            
            if self.explorer.fs_parser.superblock:
                print("SquashFS filesystem mounted successfully.")
                print("Use 'ls' to list files and directories.")
            else:
                print("Failed to mount SquashFS filesystem.")
        except Exception as e:
            print(f"Error mounting filesystem: {e}")