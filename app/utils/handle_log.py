from pathlib import Path

from typing import Any, Callable, Coroutine

from classes.fatal_exceptions import FatalException, LogException


def create_log(exc: FatalException) -> None | Exception:
    """Creates log text file containing the content of an exception.

    Args:
        exc (FatalException): exception to log.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    res: None | Exception = cleanup_log()
    if isinstance(res, Exception): return res
    
    try:  
        with open("log/log.log", "w") as f:
            f.write(repr(exc))
    except Exception as e:
        return LogException(exc=e)


def cleanup_log() -> None | Exception:
    """Make sure the directory for the log file exists and the log file does not.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        if not Path("temp").exists():
                Path("temp").mkdir()
        if Path("log/log.log").exists():
            Path("log/log.log").unlink()
    except Exception as e:
        return LogException(exc=e)
    
    
async def handle_log(exc: FatalException, f: Callable[[str], Coroutine[Any, Any, Any]]) -> None | Exception:
    """Handles the creation of a log file and the sending of the log file to the user.

    Args:
        exc (FatalException): exception to log.
        f (Callable[[str], Coroutine[Any, Any, Any]]): function to send the log file.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    res: None | Exception = create_log(exc)
    if isinstance(res, Exception): return res
    
    try:
        await f("log/log.log")
    except Exception as e:
        return LogException(exc=e)
    
    res: None | Exception = cleanup_log()
    if isinstance(res, Exception): return res
    
