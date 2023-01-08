from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import  NotAuthorizedException
from classes.sqlalchemy_protocols import SessionProtocol


def sync(chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to sync telegram event handlers to database.

    Args: 
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)

    return "Connections syncronized."