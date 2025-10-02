import abc
import re

__all__ = ("MessageProcessor",)


class MessageProcessor(abc.ABC):
    """
    A base class for message processors to implement methods for handling console messages.
    """

    @staticmethod
    def decode_message(message: bytes) -> tuple[str | None, str | None, str, str]:
        """
        Decode a console message into its components.

        :param message: The raw message bytes.
        :return: A tuple containing (message_id, unknown_digits, message_type, data).
        """
        match = re.search(
            rb'(.{2})'  # 2 characters (Message ID?)
            rb'\x17'  # ETB
            rb'\x16'  # SYN
            rb'([0-9]{8})?'  # 8 Digits
            rb'\x01'  # SOH
            rb'([0-9]{10})'  # 10 Digits (Message Type)
            rb'\x02'  # STX
            rb'(.*)',  # Data (arbitrary length)
            message
        )

        if match:
            message_id = match.group(1).decode('ascii') if match.group(1) else None
            unknown_digits = match.group(2).decode('ascii') if match.group(2) else None
            message_type = match.group(3).decode('ascii')
            data = match.group(4).decode('ascii')
            return message_id, unknown_digits, message_type, data
        else:
            raise ValueError("Invalid message format")

    @abc.abstractmethod
    def process_message(self, message: bytes) -> None:
        """
        Process an incoming message from the console.

        :param message:
        :return: None
        :rtype: None
        """
        raise NotImplementedError("Subclasses must implement this method.")
