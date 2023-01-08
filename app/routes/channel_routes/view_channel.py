from typing import Callable

from sqlalchemy.exc import SQLAlchemyError

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from app.utils.get_channel_filter_attr import get_channel_filter_attr

from classes.validation_exceptions import ChannelDoesNotExistException, NotAuthorizedException, NoChannelFoundException
from classes.fatal_exceptions import DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel


def query_database(attr: str, value: str, session: SessionProtocol) -> Channel | Exception:
    """Reads a channel from the database.

    Args:
        attr (str): attribute to filter by.
        value (str): value of attribute.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        list[Channel] | Exception: list of channels from database if everything went well or exception if any.
    """
    
    try:
        channel: Channel = session.query(Channel).filter(getattr(Channel, attr) == value).first()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseQueryException(exc=e)
    if channel is None:
        return NoChannelFoundException(attr=attr, value=value)
    
    return channel


def validate(channel: Channel | None) -> Channel | Exception:
    """Validates the attribute and value.

    Args:
        channel (Channel | None): channel from database if any.

    Returns:
        Channel | Exception: validated channel if everything went well or exception if validation fails.
    """
    
    if channel is None: return ChannelDoesNotExistException()
    return channel

    
def format_message(channel: Channel) -> str:
    """Structures channels queried in a message.

    Args:
        channels (Channel): lchannel from database

    Returns:
        str: message to be sent to the user.
    """
    
    format_channel: Callable[[Channel], str] = lambda channel: f"{channel.name} - {channel.url}"
    channel_info: str = format_channel(channel)
    channel_inputs: str = "\n".join([format_channel(input_) for input_ in channel.inputs])
    channel_outputs: str = "\n".join([format_channel(output) for output in channel.outputs])
    message: str = f"Channel info:\n{channel_info}\nInputs: \n{channel_inputs} \nOutputs:\n{channel_outputs}"
    return message


def view_channel(command: str | None, chat_id: int, session: SessionProtocol) -> str | Exception: 
    """Route to read a channel from the database.

    Args:
        command (str | None): command string from event.
        chat_id (int): chat id from event.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        str | Exception: ok message or exception if any
    """
    is_auth: bool | Exception =  is_authorized(chat_id, session)
    if isinstance(is_auth, Exception): return is_auth
    if not is_auth: return NotAuthorizedException(chat_id=chat_id)
    
    command = command if command is not None else ""
    
    flags: tuple[str, ...] = ("filter", )
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    value: str = args[0]
    attr: str = get_channel_filter_attr(value)
    
    channel: Channel | Exception = query_database(attr, value, session)
    if isinstance(channel, Exception): return channel
    
    validated_channel: None | Exception = validate(channel)
    if isinstance(validated_channel, Exception): return validated_channel
    
    message: str = format_message(validated_channel)
    
    return message
