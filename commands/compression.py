# commands/compression.py - Compression command

from commands.base import Command
from squashfs import CompressionID

class CompressionCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show compression method"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine compression method.")
            return
            
        comp_id = self.explorer.superblock.compression_id
        comp_name = "Unknown"
        try:
            comp_name = CompressionID(comp_id).name
        except ValueError:
            comp_name = f"Unknown ({comp_id})"
        
        print(f"\nCompression method: {comp_name} (ID: {comp_id})")
        
        # Additional info about the compression method
        compression_info = {
            CompressionID.GZIP: "Standard GZIP compression (zlib)",
            CompressionID.LZMA: "LZMA compression, high compression ratio",
            CompressionID.LZO: "LZO compression, optimized for speed",
            CompressionID.XZ: "XZ compression, high compression ratio",
            CompressionID.LZ4: "LZ4 compression, very fast decompression",
            CompressionID.ZSTD: "Zstandard compression, good balance of speed and ratio"
        }
        
        if comp_id in compression_info:
            print(f"Description: {compression_info[comp_id]}")