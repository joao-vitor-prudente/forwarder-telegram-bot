from re import split


def tokenize_command(command: str) -> list[str]:
    """Tokenizes the command string.
        Eg.: "/add_input_channel --channel=channel_name --url=https://t.me/..."
        ---> ["/add_input_channel", "channel", "channel_name", "url", "https://t.me/..."]
    Args:
        command (str): string containing the command.

    Returns:
        list[str]: list of strings containing the tokens.
    """

    tokens: list[str] = split(r"--|=", command)
    tokens: list[str] = [token.strip() for token in tokens]

    return tokens
