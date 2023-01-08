# pyright:reportMissingTypeStubs=false

from telethon.sync import TelegramClient

from asyncio import AbstractEventLoop

from classes.telethon_protocols import TelegramClientProtocol


def create_client(name: str, api_id: int, api_hash: str, loop: AbstractEventLoop) -> TelegramClientProtocol:
    """Creates a TelegramClient instance.

    Args:
        name (str): name of the client.
        api_id (int): api id of the client.
        api_hash (str): api hash of the client.
        loop (AbstractEventLoop): asyncio loop.

    Returns:
        TelegramClientProtocol: TelegramClient instance.
    """
    
    return TelegramClient(name, api_id, api_hash, loop=loop)  # type: ignore