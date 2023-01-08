from typing import Callable

from inspect import getsource

from ast import AST, AsyncFunctionDef, parse, walk, get_docstring


def help_(router: Callable[[str], None | Exception]) -> str:
    """Gets docstring of all route closures in router function to create a help message.

    Args:
        router (Callable[[str], None  |  Exception]): router function (main).

    Returns:
        str: message with all commands.
    """
    
    # parse source code of router function
    source: str = getsource(router)
    tree: AST = parse(source)
    
    # filter async functions from tree
    functions: list[AsyncFunctionDef] = [f for f in walk(tree) if isinstance(f, AsyncFunctionDef)]

    # get docstrings of all functions
    function_docs_: list[str | None] = [get_docstring(f) for f in functions]
    function_docs: list[str] = [f for f in function_docs_ if f is not None]
    
    # replace spaces with indented new lines to make it look better
    function_docs = [f.replace(" ", "\n    ") for f in function_docs]
    
    message: str = "Commands:\n\n" + "\n\n".join(function_docs)
    return message
