from typing import Callable

from sqlalchemy.exc import SQLAlchemyError

from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import NoFilterFoundException, NotAuthorizedException
from classes.fatal_exceptions import DatabaseCommitException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Filter
    

def query_database(mode: str, session: SessionProtocol) -> list[Filter] | Exception:
    """Queries the database for filter.

    Args:
        mode (str): blacklist, replacement or link_remover.
        session (SessionProtocol): sqlalchemy session instance.
    Returns:
        list[Filter] | Exception: filter from database if any or exception if any.
    """
        
    try:
        filter_: list[Filter] = session.query(Filter).filter(Filter.mode == mode).all()
    except SQLAlchemyError as e:
        return DatabaseCommitException(exc=e)
    
    return filter_


def validate(filter_: list[Filter]) -> list[Filter] | Exception:
    """Validates the filter.

    Args:
        filter_ (Filter): validated filter from database or exception if any.
        
    Returns:
        None | Exception: validated filter if everything went well or exception if validation fails.
    """

    if len(filter_) == 0: return NoFilterFoundException()
    return filter_
    


def format_message(filters: list[Filter]) -> str:
    """Structures filters queried in a message.

    Args:
        filters (list[Filter]): list of filters from database

    Returns:
        str: message to be sent to the user.
    """
    
    format_filter_without_replacement: Callable[[Filter], str] = lambda filter_: f"{filter_.condition}"
    format_filter_with_replacement: Callable[[Filter], str] = lambda filter_: f"{filter_.condition} -> {filter_.replacement}"
    format_filter = format_filter_with_replacement if filters[0].mode == "replacement" else format_filter_without_replacement
    formated_filters: str = "\n".join([format_filter(filter_) for filter_ in filters])
    message: str = f"Filters: \n {formated_filters}"
    return message


def view_filters(chat_id: int, session: SessionProtocol, mode: str) -> str | Exception: 
    """Route to view all filters of a determined mode from database.

    Args:
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
    
    # query database
    filters: list[Filter] | Exception = query_database(mode, session)
    if isinstance(filters, Exception): return filters
    
    # validate filter
    validated_filter: list[Filter] | Exception = validate(filters)
    if isinstance(validated_filter, Exception): return validated_filter
    
    # format message
    message: str = format_message(validated_filter)
    if isinstance(message, Exception): return message
    
    return message