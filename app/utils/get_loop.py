from db.schema import Channel


def get_loop(channels: list[Channel], passed_channels: tuple[Channel, ...] = tuple()) -> tuple[Channel, ...] | None:
    """Find a loop in the channels outputs if there is one.

    Args:
        channels (list[Channel]): list of channels to check.
        passed_channels (tuple[Channel, ...], optional): list of channels that have been passed. Defaults to tuple().

    Returns:
        tuple[Channel, ...] | None: tuple of channels that form a loop or empty tuple if there is none.
    """

    for channel in channels:
        
        if channel in passed_channels:
            return *passed_channels, channel
        
        if len(channel.outputs) == 0:
            return None
        
        return get_loop(channel.outputs, (*passed_channels, channel))
