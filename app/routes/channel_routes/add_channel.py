from sqlalchemy.exc import SQLAlchemyError

from uuid import uuid4

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from app.validations.validate_url import validate_url

from classes.validation_exceptions import ChannelAlreadyExistsException, InvalidCommandException, NotAuthorizedException
from classes.fatal_exceptions import DatabaseCommitException, DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel


def query_database(name: str, url: str, session: SessionProtocol) -> None | Exception:
    """Registers the channel in the database.

    Args:
        name (str): name value from command.
        url (str): url value from command.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        Channel | None | Exception: channel from database if any or exception if any.
    """
    
    if not validate_url(url):
        return InvalidCommandException(message="Invalid url.", command=url)
    
    try:
        channel: Channel | None = session.query(Channel).filter(Channel.name == name or Channel.url == url).first()
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)
    
    return channel


def validate(channel: Channel | None) -> None | Exception:
    """Validates the name and url.

    Args:
        channel (Channel | None): channel from database if any.

    Returns:
        None | Exception: None if everything went well or exception if validation fails.
    """
    
    if channel is not None:
        return ChannelAlreadyExistsException(name=str(channel.name), url=str(channel.url))
    


def commit_to_database(name: str, url: str, session: SessionProtocol) -> None | Exception:
    """Registers the channel in the database.

    Args:
        name (str): name value from command.
        url (str): url value from command.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        channel = Channel(id=str(uuid4()), name=name, url=url)
        session.add(channel)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseCommitException(exc=e)


def add_channel(command: str | None, chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to add a channel to the database.

    Args:
        command (str | None): command string from event.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    
    # check if user is authorized
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)
    
    # parse command
    command = command if command is not None else ""
    
    flags: tuple[str, ...] = ("name", "url")
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    name: str = args[0]
    url: str = args[1]
    
    # query database
    channel: Channel | None | Exception = query_database(name, url, session)
    if isinstance(channel, Exception): return channel
    
    # make validations
    is_all_valid: None | Exception = validate(channel)
    if isinstance(is_all_valid, Exception): return is_all_valid
    
    # commit to database
    res: None | Exception = commit_to_database(name, url, session)
    if isinstance(res, Exception): return res
    
    return "Channel added successfully!"
    
    