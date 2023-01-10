from functools import reduce
import re

Pos = tuple[int, int]


# TODO: IN CASE OF TWO IDENTICAL URLS, THIS ONLY DETECTS THE FIRST
def get_link_positions(message: str, domain: str) -> list[Pos]:
    # get the start and end position of the links of the specified domain.
    return [
        (message.index(word), message.index(word) + len(word))   # start -> index of the word, end -> index of the word + length of the word.
        for word in message.replace("\n", " ").split()  # separate the word by spaces and new lines.
        if domain in word and "." in word[1:-2]  # checks if the domain is in the word and if there is a . in the middle of the word.
    ]


def remove_poctuation_from_links(message: str, link_positions: list[Pos], ponctuation: list[str]) -> list[Pos]:
    return [(
        start + 1 if message[start] in ponctuation else start, # check if doesnt start with ponctuation
        end - 1 if message[end - 1] in ponctuation else end  # check if doesnt end with ponctuation
    ) for start, end in link_positions]


def replace_link_for_placeholder(message: str, link_positions: list[Pos]) -> str:
    # replace the areas where there is a link that is going to be removed for a placeholder in order to avoid problems while separating phrases   
    return reduce(
        lambda prev, curr: prev[:curr[0]] + "p" * (curr[1] - curr[0]) + prev[curr[1]:], 
        # prev is the message, curr is a tuple with start and end position of the link. 
        link_positions, message
    )


def get_indices_of_delimiters(placeholder_message: str, delimiters: list[str]) -> list[Pos]:
    # gets the start end end of all the segments separated by any of the delimiters.
    return [
        (m.start(0), m.end(0))  # get start and end
        for m in re.finditer(re.compile(  # iterate through delimiters.
            "|".join(map(re.escape, delimiters))  # get regex for delimiters using the delimiters list.
        ), placeholder_message)
    ]
    

def get_indices_of_segments(placeholder_message: str, delimiter_positions: list[Pos]) -> list[Pos]:
    return [(0, delimiter_positions[0][0] + 1)] + [  # first segment: 0 to start of next delimiter
        (prev_end, curr_end)  # middle segments: the end of the previous to the end of the current
        for (_, prev_end), (_, curr_end) in zip(delimiter_positions, delimiter_positions[1:])  # loops through tuples of two consecutive positions
    ] + [(delimiter_positions[-1][1], len(placeholder_message))]  # last segment: end of last delimiter to end of message


def remove_link_segments(segment_positions: list[Pos], link_positions: list[Pos]) -> list[Pos]:
    return [
        (start_segment, end_segment) 
        for start_segment, end_segment in segment_positions
        if not any(start_link in range(start_segment, end_segment) for start_link, _ in link_positions)  
        # check if start of link is in range of segment. 
        # OBS: a link cannot be in two segments at once.
    ]


def assemble_message(message: str, remaining_segments: list[Pos]) -> str:
    return "".join(
        [message[start:end] for start, end in remaining_segments]  # joins message from remaining segments.
    ).replace("\n ", "\n").lstrip("\n").rstrip("\n").replace("\n\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
    # correct cases where there a space at the beguining of the line
    # correct cases where the message starts or ends with new lines
    # correct cases where the removal of links leaves a lot of new lines
    
    
sep = f"\n{'x'*30}\n"
def remove_link(message: str, domain: str) -> str:    
    # create dict of links to remove and their position.
    pos_link: list[Pos] = get_link_positions(message, domain)
    if len(pos_link) == 0:
        return message
    # remove any ponctuation counted in pos_link at the begining or end of any link position
    ponctuation: list[str] = [".", ",", "!", "?"]
    pos_link: list[Pos] = remove_poctuation_from_links(message, pos_link, ponctuation)
    # substitute links for commom placeholder to identify where they were and not mess up the splitting.
    temp_message: str = replace_link_for_placeholder(message, pos_link)
    # get start and end indices of all delimiters in order of appearance.
    delimiters: list[str] = ["\n", ".", "?", "!"]
    delimiter_pos: list[Pos] = get_indices_of_delimiters(temp_message, delimiters)
    # get start and end indices of all segments delimited by all delimiters in order of appearance.
    segments_pos: list[Pos] = get_indices_of_segments(temp_message, delimiter_pos)
    # remove segments that contain the links to remove.
    remaining_segments: list[Pos] = remove_link_segments(segments_pos, pos_link)
    # join segments and do some final treatment.
    new_message: str = assemble_message(message, remaining_segments)
    return new_message