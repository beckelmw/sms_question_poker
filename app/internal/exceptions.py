from dataclasses import dataclass


@dataclass
class ServiceException(Exception):
    code: int = 400
    message: str = "An error occurred"
