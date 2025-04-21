#!/usr/bin/env python3
# tool.py - Main script for SquashFS Explorer

import sys
import os
import argparse
from squashfs import SquashFSSuperblock, unpack_squashfs_superblock
from commands import COMMAND_REGISTRY


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
                    command_class = COMMAND_REGISTRY[cmd]
                    command = command_class(self)
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