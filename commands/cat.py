# commands/cat.py - Show file contents command

from commands.base import Command

class CatCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Display file contents"
    
    def execute(self, *args) -> None:
        if not hasattr(self.explorer, 'fs_parser') or not self.explorer.fs_parser:
            print("SquashFS filesystem not mounted. Use 'mount' command first.")
            return
        
        if not args:
            print("Usage: cat <filename>")
            return
        
        filename = args[0]
        try:
            content = self.explorer.fs_parser.get_file_content(filename)
            if content:
                # Try to decode as text, fall back to hex dump for binary
                try:
                    text_content = content.decode('utf-8')
                    print(f"\nFile contents of {filename}:")
                    print(text_content)
                except UnicodeDecodeError:
                    print(f"\nBinary file: {filename} (showing hex dump)")
                    # Hex dump of first 256 bytes
                    for i in range(0, min(256, len(content)), 16):
                        chunk = content[i:i+16]
                        hex_values = ' '.join(f'{b:02x}' for b in chunk)
                        ascii_values = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                        print(f"{i:04x}: {hex_values:<48} |{ascii_values}|")
                    
                    if len(content) > 256:
                        print(f"... truncated, total size: {len(content)} bytes")
            else:
                print(f"File not found or is empty: {filename}")
        except Exception as e:
            print(f"Error reading file: {e}")