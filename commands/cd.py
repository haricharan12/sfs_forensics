# commands/cd.py - Change directory command

from commands.base import Command

class ChangeDirectoryCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Change the current directory"
    
    def execute(self, *args) -> None:
        if not hasattr(self.explorer, 'fs_parser') or not self.explorer.fs_parser:
            print("SquashFS filesystem not mounted. Use 'mount' command first.")
            return
        
        if not args:
            print("Usage: cd <directory>")
            return
        
        path = args[0]
        try:
            if self.explorer.fs_parser.change_directory(path):
                print(f"Changed directory to: {path}")
            else:
                print(f"Directory not found: {path}")
        except Exception as e:
            print(f"Error changing directory: {e}")