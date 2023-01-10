from abc import ABC, abstractmethod

from typing import Any, Callable, Coroutine, TypeAlias

from classes.telethon_protocols import EventProtocol

handler_type: TypeAlias = Callable[[EventProtocol], Coroutine[Any, Any, None]]


# base exceptions
class FatalException(ABC, Exception):
    @abstractmethod
    def __init__(self: "FatalException", exc: Exception, message: str):
        super().__init__(message)
        self.exc = exc
        self.message = message

    @abstractmethod
    def __repr__(self: "FatalException") -> str:
        pass


# database exceptions
class ConnectionException(FatalException):
    def __init__(
        self: "ConnectionException", 
        exc: Exception, 
        message: str = "Error while connecting to database.", 
        connection_str: str | None = None
    ):
        super().__init__(exc, message)
        self.connection_str = connection_str
    
    def __repr__(self: "ConnectionException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "connection_str": self.connection_str, 
            "exc": str(self.exc)
        })
        
    
class DatabaseCommitException(FatalException):
    def __init__(
        self: "DatabaseCommitException", 
        exc: Exception, 
        message: str = "Error while committing changes to database."
    ):
        super().__init__(exc, message)
    
    def __repr__(self: "DatabaseCommitException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "exc": str(self.exc)
        })
        
        
class DatabaseQueryException(FatalException):
    def __init__(
        self: "DatabaseQueryException", 
        exc: Exception, 
        message: str = "Error while querying database."
    ):
        super().__init__(exc, message)
        
    def __repr__(self: "DatabaseQueryException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "exc": str(self.exc
        )})
        
        
class RollBackException(FatalException):
    def __init__(
        self: "RollBackException", 
        exc: Exception, 
        prev_exc: Exception,
        message: str = "Could not complete operation.\nCould not rollback changes to database.\nPlease contact the developer.", 
        input_id: str | None = None, 
        output_id: str | None = None
    ):
        super().__init__(exc, message)
        self.input_id = input_id
        self.output_id = output_id
        self.prev_exc = prev_exc
    
    def __repr__(self: "RollBackException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "input_id": self.input_id, 
            "output_id": self.output_id, 
            "exc": str(self.exc), 
            "prev_exc": str(self.prev_exc)
        })
        

# telegram connection exceptions
class CannotRemoveEventHandlerException(FatalException):
    def __init__(
        self: "CannotRemoveEventHandlerException", 
        exc: Exception, 
        message: str = "Could not remove event handler.", 
        handler: handler_type | None = None, 
        event: Any | None = None
    ):
        super().__init__(exc, message)
        self.handler = handler
        self.event = event
        
    def __repr__(self: "CannotRemoveEventHandlerException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "handler": self.handler, 
            "event": self.event, 
            "exc": str(self.exc)
        })
        
        
class CannotAddEventHandlerException(FatalException):
    def __init__(
        self: "CannotAddEventHandlerException", 
        exc: Exception, 
        message: str = "Could not add event handler.", 
        handler: handler_type | None = None, 
        event: Any | None = None
    ):
        super().__init__(exc, message)
        self.handler = handler
        self.event = event
    
    def __repr__(self: "CannotAddEventHandlerException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "handler": self.handler, 
            "event": self.event, 
            "exc": str(self.exc)
        })
        
        
# logging exceptions
class LogException(FatalException):
    def __init__(
        self: "LogException", 
        exc: Exception, 
        message: str = "Could not create log file."
    ):
        super().__init__(exc, message)
        
    def __repr__(self: "LogException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "exc": self.exc
        })