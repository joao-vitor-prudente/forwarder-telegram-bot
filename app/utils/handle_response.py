from typing import Any, Callable, Coroutine, TypeAlias

from classes.telethon_protocols import TelegramClientProtocol, MessageProtocol
from classes.fatal_exceptions import FatalException

from app.utils.handle_log import handle_log

send_file_type: TypeAlias = Callable[[str], Coroutine[Any, Any, MessageProtocol]]


async def handle_response(res: Exception | str, client: TelegramClientProtocol, url: str) -> None:
        """Handles response from routes.

        Args:
            res (Exception | str): route function return.
            client (TelegramClientProtocol): Telegram client.
            url (str): url to send the response to.
        """
        
        message = f"Error: {res}" if isinstance(res, Exception) else res
        await client.send_message(url, message)
        
        if not isinstance(res, FatalException): return
        send_file: send_file_type = lambda file: client.send_file(url, file)
        log_res: None |Exception = await handle_log(res, send_file)
        
        if isinstance(log_res, Exception):
            await client.send_message(url, f"Error: {log_res}")