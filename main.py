# pyright:reportMissingTypeStubs=false
# pyright:reportUnusedFunction=false

from telethon.sync import events

from asyncio import new_event_loop, set_event_loop, AbstractEventLoop

from typing import TypeAlias, Callable, Coroutine, Any

from functools import partial

from db.init_db import init_db

from classes.telethon_protocols import EventProtocol, TelegramClientProtocol
from classes.sqlalchemy_protocols import EngineProtocol, SessionProtocol

from app.utils.create_client import create_client
from app.utils.get_client_data import get_client_data
from app.utils.remanage_connections import remanage_connections
from app.utils.handle_response import handle_response

from app.routes.utility_routes.auth import auth as auth_route
from app.routes.utility_routes.help_ import help_ as help_route
from app.routes.utility_routes.sync import sync as sync_route

from app.routes.channel_routes.add_channel import add_channel as add_channel_route
from app.routes.channel_routes.remove_channel import remove_channel as remove_channel_route
from app.routes.channel_routes.view_channel import view_channel as view_channel_route
from app.routes.channel_routes.view_all_channels import view_all_channels as view_all_channels_route
from app.routes.channel_routes.view_connections import view_connections as view_connections_route
from app.routes.channel_routes.connect_channels import connect_channels as connect_channels_route
from app.routes.channel_routes.disconnect_channels import disconnect_channels as disconnect_channels_route

from app.routes.filter_routes.add_filter import add_filter as add_filter_route
from app.routes.filter_routes.remove_filter import remove_filter as remove_filter_route
from app.routes.filter_routes.view_filters import view_filters as view_filters_route

handler_type: TypeAlias = Callable[[EventProtocol], Coroutine[Any, Any, None]]
response_handler_type: TypeAlias = Callable[[str | Exception], Coroutine[Any, Any, None]]
    
# route function names starting with connection_handler are restricted to only be used as a connection between two telegram channels


