def parse_command(tokens: list[str]) -> dict[str, str]:
    """Parses the command string and returns a dictionary with the arguments and its values.
        Eg.: ["/add_input_channel", "channel", "channel_name", "url", "https://t.me/..."]
        ---> {"channel": "channel_name", "url": "https://t.me/..."}
    Args:
        tokens (list[str]): list of string containing tokenized command.

    Returns:
        dict[str, str]: dictionary associating the arguments with its values.
    """

    args = tokens[1:][::2]
    vals = tokens[1:][1::2]
    kwargs: dict[str, str] = dict(zip(args, vals))
    
    return kwargs
