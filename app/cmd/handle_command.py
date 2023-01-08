from app.cmd.parse import parse_command
from app.cmd.tokenize import tokenize_command

from app.validations.validate_command import validate_command

from classes.validation_exceptions import  InvalidCommandException

def handle_command(command: str, flags: tuple[str, ...]) -> tuple[str, ...] | Exception:
    """Make all validations necessary to handle the command and parse it to get the arguments.

    Args:
        command (str): command string from the message.
        flags (list[str]): list of flags in the form --flag=... to be parsed.

    Returns:
        tuple[str, ...] | Exception: tuple of arguments or exception if any.
    """
    
    if not validate_command(command, len(flags)):
        return InvalidCommandException(command=command)
    
    tokens: list[str] = tokenize_command(command)
    flags_args: dict[str, str] = parse_command(tokens)

    args_: list[str | None] = [flags_args.get(arg) for arg in flags]
    
    if any([arg is None for arg in args_]):
        return InvalidCommandException(command=command)
    
    args: tuple[str, ...] = tuple([arg for arg in args_ if arg is not None])
    return args