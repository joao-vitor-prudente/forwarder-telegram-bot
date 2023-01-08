from sqlalchemy.exc import SQLAlchemyError

from app.cmd.handle_command import handle_command

from app.auth.authorize import authorize

from classes.validation_exceptions import AuthorizationException
from classes.fatal_exceptions import DatabaseCommitException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Admin


def validator(login: str, password: str, session: SessionProtocol) -> None | Exception:
    """Validates the login and password.

    Args:
        login (str): login value from command.
        password (str): password value from command.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if validation fails.
    """
    
    res: bool | Exception = authorize(login, password, session)
    if isinstance(res, Exception): return res
    if not res: return AuthorizationException(login=login, password=password)


def registerer(login: str, password: str, chat_id: int, session: SessionProtocol) -> None | Exception:
    """Registers the channel in the database.

    Args:
        login (str): login value from command.
        password (str): password value from command.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        admin: Admin = session.query(Admin).filter(Admin.login == login).first()  # type: ignore
        setattr(admin, "authorized_chat_id", chat_id)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseCommitException(exc=e)


def auth(command: str | None, chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to authorize a chat to the database.

    Args:
        command (str | None): command string from event.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    
    command = command if command is not None else ""
    
    flags: tuple[str, ...] = ("login", "password")
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    login: str = args[0]
    password: str = args[1]
    
    is_all_valid: None | Exception = validator(login, password, session)
    if isinstance(is_all_valid, Exception): return is_all_valid
    
    res: None | Exception = registerer(login, password, chat_id, session)
    if isinstance(res, Exception): return res
    
    return "Chat authorized successfully!"
    