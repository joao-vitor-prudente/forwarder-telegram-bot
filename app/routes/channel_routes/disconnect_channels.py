# pyright:reportMissingTypeStubs=false

from sqlalchemy.exc import SQLAlchemyError

from typing import Callable, Any, Coroutine, TypeAlias

from app.utils.get_channel_filter_attr import get_channel_filter_attr
from app.utils.remanage_connections import register_event_handler, remove_event_handler

from app.cmd.handle_command import handle_command

from app.auth.is_authorized import is_authorized

from classes.validation_exceptions import ChannelDoesNotExistException, ChannelsNotConnectedException
from classes.validation_exceptions import NotAuthorizedException, ConnectionsNotSyncronizedException
from classes.fatal_exceptions import DatabaseQueryException, DatabaseCommitException, RollBackException
from classes.telethon_protocols import EventBuilderProtocol, EventProtocol, TelegramClientProtocol
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel

handler_type: TypeAlias = Callable[[EventProtocol], Coroutine[Any, Any, None]]


def query_database(input_attr: str, input_value: str, output_attr: str, output_value: str, session: SessionProtocol) -> tuple[Channel | None, Channel | None] | Exception:
    """Queries the input and output channels from database.

    Args:
        input_attr (str): attribute to filter input by.
        input_value (str): value of input attribute.
        output_attr (str): attribute to filter output by.
        output_value (str): value of output attribute.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        tuple[Channel, Channel] | Exception: input and output channels if everything went well or exception if any.
    """
    
    try:
        input_channel: Channel = session.query(Channel).filter(getattr(Channel, input_attr) == input_value).first()
        output_channel: Channel = session.query(Channel).filter(getattr(Channel, output_attr) == output_value).first()
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)

    return input_channel, output_channel


def validate(input_channel: Channel | None, output_channel: Channel | None) -> tuple[Channel, Channel] | Exception:
    """Validates the attribute and value.

    Args:
        input_channel (Channel | None): input channel from database.
        output_channel (Channel | None): output channel from database.
        
    Returns:
        tuple[Channel, Channel] | Exception: validated channels if everything went well or exception if validation fails.
    """
    
    if input_channel is None:
        return ChannelDoesNotExistException(message="There is no channel with the specified input name or url.")
    
    if output_channel is None:
        return ChannelDoesNotExistException(message="There is no channel with the specified output name or url.")
     
    if output_channel not in input_channel.outputs:
        return ChannelsNotConnectedException(input_id=str(input_channel.id), output_id=str(output_channel.id))

    return input_channel, output_channel


def get_event_handler(input_id: str, output_id: str, client: TelegramClientProtocol) -> tuple[handler_type, EventBuilderProtocol] | Exception:
    """Generates the event handler function.

    Args:
        input_id (str): input channel id.
        output_id (str): output channel id.
        client (TelegramClientProtocol): telegram client instance.

    Returns:
        tuple[handler_type, EventBuilderProtocol] | Exception: 
            event handler function associated with connection between input and output and its event or exception if any.
    """
    
    handler = [
        (handler, event) for handler, event in client.list_event_handlers() 
        if handler.__name__.startswith("connection_handler") 
        and input_id in handler.__name__ 
        and output_id in handler.__name__
        and handler.__name__.find(input_id) < handler.__name__.find(output_id)
    ]
    if len(handler) == 0:
        return ConnectionsNotSyncronizedException(input_id=input_id, output_id=output_id)
    
    return handler[0]
    

def commit_to_database(session: SessionProtocol, input_channel: Channel, output_channel: Channel) -> None | Exception:
    """Commits the changes to database.

    Args:
        session (Session): sqlalchemy session instance.
        input_channel (Channel): input channel instance.
        output_channel (Channel): output channel instance.
        
    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        input_channel.outputs.remove(output_channel)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        return DatabaseCommitException(exc=e)


def disconnect_channels(command: str | None, chat_id: int, session: SessionProtocol, client: TelegramClientProtocol) -> str | Exception: 
    """Route to connect a channel to another in a relationship of input-output in the database.

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
    
    flags: tuple[str, ...] = ("input", "output")
    args: tuple[str, ...] | Exception = handle_command(command, flags)
    if isinstance(args, Exception): return args
    
    input_value: str = args[0]
    input_attr: str = get_channel_filter_attr(input_value)
    output_value: str = args[1]
    output_attr: str = get_channel_filter_attr(output_value)
    
    # query database
    channels: tuple[Channel | None, Channel | None] | Exception = query_database(input_attr, input_value, output_attr, output_value, session)
    if isinstance(channels, Exception): return channels
    input_channel, output_channel = channels
        
    # make validations
    validated_channels: tuple[Channel, Channel] | Exception = validate(input_channel, output_channel)
    if isinstance(validated_channels, Exception): return validated_channels
    validated_input_channel, validated_output_channel = validated_channels
    
    # get event handler
    handler_event: tuple[handler_type, EventBuilderProtocol] | Exception = get_event_handler(
        str(validated_input_channel.id), 
        str(validated_output_channel.id), 
        client
    )
    if isinstance(handler_event, Exception): return handler_event
    handler, event = handler_event
    
    # register event handler
    register_res: None | Exception = remove_event_handler(handler, event, client)
    if isinstance(register_res, Exception): return register_res
    
    # commit to database
    commit_res: None | Exception = commit_to_database(session, input_channel, output_channel)
    
    # if commit fails
    if isinstance(commit_res, Exception): 
        rollback_res: None | Exception = register_event_handler(handler, event, client)
        
        # if roll back fails
        if isinstance(rollback_res, Exception):
            return RollBackException(input_id=str(validated_input_channel.id), output_id=str(validated_output_channel.id), exc=rollback_res, prev_exc=commit_res)
        
        # if roll back succeeds
        return commit_res
    
    # if commit succeeds    
    return "Channels connected successfully!"