def main(env: str) -> None | Exception:
    """Main function of the client.

    Args:
        env (str): environment to load [dev or prod].

    Returns:
        None | Exception: None if everything went well or exception if any.
    """
    
    # start loop
    loop: AbstractEventLoop = new_event_loop()
    set_event_loop(loop)
    
    # start database
    db: tuple[EngineProtocol, SessionProtocol] | Exception = init_db("sqlite:///database.db")
    if isinstance (db, Exception): return db
    session: SessionProtocol = db[1]
    
    print("Database connected!")
    
    # start client
    client_data = get_client_data(env)
    if isinstance(client_data, Exception): return client_data
    client: TelegramClientProtocol = create_client("session", client_data.api_id, client_data.api_hash, loop)
    client.start(lambda: client_data.phone)
    
    print("Client started!")
    
    # manage initial connections
    res: str | Exception = remanage_connections(session, client)
    if isinstance(res, Exception): return res
    
    print("Initial connections managed!")
    
    response_handler: response_handler_type = partial(handle_response, client=client, url=client_data.url)
    
    # utility routes
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/help"))
    async def help_(event: EventProtocol) -> None:
        """Utility:\n\n/help"""
        message: str = help_route(main)
        await client.send_message(client_data.url, message)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/auth"))
    async def auth(event: EventProtocol) -> None:
        """/auth --login=<admin_username> --password=<admin_password>"""
        res: str | Exception = auth_route(event.message.message, event.chat_id, session)
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/sync"))
    async def sync(event: EventProtocol) -> None:
        """/sync"""
        res1: str | Exception = sync_route(event.chat_id, session)
        # if routing succeeds remanage connections
        if isinstance(res1, str):
            res2: str | Exception = remanage_connections(session, client) 
            # if both succeed combine success message
            if isinstance(res2, str): res = f"{res1}\n{res2}"
            # if remanage connections fails, send only remanage connections error
            else: res = res2
        # if routing fails send only auth error
        else: res = res1
        
        await response_handler(res)
        
    # channel managing routes
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/add_channel"))
    async def add_channel(event: EventProtocol) -> None:
        """Managing Channels:\n\n/add_channel --name=<channel_name> --url=<channel_url>"""
        res: str | Exception = add_channel_route(event.message.message, event.chat_id, session)
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/remove_channel"))
    async def remove_channel(event: EventProtocol) -> None:
        """/remove_channel --filter=<channel_name_or_url>"""
        res: str | Exception = remove_channel_route(event.message.message, event.chat_id, session)
        res: str | Exception = remanage_connections(session, client)
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_channel"))
    async def view_channel(event: EventProtocol) -> None:
        """/view_channel --filter=<channel_name_or_url>"""
        res: str | Exception = view_channel_route(event.message.message, event.chat_id, session)
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_all_channel"))
    async def view_all_channel(event: EventProtocol) -> None:
        """/view_all_channel"""
        res: str | Exception = view_all_channels_route(event.chat_id, session)
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_connections"))
    async def view_connections(event: EventProtocol) -> None:
        """/view_connections"""
        res: str | Exception = view_connections_route(event.chat_id, session)
        await response_handler(res)
    
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/connect_channels"))
    async def connect_channels(event: EventProtocol) -> None:
        """/connect_channels --input=<input_channel_name_or_url> --output=<output_channel_name_or_url>"""
        res: str | Exception = connect_channels_route(event.message.message, event.chat_id, session, client)
        await response_handler(res)
            
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/disconnect_channels"))
    async def disconnect_channels(event: EventProtocol) -> None:
        """/disconnect_channels --input=<input_channel_name_or_url> --output=<output_channel_name_or_url>"""
        res: str | Exception = disconnect_channels_route(event.message.message, event.chat_id, session, client)
        await response_handler(res)
    
    # filter managing routes
    # filter add routes
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/add_to_blacklist"))
    async def add_to_blacklist(event: EventProtocol) -> None:
        """Managing Filters:\n\n/add_to_blacklist --condition=<condition>"""
        res: str | Exception = add_filter_route(event.message.message, event.chat_id, session, "blacklist")
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/add_replacement"))
    async def add_replacement(event: EventProtocol) -> None:
        """/add_replacement --condition=<condition> --replacement=<replacement>"""
        res: str | Exception = add_filter_route(event.message.message, event.chat_id, session, "replacement")
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/add_link_remover"))
    async def add_link_remover(event: EventProtocol) -> None:
        """/add_link_remover --condition=<condition>"""
        res: str | Exception = add_filter_route(event.message.message, event.chat_id, session, "link_remover")
        await response_handler(res)
    
    # filter remove routes
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/remove_from_blacklist"))
    async def remove_from_blacklist(event: EventProtocol) -> None:
        """/remove_from_blacklist --condition=<condition>"""
        res: str | Exception = remove_filter_route(event.message.message, event.chat_id, session, "blacklist")
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/remove_replacement"))
    async def remove_replacement(event: EventProtocol) -> None:
        """/remove_replacement --condition=<condition>"""
        res: str | Exception = remove_filter_route(event.message.message, event.chat_id, session, "replacement")
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/remove_link_remover"))
    async def remove_link_remover(event: EventProtocol) -> None:
        """/remove_link_remover --condition=<condition>"""
        res: str | Exception = remove_filter_route(event.message.message, event.chat_id, session, "link_remover")
        await response_handler(res)
        
    # filter view routes
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_blacklist"))
    async def view_blacklist(event: EventProtocol) -> None:
        """/view_blacklist"""
        res: str | Exception = view_filters_route(event.chat_id, session, "blacklist")
        await response_handler(res)
        
    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_replacements"))
    async def view_replacements(event: EventProtocol) -> None:
        """/view_replacements"""
        res: str | Exception = view_filters_route(event.chat_id, session, "replacement")
        await response_handler(res)

    @client.on(events.NewMessage(chats=[client_data.url], pattern="^/view_link_removers"))
    async def view_link_removers(event: EventProtocol) -> None:
        """/view_link_removers"""
        res: str | Exception = view_filters_route(event.chat_id, session, "link_remover")
        await response_handler(res)

    print("Server running!")
    client.run_until_disconnected()
    
    
if __name__ == "__main__":
    x = main("dev")
    if isinstance(x, Exception): raise x