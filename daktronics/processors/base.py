from typing import Protocol

__all__ = ("MessageProcessor",)

class MessageProcessor(Protocol):
    """
    A base protocol for message processors to implement methods for handling console messages.
    """
    def process_message(self, message: bytes) -> None:
        """
        Process an incoming message from the console.

        :param message:
        :return: None
        :rtype: None
        """
        ...