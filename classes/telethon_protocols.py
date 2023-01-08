from typing import Iterable, MutableSequence, Protocol, Any, Coroutine, Callable, runtime_checkable, Sequence
from datetime import datetime


@runtime_checkable
class MessageProtocol(Protocol):
    def __init__(self: "MessageProtocol", id: int, peer_id: Any, date: datetime, message: str) -> None:
        self.message: str
        ...


@runtime_checkable
class EventBuilderProtocol(Protocol):
    def __init__(
        self: "EventBuilderProtocol", 
        chats: Sequence[Any] | MutableSequence[Any] | None, *, 
        blacklist_chats: bool, 
        func: Callable[["EventBuilderProtocol"], Any | None]
    ) -> None:
        self.chats: Iterable[Any] | None
        self.blacklist_chats: bool
        self.func: Callable[["EventBuilderProtocol"], Any] | None
        ...


@runtime_checkable 
class EventProtocol(Protocol):
    def __init__(self: "EventProtocol", message: MessageProtocol) -> None:
        self.message: MessageProtocol
        self.chat_id: int
        ...
        

@runtime_checkable
class TelegramClientProtocol(Protocol):
    
    def __init__(self: "TelegramClientProtocol", session: str, api_id: int, api_hash: str) -> None:
        self.session: str
        self.api_id: int
        self.api_hash: str
        ...
    
    def start(self: "TelegramClientProtocol", phone: Callable[[], str]) -> "TelegramClientProtocol":
        ...
        
    def run_until_disconnected(self) -> Coroutine[Any, Any, Any | None] | Any | None:
        ...
        
    def add_event_handler(self: "TelegramClientProtocol", callback: Callable[[Any], Any], event: Any):
        ...
    
    def remove_event_handler(self: "TelegramClientProtocol", callback: Callable[[Any], Any], event: Any = None) -> int:
        ...
    
    def list_event_handlers(self) -> Sequence[tuple[Callable[[Any], Any], Any]]:
        ...
        
    def on(self: 'TelegramClientProtocol', event: EventBuilderProtocol) -> Callable[[Any], Callable[[Any], Callable[[Any], Any]]]:
        ...
    
    async def send_message(self: "TelegramClientProtocol", entity: Any, message: Any) -> MessageProtocol:
        ...
        
    async def send_file(self: "TelegramClientProtocol", entity: Any, file: Any) -> MessageProtocol:
        ...
        