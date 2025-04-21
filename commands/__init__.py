# commands/__init__.py - Command registry

# Global command registry
COMMAND_REGISTRY = {}

def register(name=None):
    """
    Decorator to register a command class in the registry.
    
    Usage:
        @register()
        class MyCommand(Command):
            ...
    
        @register("custom_name")
        class MyOtherCommand(Command):
            ...
    
        @register("name1", "name2")  # Register with multiple names
        class MultiNameCommand(Command):
            ...
    """
    def decorator(cls):
        # Get the command name from the class name if not specified
        if name is None:
            # Convert CamelCase to lowercase with underscores
            cmd_name = ''.join(['_' + c.lower() if c.isupper() else c for c in cls.__name__]).lstrip('_')
            # Remove 'Command' suffix if present
            cmd_name = cmd_name.replace('_command', '')
            COMMAND_REGISTRY[cmd_name] = cls
        elif isinstance(name, str):
            # Register with the provided name
            COMMAND_REGISTRY[name] = cls
        else:
            # Register with multiple names
            for n in name:
                COMMAND_REGISTRY[n] = cls
        return cls
    
    # Handle case when called with arguments or directly with class
    if callable(name):
        cls = name
        name = None
        return decorator(cls)
    return decorator