from typing import Protocol, Any


class EngineProtocol(Protocol):
    def __init__(self: "EngineProtocol", pool: Any, dialect: Any, url: str) -> None:
        ...


class QueryProtocol(Protocol):
    def __init__(self: "QueryProtocol", *entities: Any) -> None:
        ...
    
    def filter(self: "QueryProtocol", *criterion: Any) -> "QueryProtocol":
        ...
    
    def first(self: "QueryProtocol") -> Any:
        ...
        
    def all(self: "QueryProtocol") -> list[Any]:
        ...


class SessionProtocol(Protocol):
    def __init__(self: "SessionProtocol", bind: EngineProtocol) -> None:
        ...
        
    def commit(self: "SessionProtocol"):
        ...
        
    def rollback(self: "SessionProtocol"):
        ...
        
    def query(self: "SessionProtocol", *entities: Any, **kwargs: Any) -> QueryProtocol:
        ...
        
    def add(self: "SessionProtocol", instance: Any):
        ...
        
    def delete(self: "SessionProtocol", instance: Any):
        ... 
        