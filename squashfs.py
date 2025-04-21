# squashfs.py - Core SquashFS functionality

import struct
from enum import IntEnum
from typing import NamedTuple, Optional


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