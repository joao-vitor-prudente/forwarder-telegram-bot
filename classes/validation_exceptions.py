from typing import Any

from abc import ABC, abstractmethod


# base exceptions
class ValidationException(ABC, Exception):
    @abstractmethod
    def __init__(self: "ValidationException", message: str):
        super().__init__(message)
        self.message = message
    
    @abstractmethod
    def __repr__(self: "ValidationException") -> str:
        pass
    

# environment exceptions
class InvalidEnvironmentException(ValidationException):
    def __init__(
        self: "InvalidEnvironmentException", 
        message: str = "Invalid environmt. Try dev or prod", 
        env: str | None = None
    ):
        self.message = message
        self.env = env
    
    def __repr__(self: "InvalidEnvironmentException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "env": self.env
        })


class EnvironmentVariableException(ValidationException):
    def __init__(
        self: "EnvironmentVariableException", 
        message: str = "Environment variable not found.", 
        var_name: str | None = None
    ):
        self.message = message
        self.var_name = var_name
    
    def __repr__(self: "EnvironmentVariableException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "var_name": self.var_name
        })
        

# authorization exceptions
class NotAuthorizedException(ValidationException):
    def __init__(
        self: "NotAuthorizedException", 
        message: str = "You are not authorized to use this command.", 
        chat_id: int | None = None
    ):
        super().__init__(message)
        self.chat_id = chat_id
    
    def __repr__(self: "NotAuthorizedException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "chat_id": self.chat_id
        })
        

class AuthorizationException(ValidationException):
    def __init__(
        self: "AuthorizationException", 
        message: str = "Invalid login or password.", 
        login: str | None = None, 
        password: str | None = None
    ):
        super().__init__(message)
        self.login = login
        self.password = password
    
    def __repr__(self: "AuthorizationException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "login": self.login, 
            "password": self.password
        })
    

# command parsing exceptions
class InvalidCommandException(ValidationException):
    def __init__(
        self: "InvalidCommandException", 
        message: str = "Mal-formed command.", 
        command: str | None = None
    ):
        super().__init__(message)
        self.command = command

    def __repr__(self: "InvalidCommandException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "command": self.command
        })


# channel validation exceptions
class ChannelAlreadyExistsException(ValidationException):
    def __init__(
        self: "ChannelAlreadyExistsException", 
        message: str = "A channel with this name or url already exists", 
        name: str | None = None, 
        url: str | None = None
    ):
        super().__init__(message)
        self.name = name
        self.url = url
        
    def __repr__(self: "ChannelAlreadyExistsException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "name": self.name, 
            "url": self.url
        })


class ChannelDoesNotExistException(ValidationException):
    def __init__(
        self: "ChannelDoesNotExistException", 
        message: str = "There is no channel with the specified name or url.", 
    ):
        super().__init__(message)
        
    def __repr__(self: "ChannelDoesNotExistException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
        })
        
    
class ChannelsAlreadyConnectedException(ValidationException):
    def __init__(
        self: "ChannelsAlreadyConnectedException", 
        message: str = "The specified channels are already connected.", 
        input_id: str | None = None, 
        output_id: str | None = None, 
    ):
        super().__init__(message)
        self.input_id = input_id
        self.output_id = output_id
    
    def __repr__(self: "ChannelsAlreadyConnectedException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "input_attr": self.input_id, 
            "input_value": self.output_id, 
        })
        

class ChannelsNotConnectedException(ValidationException):
    def __init__(
        self: "ChannelsNotConnectedException", 
        message: str = "The specified channels are not connected.", 
        input_id: str | None = None, 
        output_id: str | None = None, 
    ):
        super().__init__(message)
        self.input_id = input_id
        self.output_id = output_id
    
    def __repr__(self: "ChannelsNotConnectedException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "input_attr": self.input_id, 
            "input_value": self.output_id, 
        })


