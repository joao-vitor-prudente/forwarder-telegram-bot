from functools import reduce

from db.schema import Filter
from app.utils.link_remover import remove_link


def treat_message(message: str, filters: list[Filter]) -> str | None:  
    """Uses filters to treat message.

    Args:
        message (str): message to be treated.
        filters (list[Filter]): filter objects from database to determine how the message should be treated.

    Returns:
        str | None: treated message or None if the message should be ignored.
    """
    
    # get list of operations that should be performed
    blacklist: list[str] = [str(filter_.condition) for filter_ in filters if str(filter_.mode) == "blacklist"]
    to_be_replaced: list[str] = [str(filter_.condition) for filter_ in filters if str(filter_.mode) == "replacement"]
    replacements: list[str] = [str(filter_.replacement) for filter_ in filters if str(filter_.mode) == "replacement"]
    link_removers: list[str] = [str(filter_.condition) for filter_ in filters if str(filter_.mode) == "link_remover"]
    
    # treat blacklist
    if any([expr in message for expr in blacklist]): return None
    
    # starts with the message and iterates through expressions and replacements returning the replaced message for the next iteration
    message_: str = reduce(lambda prev, curr: prev.replace(curr[0], curr[1]), zip(to_be_replaced, replacements), message)
    # starts with de message and iterates through link removers returning the message without links for the next iteration
    message_: str = reduce(lambda prev, curr: remove_link(prev, curr), link_removers, message_)
    return message_