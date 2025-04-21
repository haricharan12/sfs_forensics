#!/usr/bin/env python3
import struct
import sys
import os
import time
import argparse
from enum import IntEnum
from typing import NamedTuple, Dict, Any, Callable, Optional, List, Type


# Compression ID constants
class CompressionID(IntEnum):
    GZIP = 1
    LZMA = 2
    LZO = 3
    XZ = 4
    LZ4 = 5
    ZSTD = 6


# Define the SquashFS superblock structure
class SquashFSSuperblock(NamedTuple):
    magic: int
    inode_count: int
    modification_time: int
    block_size: int
    fragment_entry_count: int
    compression_id: int
    block_log: int
    flags: int
    id_count: int
    version_major: int
    version_minor: int
    root_inode_ref: int
    bytes_used: int
    id_table_start: int
    xattr_id_table_start: int
    inode_table_start: int
    directory_table_start: int
    fragment_table_start: int
    export_table_start: int


# Magic number constant
SQUASHFS_MAGIC = 0x73717368


def unpack_squashfs_superblock(data: bytes) -> Optional[SquashFSSuperblock]:
    """
    Unpack bytes into a SquashFSSuperblock according to the SquashFS specification.
    
    Args:
        data: Bytes containing a SquashFS superblock (at least 96 bytes)
        
    Returns:
        A SquashFSSuperblock instance with unpacked fields or None if unpacking fails
    """
    # Check if we have enough data for the superblock
    if len(data) < 96:
        print(f"Warning: Data too short for a complete superblock: expected at least 96 bytes, got {len(data)}")
        # Try to unpack what we can for diagnostic purposes
        try:
            if len(data) >= 4:
                magic = struct.unpack("<I", data[:4])[0]
                if magic == SQUASHFS_MAGIC:
                    print(f"Found valid magic number (0x{magic:08x}), but superblock is incomplete")
                else:
                    print(f"Invalid magic number: expected 0x{SQUASHFS_MAGIC:08x}, got 0x{magic:08x}")
            return None
        except Exception as e:
            print(f"Error examining file header: {e}")
            return None
    
    # Try to unpack with safe error handling
    try:
        # Unpack the superblock from bytes (little-endian)
        # Note: The 'x' at the end is for padding - we need to make sure we have enough bytes
        if len(data) < 97:  # We need 97 bytes including the padding byte
            data = data + b'\x00' * (97 - len(data))  # Pad with zeros if needed
            
        unpacked = struct.unpack("<IIIIIHHHHHHQQQQQQQQx", data[:97])
        
        superblock = SquashFSSuperblock(
            magic=unpacked[0],
            inode_count=unpacked[1],
            modification_time=unpacked[2],
            block_size=unpacked[3],
            fragment_entry_count=unpacked[4],
            compression_id=unpacked[5],
            block_log=unpacked[6],
            flags=unpacked[7],
            id_count=unpacked[8],
            version_major=unpacked[9],
            version_minor=unpacked[10],
            root_inode_ref=unpacked[11],
            bytes_used=unpacked[12],
            id_table_start=unpacked[13],
            xattr_id_table_start=unpacked[14],
            inode_table_start=unpacked[15],
            directory_table_start=unpacked[16],
            fragment_table_start=unpacked[17],
            export_table_start=unpacked[18]
        )
        
        # Validate magic number
        if superblock.magic != SQUASHFS_MAGIC:
            print(f"Invalid magic number: expected 0x{SQUASHFS_MAGIC:08x}, got 0x{superblock.magic:08x}")
            return None
        
        # Validate block_log against block_size
        # We'll just warn instead of failing
        if (1 << superblock.block_log) != superblock.block_size:
            print(f"Warning: block_log ({superblock.block_log}) does not match block_size ({superblock.block_size})")
        
        return superblock
    
    except struct.error as e:
        print(f"Error unpacking superblock: {e}")
        print("The file may not be a valid SquashFS image or may be corrupted.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Command registry
COMMAND_REGISTRY = {}


def register_command(name):
    """Decorator to register commands in the global registry"""
    def decorator(cls):
        COMMAND_REGISTRY[name] = cls
        return cls
    return decorator


class Command:
    """Base class for all commands"""
    
    def __init__(self, explorer):
        self.explorer = explorer
    
    @staticmethod
    def get_help() -> str:
        """Return help text for the command"""
        return "No help available for this command"
    
    def execute(self, *args) -> None:
        """Execute the command with the given arguments"""
        raise NotImplementedError("Command subclasses must implement execute()")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable format"""
        # Convert bytes to human-readable format
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if size_bytes < 1024.0 or unit == 'TiB':
                break
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} {unit}"


@register_command("help")
class HelpCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show this help message"
    
    def execute(self, *args) -> None:
        print("\nAvailable commands:")
        
        # Find the maximum command name length for alignment
        max_length = max(len(cmd) for cmd in COMMAND_REGISTRY.keys())
        
        # Sort commands alphabetically
        for cmd_name in sorted(COMMAND_REGISTRY.keys()):
            cmd_class = COMMAND_REGISTRY[cmd_name]
            help_text = cmd_class.get_help()
            print(f"  {cmd_name.ljust(max_length + 2)}- {help_text}")
        
        print("\nUsage: command [arguments]")


@register_command("info")
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


@register_command("date")
class DateCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show filesystem creation date"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine date.")
            return
            
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.explorer.superblock.modification_time))
        print(f"\nFilesystem creation date: {date_str} UTC")
        print(f"Unix timestamp: {self.explorer.superblock.modification_time}")


@register_command("compression")
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


@register_command("size")
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


@register_command("version")
class VersionCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show SquashFS version"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine version.")
            return
            
        sb = self.explorer.superblock
        print(f"\nSquashFS Version: {sb.version_major}.{sb.version_minor}")


@register_command("block")
class BlockCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show block size information"
    
    def execute(self, *args) -> None:
        if not self.explorer.superblock:
            print("No valid superblock found. Cannot determine block size.")
            return
            
        sb = self.explorer.superblock
        print(f"\nBlock size: {sb.block_size} bytes ({self._format_size(sb.block_size)})")
        print(f"Block log: {sb.block_log} (2^{sb.block_log} = {sb.block_size})")


@register_command("flags")
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


@register_command("offsets")
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


@register_command("hex")
class HexDumpCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show hex dump of the first bytes (default: 64)"
    
    def execute(self, *args) -> None:
        bytes_to_show = 64  # Default
        
        if args and args[0].isdigit():
            bytes_to_show = min(int(args[0]), len(self.explorer.raw_data))
        
        print(f"\nHex dump of first {bytes_to_show} bytes:")
        
        # Simple hex dump
        for i in range(0, bytes_to_show, 16):
            chunk = self.explorer.raw_data[i:min(i+16, bytes_to_show)]
            hex_values = ' '.join(f'{b:02x}' for b in chunk)
            ascii_values = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            
            print(f"{i:04x}: {hex_values:<48} |{ascii_values}|")


@register_command("raw")
class RawBytesCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Show raw bytes as integers (default: 64)"
    
    def execute(self, *args) -> None:
        bytes_to_show = 64  # Default
        
        if args and args[0].isdigit():
            bytes_to_show = min(int(args[0]), len(self.explorer.raw_data))
        
        print(f"\nRaw bytes (as integers) of first {bytes_to_show} bytes:")
        
        for i in range(0, bytes_to_show, 8):
            chunk = self.explorer.raw_data[i:min(i+8, bytes_to_show)]
            values = ' '.join(f'{b:3d}' for b in chunk)
            print(f"{i:04x}: {values}")


@register_command("magic")
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


@register_command("exit")
@register_command("quit")
class ExitCommand(Command):
    @staticmethod
    def get_help() -> str:
        return "Exit the explorer"
    
    def execute(self, *args) -> None:
        print("Exiting SquashFS Explorer. Goodbye!")
        sys.exit(0)


class SquashFSExplorer:
    def __init__(self, squashfs_file: str, force: bool = False):
        self.squashfs_file = squashfs_file
        self.force = force
        self.superblock = None
        self.raw_data = None
        
        # Read the superblock
        with open(squashfs_file, "rb") as f:
            # Read the first 4K for analysis
            self.raw_data = f.read(4096)
        
        if len(self.raw_data) < 4:
            print(f"Error: File is too small to be a valid SquashFS image (size: {len(self.raw_data)} bytes)")
            if not force:
                sys.exit(1)
        
        self.superblock = unpack_squashfs_superblock(self.raw_data)
        
        if self.superblock:
            print(f"Successfully opened {squashfs_file}")
        else:
            print(f"Warning: Could not parse a valid SquashFS superblock from {squashfs_file}")
            if not force:
                print("Use --force to attempt exploration anyway.")
                sys.exit(1)
            print("Continuing in limited mode due to --force flag.")
    
    def run(self):
        """Start the interactive explorer"""
        print("\nSquashFS Explorer")
        print(f"File: {self.squashfs_file}")
        print("Type 'help' for a list of commands.")
        
        while True:
            try:
                user_input = input("\nsquashfs> ").strip()
                
                if not user_input:
                    continue
                
                # Split command and arguments
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                args = cmd_parts[1:] if len(cmd_parts) > 1 else []
                
                if cmd in COMMAND_REGISTRY:
                    # Create a command instance and execute it
                    command = COMMAND_REGISTRY[cmd](self)
                    command.execute(*args)
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for a list of commands.")
            
            except KeyboardInterrupt:
                print("\nReceived interrupt. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="SquashFS Explorer - Interactive CLI tool")
    parser.add_argument("squashfs_file", help="Path to SquashFS file to explore")
    parser.add_argument("--force", "-f", action="store_true", help="Force exploration even if file doesn't appear to be a valid SquashFS image")
    args = parser.parse_args()
    
    if not os.path.exists(args.squashfs_file):
        print(f"Error: File '{args.squashfs_file}' not found.")
        sys.exit(1)
    
    explorer = SquashFSExplorer(args.squashfs_file, args.force)
    explorer.run()


if __name__ == "__main__":
    main()