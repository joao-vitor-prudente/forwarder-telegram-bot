from typing import TypeAlias

from sqlalchemy.exc import SQLAlchemyError

from uuid import uuid4

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import FilterAlreadyExistsException, NotAuthorizedException, CircularFilterException, ConditionIsEqualToReplacementException
from classes.fatal_exceptions import DatabaseCommitException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Filter

query_return_type: TypeAlias = tuple[Filter | None, Filter | None, Filter | None]
    

def query_database(condition: str, mode: str, session: SessionProtocol, replacement: str | None = None) -> query_return_type | Exception:
    """Queries the database for filter.

    Args:
        condition (str): condition value from command.
        mode (str): blacklist, replacement or link_remover.
        session (SessionProtocol): sqlalchemy session instance.
        replacement (str | None): replacement value from command if mode is replacement, else None.
        
    Returns:
         query_return_type | Exception: possible conflicting filters from database if everything went well, None if filter does not exist or exception if any.
    """
    
    if condition == replacement: return ConditionIsEqualToReplacementException()

    try:
        filter_1: Filter | None = session.query(Filter).filter(Filter.condition == condition and Filter.mode == mode).first()
        filter_2: Filter | None = session.query(Filter).filter(Filter.condition == replacement and Filter.mode == mode). first() if replacement is not None else None
        filter_3: Filter | None = session.query(Filter).filter(Filter.replacement == condition and Filter.mode == mode).first()
        return tuple([filter_1, filter_2, filter_3])
    except SQLAlchemyError as e:
        return DatabaseCommitException(exc=e)


def validate(conflicting_filters: query_return_type) -> None | Exception:
    """Validates the filter.

    Args:
        conflicting_filters (query_return_type): possible conflicting filters from database from database.
        
    Returns:
        None | Exception: validated filter if everything went well or exception if validation fails.
    """

    if conflicting_filters[0] is not None:
        return FilterAlreadyExistsException(
            condition=str(conflicting_filters[0].condition), 
            replacement=str(conflicting_filters[0].replacement),
            mode=str(conflicting_filters[0].mode)
        )
        
    conflicting_filters_: list[Filter] = [filter_ for filter_ in conflicting_filters[:1] if filter_ is not None]
    if len(conflicting_filters_) > 0:
        return CircularFilterException(
            condition=str(conflicting_filters_[0].condition), 
            replacement=str(conflicting_filters_[0].replacement),
            mode=str(conflicting_filters_[0].mode)
        )


def commit_to_database(condition: str, mode: str, session: SessionProtocol, replacement: str | None = None) -> None | Exception:
    """Registers the filter in the database.

    Args:
        condition (str): condition value from command.
        mode (str): blacklist, replacement or link_remover.
        session (SessionProtocol): sqlalchemy session instance.
        replacement (str | None): replacement value from command if mode is replacement, else None.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        filter_ = Filter(id=str(uuid4()), condition=condition, mode=mode, replacement=replacement)
        session.add(filter_)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseCommitException(exc=e)


def add_filter(command: str | None, chat_id: int, session: SessionProtocol, mode: str) -> str | Exception: 
    """Route to add a filter to the database.

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
    flags: tuple[str, ...] = ("condition", "replacement") if mode == "replacement" else ("condition", )
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    condition: str = args[0]
    replacement: str | None = args[1] if mode == "replacement" else None
    
    # query database
    conflicting_filters: query_return_type | Exception = query_database(condition, mode, session, replacement)
    if isinstance(conflicting_filters, Exception): return conflicting_filters
    
    # make validations
    is_all_valid: None | Exception = validate(conflicting_filters)
    if isinstance(is_all_valid, Exception): return is_all_valid
    
    # commit to database
    res: None | Exception = commit_to_database(condition, mode, session, replacement)
    if isinstance(res, Exception): return res
    
    return "Filter added successfully!"
    
    