from typing import Callable

from sqlalchemy.exc import SQLAlchemyError

from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import NotAuthorizedException, NoChannelFoundException
from classes.fatal_exceptions import DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel


def query_database(session: SessionProtocol) -> list[Channel] | Exception:
    """Reads all channels from the database.

    Args:

        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        channels: list[Channel] = session.query(Channel).all()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseQueryException(exc=e)
    
    if len(channels) == 0:
        return NoChannelFoundException(all=True)
    return channels


def format_message(channels: list[Channel]) -> str:
    """Structures channels queried in a message.

    Args:
        channels (list[Channel]): list of channels from database

    Returns:
        str: message to be sent to the user.
    """
    
    format_channel: Callable[[Channel], str] = lambda channel: f"{channel.name} - {channel.url}"
    formated_channels: str = "\n".join([format_channel(channel) for channel in channels])
    message: str = f"Channels: \n {formated_channels}"
    return message


def view_all_channels(chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to read all channels from the database.

    Args: 
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)
    
    channels: list[Channel] | Exception = query_database(session)
    if isinstance(channels, Exception): return channels
    
    message: str = format_message(channels)
    
    return message
