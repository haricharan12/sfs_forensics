# commands/__init__.py - Command registry

from commands.base import Command
from commands.help import HelpCommand
from commands.info import InfoCommand
from commands.date import DateCommand
from commands.compression import CompressionCommand
from commands.size import SizeCommand
from commands.version import VersionCommand
from commands.block import BlockCommand
from commands.flags import FlagsCommand
from commands.offsets import OffsetsCommand
from commands.hex import HexDumpCommand
from commands.raw import RawBytesCommand
from commands.magic import MagicCommand
from commands.exit import ExitCommand

# Global command registry
COMMAND_REGISTRY = {
    "help": HelpCommand,
    "info": InfoCommand,
    "date": DateCommand,
    "compression": CompressionCommand,
    "size": SizeCommand,
    "version": VersionCommand,
    "block": BlockCommand,
    "flags": FlagsCommand,
    "offsets": OffsetsCommand,
    "hex": HexDumpCommand,
    "raw": RawBytesCommand,
    "magic": MagicCommand,
    "exit": ExitCommand,
    "quit": ExitCommand
}