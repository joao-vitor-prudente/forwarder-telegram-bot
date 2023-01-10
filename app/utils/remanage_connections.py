# pyright:reportMissingTypeStubs=false

from typing import Any, Callable, Coroutine, TypeAlias

from sqlalchemy.exc import SQLAlchemyError

from telethon.sync import events

from app.utils.treat_message import treat_message

from classes.telethon_protocols import EventBuilderProtocol, EventProtocol, TelegramClientProtocol
from classes.fatal_exceptions import CannotRemoveEventHandlerException, CannotAddEventHandlerException, DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

from db.schema import Channel, Filter


handler_type: TypeAlias = Callable[[EventProtocol], Coroutine[Any, Any, None]]


def remove_event_handler(handler: handler_type, event:  EventBuilderProtocol, client: TelegramClientProtocol) -> None | Exception:
    """Remove event handler from client.

    Args:
        handler (handler_type): event callback function.
        event (EventBuilderProtocol): event instance.
        client (TelegramClientProtocol): telegram client instance.
    
    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        client.remove_event_handler(handler, event)
    except Exception as e:
        CannotRemoveEventHandlerException(handler=handler, event=event, exc=e)


def query_channels(session: SessionProtocol) -> list[Channel] | Exception:
    """Query all channels from database.

    Args:
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        list[Channel] | Exception: list of channels if everything went well or exception if any.
    """
    
    try:
        channels: list[Channel] = session.query(Channel).all()
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)

    return channels


def get_channel_pairs(channels: list[Channel]) -> list[tuple[Channel, Channel]]:
    """Get all channel pairs of input output from a list of channels.

    Args:
        channels (list[Channel]): list of channels.

    Returns:
        list[tuple[Channel, Channel]]: list of input output pairs.
    """
    
    # filter list of channels to only include channels with outputs
    channels_with_outputs: list[Channel] = [channel for channel in channels if len(channel.outputs) > 0]
    # create a list of tuples of the channel and each of its outputs for each channel
    channel_pairs_separated: list[list[tuple[Channel, Channel]]] = [
        [(input_, output) for output in input_.outputs] 
        for input_ in channels_with_outputs
    ]
    # reduce list of lists of tuples to a list of tuples
    channel_pairs: list[tuple[Channel, Channel]] = sum(channel_pairs_separated, [])
    return channel_pairs



def get_event_handler(input_channel: Channel, output_channel: Channel, client: TelegramClientProtocol, session: SessionProtocol) -> tuple[handler_type, events.NewMessage]:
    """Get event handler for a channel pair.

    Args:
        input_channel (Channel): input channel instance.
        output_channel (Channel): output channel instance.
        client (TelegramClientProtocol): telegram client instance.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        tuple[handler_type, events.NewMessage]: event handler and event instance.
    """
    
    async def handler(event: EventProtocol):
        filters: list[Filter] = session.query(Filter).all()
        treated_message: None | str = treat_message(event.message.message, filters)
        if treated_message is None: return
        await client.send_message(output_channel.url, treated_message)
    
    # save input and output urls in the handler's name to be able to identify it later
    handler.__name__ = f"connection_handler - ({input_channel.id}) -> ({output_channel.id})"
    return handler, events.NewMessage(chats=[input_channel.url])
  
    
def register_event_handler(handler: handler_type, event: EventBuilderProtocol, client: TelegramClientProtocol) -> None | Exception:
    """Registers event handler to client.

    Args:
        handler (handler_type): event callback function.
        event (EventBuilderProtocol): event instance.
        client (TelegramClientProtocol): telegram client instance.
    
    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    try:
        client.add_event_handler(handler, event)
    except Exception as e:
        CannotAddEventHandlerException(handler=handler, event=event, exc=e)  



def remanage_connections(session: SessionProtocol, client: TelegramClientProtocol) -> str | Exception:
    """Remove all event handlers from client and add new ones.

    Args:
        session (SessionProtocol): sqlalchemy session instance.
        client (TelegramClientProtocol): telegram client instance.

    Returns:
        str | Exception: success message or exception if any.
    """
    
    res: list[Exception | None] = [
        remove_event_handler(handler, event, client) 
        for handler, event in client.list_event_handlers() 
        if handler.__name__.startswith("connection_handler")
    ]
    exceptions: list[Exception] = [e for e in res if isinstance(e, Exception)]
    if len(exceptions) > 0: return exceptions[0]
        
    channels: list[Channel] | Exception = query_channels(session)
    if isinstance(channels, Exception): return channels
    
    channel_pairs: list[tuple[Channel, Channel]] = get_channel_pairs(channels)
    
    event_handlers: list[tuple[handler_type, events.NewMessage]] = [
        get_event_handler(input_channel, output_channel, client, session) 
        for input_channel, output_channel in channel_pairs
    ]
    
    res: list[Exception | None] = [
        register_event_handler(handler, event, client) 
        for handler, event in event_handlers
    ]
    exceptions: list[Exception] = [e for e in res if isinstance(e, Exception)]
    if len(exceptions) > 0: return exceptions[0]
    
    return "Telegram connections remanaged successfully!"
