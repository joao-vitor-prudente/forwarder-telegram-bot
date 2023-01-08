from sqlalchemy.exc import SQLAlchemyError

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import FilterDoesNotExistException, NotAuthorizedException
from classes.fatal_exceptions import DatabaseCommitException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Filter
    

def query_database(condition: str, mode: str, session: SessionProtocol) -> Filter | None | Exception:
    """Queries the database for filter.

    Args:
        condition (str): condition value from command.
        mode (str): blacklist, replacement or link_remover.
        session (SessionProtocol): sqlalchemy session instance.
        replacement (str | None): replacement value from command if mode is replacement, else None.
        
    Returns:
        Filter | None | Exception: filter from database if any or exception if any.
    """
        
    try:
        filter_: Filter | None = session.query(Filter).filter(Filter.condition == condition and Filter.mode == mode).first()
    except SQLAlchemyError as e:
        return DatabaseCommitException(exc=e)
    
    return filter_


def validate(filter_: Filter | None) -> Filter | Exception:
    """Validates the filter.

    Args:
        filter_ (Filter): validated filter from database or exception if any.
        
    Returns:
        None | Exception: validated filter if everything went well or exception if validation fails.
    """

    if filter_ is None: return FilterDoesNotExistException()
    return filter_
    


def commit_to_database(filter_: Filter, session: SessionProtocol) -> None | Exception:
    """Registers the filter in the database.

    Args:
        filter_ (Filter): validated filter from database.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        session.delete(filter_)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseCommitException(exc=e)


def remove_filter(command: str | None, chat_id: int, session: SessionProtocol, mode: str) -> str | Exception: 
    """Route to remove a filter from the database.

    Args:
        command (str | None): command string from event.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.
        mode (str): blacklist, replacement or link_remover.


    Returns:
        str | Exception: ok message or exception if any
    """
    
    # check if user is authorized
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)
    
    # parse command
    command = command if command is not None else ""
    flags: tuple[str, ...] = ("condition", )
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    condition: str = args[0]
    
    # query database
    filter_: Filter | None | Exception = query_database(condition, mode, session)
    if isinstance(filter_, Exception): return filter_
    
    # validate filter
    validated_filter: Filter | Exception = validate(filter_)
    if isinstance(validated_filter, Exception): return validated_filter
    
    # commit to database
    res: None | Exception = commit_to_database(validated_filter, session)
    if isinstance(res, Exception): return res
    
    return "Filter removed successfully!"
    