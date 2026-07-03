from typing import TypedDict

class ProfileState(TypedDict):
    """
    Represents the state of a profile in the data profiler agent.
    """
    file_path: str
    schema: dict
    quality: dict
    statistics: dict
    report: dict