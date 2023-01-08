from sqlalchemy.exc import SQLAlchemyError

from db.schema import Admin

from classes.fatal_exceptions import DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

def is_authorized(chat_id: int, session: SessionProtocol) -> bool | Exception:
    """Check if chat is authorized by any admin.

    Args:
        chat_id (int): integer id of the chat from which the message that triggered the register came from.
        SessionProtocol (Session): sqlalchemy session object.

    Returns:
        bool | Exception: True if chat is authorized, False otherwise and exception in case of database error.
    """
    
    try:
        admins: list[Admin] = session.query(Admin).all()
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)
    
    chat_ids_in_db: list[int] = [admin.authorized_chat_id for admin in admins]  # type: ignore    
    if chat_id not in chat_ids_in_db:
        return False

    return True
