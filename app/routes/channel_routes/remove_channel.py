# pyright:reportMissingTypeStubs=false

from sqlalchemy.exc import SQLAlchemyError

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from app.utils.get_channel_filter_attr import get_channel_filter_attr

from classes.validation_exceptions import ChannelDoesNotExistException, NotAuthorizedException
from classes.fatal_exceptions import DatabaseCommitException, DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel


def query_database(attr: str, value: str, session: SessionProtocol) -> Channel | None | Exception:
    """Deletes the channel from the database.

    Args:
        attr (str): attribute to filter by.
        value (str): value of attribute.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        Channel | Exception: channel instance if everything went well or exception if any.
    """
    
    try:
        channel: Channel = session.query(Channel).filter(getattr(Channel, attr) == value).first()  # type: ignore
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)
    
    return channel


def validate(channel: Channel | None) -> Channel | Exception:
    """Validates the attribute and value.

    Args:
        channel (Channel | None): channel from database if any.

    Returns:
        Channel- | Exception: channel if everything went well or exception if validation fails.
    """
    
    if channel is None: return ChannelDoesNotExistException()
    return channel


def commit_to_database(channel: Channel, session: SessionProtocol) -> None | Exception:
    """Commits the channel to the database.

    Args:
        channel (Channel): channel instance.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        channel.inputs.clear()
        channel.outputs.clear()
        session.delete(channel)
        session.commit()
    except SQLAlchemyError as e:
        return DatabaseCommitException(exc=e)
    

def remove_channel(command: str | None, chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to remove a channel to the database.

    Args:
        command (str | None): command string from event.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.
        client (TelegramClientProtocol): telegram client instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    
    # check if user is authorized
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)
    
    # parse command
    command = command if command is not None else ""
    
    flags: tuple[str, ...] = ("filter", )
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    value: str = args[0]
    attr: str = get_channel_filter_attr(value)
    
    # query database
    channel: Channel | None | Exception = query_database(attr, value, session)
    if isinstance(channel, Exception): return channel
    
    # make validations
    validated_channel: Channel | Exception = validate(channel)
    if isinstance(validated_channel, Exception): return validated_channel

    # commiting to database
    res: None | Exception = commit_to_database(validated_channel, session)
    if isinstance(res, Exception): return res
    
    return "Channel removed successfully!"