class ChannelLoopException(ValidationException):
    def __init__(
        self: "ChannelLoopException", 
        message: str = "Connectiong input channel to output channel generates a loop.", 
        input_id: str | None = None, 
        output_id: str | None = None, 
        loop: tuple[Any, ...] | None = None
    ):
        super().__init__(message)
        self.input_id = input_id
        self.output_id = output_id
        self.loop = loop
    
    def __repr__(self: "ChannelLoopException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "input_attr": self.input_id, 
            "input_value": self.output_id,
            "loop": str(self.loop)
        })


class SameInputAndOutputException(ValidationException):
    def __init__(
        self: "SameInputAndOutputException", 
        message: str = "Input and output channels are the same.", 
        input_id: str | None = None, 
        output_id: str | None = None, 
    ):
        super().__init__(message)
        self.input_id = input_id
        self.output_id = output_id
        
    def __repr__(self: "SameInputAndOutputException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "input_id": self.input_id, 
            "output_id": self.output_id, 
        })
        
        
class NoChannelFoundException(ValidationException):
    def __init__(
        self: "NoChannelFoundException",
        message: str = "No channel found for this query.",
        attr: str | None = None,
        value: str | None = None,
        all: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.attr = attr
        self.value = value
        self.all = all
    
    def __repr__(self: "NoChannelFoundException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "attr": self.attr, 
            "value": self.value, 
            "all": self.all, 
        })
        

# filter validation exceptions
class FilterAlreadyExistsException(ValidationException):
    def __init__(
        self: "FilterAlreadyExistsException", 
        message: str = "A filter with this condition already exists", 
        condition: str | None = None, 
        replacement: str | None = None,
        mode: str | None = None
    ):
        super().__init__(message)
        self.condition = condition
        self.replacement = replacement
        self.mode = mode
        
    def __repr__(self: "FilterAlreadyExistsException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "condition": self.condition, 
            "replacement": self.replacement,
            "mode": self.mode
        })


class CircularFilterException(ValidationException):
    def __init__(
        self: "CircularFilterException", 
        message: str = "The specified filter replacement is the condition for another existing filter.", 
        condition: str | None = None, 
        replacement: str | None = None,
        mode: str | None = None
    ):
        super().__init__(message)
        self.condition = condition
        self.replacement = replacement
        self.mode = mode
        
    def __repr__(self: "CircularFilterException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "condition": self.condition, 
            "replacement": self.replacement,
            "mode": self.mode
        })
        

class FilterDoesNotExistException(ValidationException):
    def __init__(
        self: "FilterDoesNotExistException", 
        message: str = "There is no filter with the specified condition.", 
    ):
        super().__init__(message)
        
    def __repr__(self: "FilterDoesNotExistException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
        })


class NoFilterFoundException(ValidationException):
    def __init__(
        self: "NoFilterFoundException", 
        message: str = "No filter of the specified type found.", 
    ):
        super().__init__(message)
        
    def __repr__(self: "NoFilterFoundException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
        })


class ConditionIsEqualToReplacementException(ValidationException):
    def __init__(
        self: "ConditionIsEqualToReplacementException", 
        message: str = "The specified filter replacement is the condition for another existing filter.", 
        condition: str | None = None, 
        replacement: str | None = None
    ):
        super().__init__(message)
        self.condition = condition
        self.replacement = replacement
        
    def __repr__(self: "ConditionIsEqualToReplacementException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message, 
            "condition": self.condition, 
            "replacement": self.replacement
        })
        
# telegram connection exceptions
class ConnectionsNotSyncronizedException(ValidationException):
    def __init__(
        self: "ConnectionsNotSyncronizedException", 
        message: str = "The connections are not syncronized.",
        input_id: str | None = None, 
        output_id: str | None = None
    ):
        super().__init__(message)
        self.input_id = input_id
        self.output_id = output_id
    
    def __repr__(self: "ConnectionsNotSyncronizedException") -> str:
        return str({
            "type": __class__.__name__, 
            "message": self.message,
            "input_id": self.input_id, 
            "output_id": self.output_id
        })
