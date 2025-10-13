from dataclasses import dataclass


@dataclass
class Remote:
    owner: str
    project: str
    url: str
