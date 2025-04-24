# commands/__init__.py - Command registry

# Global command registry
COMMAND_REGISTRY = {}

def register(*names):
   
    def decorator(cls):
        if not names:
            # Auto-derive name from class name
            cmd_name = cls.__name__.lower()
            if cmd_name.endswith('command'):
                cmd_name = cmd_name[:-7]  # Remove 'command' suffix
            COMMAND_REGISTRY[cmd_name] = cls
        else:
            # Register with all provided names
            for name in names:
                COMMAND_REGISTRY[name] = cls
        return cls
    return decorator