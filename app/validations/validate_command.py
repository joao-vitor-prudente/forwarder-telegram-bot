from app.cmd.tokenize import tokenize_command


def validate_command(command: str, arg_num: int) -> bool:
    """Validates the command string.

    Args:
        command (str): command string.
        arg_num (int): number of arguments to be parsed.

    Returns:
        bool: True if the command is valid, False otherwise.
    """
    
    if command.count("--") != arg_num or command.count("=") != arg_num:
        return False

    tokens: list[str] = tokenize_command(command)

    # 1 [command] + arg_num [args] + arg_num [values]
    expected_len = 1 + 2 * arg_num

    if len(tokens) != expected_len:
        return False

    if any([token == "" for token in tokens]):
        return False

    return True
