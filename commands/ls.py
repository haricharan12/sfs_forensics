# commands/ls.py - List directory contents command

from commands.base import Command

class ListCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "List files and directories in the current directory"
    
    def execute(self, *args) -> None:
        if not hasattr(self.explorer, 'fs_parser') or not self.explorer.fs_parser:
            print("SquashFS filesystem not mounted. Use 'mount' command first.")
            return
        
        try:
            path = args[0] if args else None
            entries = self.explorer.fs_parser.list_directory(path)
            
            if not entries:
                print("No files or directories found.")
                return
            
            print("\nDirectory contents:")
            for entry in sorted(entries):
                print(f"  {entry}")
        except Exception as e:
            print(f"Error listing directory: {e}")