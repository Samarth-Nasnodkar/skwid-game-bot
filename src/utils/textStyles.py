def bold(text: str) -> str:
    return f"**{text}**"


def italics(text: str) -> str:
    return f"*{text}*"


def strikethrough(text: str) -> str:
    return f"~~{text}~~"


def underline(text: str) -> str:
    return f"__{text}__"


def spoiler(text: str) -> str:
    return f"||{text}||"


def highlight(text: str) -> str:
    return f"`{text}`"


def code(text: str) -> str:
    return f"```{text}```"
