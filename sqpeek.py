#!/usr/bin/env python3
"""
sqpeek.py – minimal SquashFS v4 reader (read‑only, gzip only)

Usage:
  ./sqpeek.py IMAGE.sfs info
  ./sqpeek.py IMAGE.sfs ls [DIR]

Features implemented
  • super‑block parse & sanity check
  • directory enumeration (recursive)
Limitations
  – files larger than one data‑block are not streamed yet (no `cat`)
  – ignores fragments, xattrs, export table
  – supports only compression = 1 (gzip)
"""

import struct, sys, zlib, os, pathlib, time

MAGIC   = 0x73717368           # "hsqs" little‑endian
SB_FMT  = "<IIIIIHHHHHHQQQQQQQ"  # 5×I, 6×H, 7×Q  → 88 bytes
SUPER_LEN = struct.calcsize(SB_FMT)

DIR_TYPE  = 1
FILE_TYPE = 8

class SquashFSImage:
    def __init__(self, path: str):
        self.f = open(path, "rb")
        self._read_super()

    # ---------- super‑block ----------
    def _read_super(self):
        self.f.seek(0)
        blob = self.f.read(96)                    # 88 useful + 8 padding
        (magic, self.inode_count, self.mkfs_time, self.block_size,
         self.frag_count, self.compression, self.block_log, self.flags,
         self.id_count, self.version_major, self.version_minor,
         self.root_inode_ref, self.bytes_used, self.id_tbl_start,
         self.xattr_tbl_start, self.inode_tbl_start,
         self.dir_tbl_start, self.frag_tbl_start,
         self.lookup_tbl_start) = struct.unpack_from(SB_FMT, blob)

        if magic != MAGIC:
            raise ValueError("Not a SquashFS image (bad magic)")
        if self.compression != 1:
            raise NotImplementedError("Only gzip‑compressed images handled")

    # ---------- low‑level helpers ----------
    def _block_at(self, pos: int) -> bytes:
        """Read & (maybe) decompress a metadata or data block."""
        self.f.seek(pos)
        hdr  = int.from_bytes(self.f.read(2), "little")
        size = hdr & 0x7FFF
        stored = (hdr & 0x8000) == 0
        data = self.f.read(size)
        return data if stored else zlib.decompress(data)

    def _inode_blob(self, inode_ref: int) -> bytes:
        blk_off = inode_ref & ~0xFFF
        inode_off = inode_ref & 0xFFF
        block = self._block_at(self.inode_tbl_start + blk_off)
        return block[inode_off:]

    # ---------- public API ----------
    def print_info(self):
        t = time.strftime("%Y‑m‑d %H:%M:%S", time.localtime(self.mkfs_time))
        print(f"SquashFS {self.version_major}.{self.version_minor}, "
              f"gzip, block={self.block_size} bytes")
        print(f"Inodes  : {self.inode_count}")
        print(f"Created : {t}")
        print(f"Bytes   : {self.bytes_used}")
        print(f"Root ref: 0x{self.root_inode_ref:08x}")

    def ls(self, path_parts=None, prefix="/"):
        """Recursively list directory entries starting at path_parts."""
        if path_parts in (None, [], [""]):
            inode_ref = self.root_inode_ref
        else:
            inode_ref = self._walk(path_parts)
        self._recurse_dir(inode_ref, prefix)

    # ---------- directory traversal ----------
    def _walk(self, parts, inode_ref=None):
        """Follow parts[] down from inode_ref (default = root)."""
        if inode_ref is None:
            inode_ref = self.root_inode_ref
        if not parts:
            return inode_ref
        name = parts[0]
        child = self._find_child(inode_ref, name)
        if child is None:
            raise FileNotFoundError("/".join(parts))
        return self._walk(parts[1:], child)

    def _find_child(self, dir_inode_ref, target):
        raw = self._inode_blob(dir_inode_ref)
        if (raw[16] & 0xF) != DIR_TYPE:
            return None
        start_block, _, offset, count = struct.unpack_from("<IIII", raw, 24)
        meta = self._block_at(self.dir_tbl_start + start_block)
        p = offset
        for _ in range(count):
            nlen, itype, child_ref = struct.unpack_from("<HBxI", meta, p)
            name = meta[p+8:p+8+nlen].decode()
            if name == target:
                return child_ref
            p += 8 + nlen + ((-nlen) & 3)
        return None

    def _recurse_dir(self, inode_ref, base):
        raw = self._inode_blob(inode_ref)
        itype = raw[16] & 0xF
        if itype != DIR_TYPE:
            print(base.rstrip("/"))
            return
        start_block, _, offset, cnt = struct.unpack_from("<IIII", raw, 24)
        meta = self._block_at(self.dir_tbl_start + start_block)
        p = offset
        for _ in range(cnt):
            nlen, child_type, child_ref = struct.unpack_from("<HBxI", meta, p)
            name = meta[p+8:p+8+nlen].decode()
            new_base = base + name + ("/" if child_type == DIR_TYPE else "")
            if child_type == DIR_TYPE:
                self._recurse_dir(child_ref, new_base)
            else:
                print(new_base)
            p += 8 + nlen + ((-nlen) & 3)

# ---------- CLI glue ----------
def usage():
    print("Usage:")
    print("  sqpeek.py IMAGE.sfs info")
    print("  sqpeek.py IMAGE.sfs ls [DIR]")
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        usage()

    img   = SquashFSImage(sys.argv[1])
    cmd   = sys.argv[2]

    if cmd == "info":
        img.print_info()
    elif cmd == "ls":
        dir_arg = sys.argv[3] if len(sys.argv) > 3 else "/"
        parts = dir_arg.strip("/").split("/")
        img.ls(parts if dir_arg != "/" else None,
               prefix="/" if dir_arg == "/" else dir_arg.rstrip("/") + "/")
    else:
        usage()

if __name__ == "__main__":
    main()
