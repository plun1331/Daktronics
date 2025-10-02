import abc
import time

import serial

from .processors import MessageProcessor

__all__ = ("Console", "Omnisport2000")


class Console(abc.ABC):
    """
    A base class for console classes to implement methods for connecting,
    reading data, and closing the connection.

    Attributes:
        port_name (str): The name of the serial port to connect to.
        baud_rate (int): The baud rate for the serial connection.
        parity (str): The parity setting for the serial connection.
        data_bits (int): The number of data bits for the serial connection.
        read_interval (float): The interval in seconds between read attempts.
    """

    def __init__(
        self,
        port_name: str,
        baud_rate: int = 19200,
        parity: str = serial.PARITY_NONE,
        data_bits: int = 8,
        read_interval: float | int = 0.01
    ) -> None:
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.parity = parity
        self.data_bits = data_bits
        self.read_interval = read_interval

    def connect(self) -> serial.Serial:
        """
        Establish a connection to the console.

        :return: The serial connection object.
        :rtype: serial.Serial
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def read(self, processor: "MessageProcessor") -> None:
        """
        Continuously read messages from the console and process them.

        :param processor: An instance of a MessageProcessor to handle incoming messages.
        :return: None
        :rtype: None
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def close(self) -> None:
        """
        Close the serial connection to the console.
        :rtype: None
        """
        raise NotImplementedError("Subclasses must implement this method.")


class Omnisport2000(Console):
    """
    A class to represent the Daktronics Omnisport 2000 scoreboard console.

    This class provides methods to connect to the console, read data, and parse
    messages related to water polo scorekeeping.

    Attributes:
        port_name (str): The name of the serial port to connect to.
        baud_rate (int): The baud rate for the serial connection.
        parity (str): The parity setting for the serial connection.
        data_bits (int): The number of data bits for the serial connection.
        read_interval (float): The interval in seconds between read attempts.
    """

    def __init__(
        self,
        port_name: str,
        baud_rate: int = 19200,
        parity: str = serial.PARITY_NONE,
        data_bits: int = 8,
        read_interval: float | int = 0.01
    ) -> None:
        super().__init__(port_name, baud_rate, parity, data_bits, read_interval)
        self.serial_connection = None
        self.read_allowed = False

    def connect(self) -> None:
        self.serial_connection = serial.Serial(
            port=self.port_name,
            baudrate=self.baud_rate,
            parity=self.parity,
            bytesize=self.data_bits,
            timeout=1
        )
        return self.serial_connection

    def read(self, processor: MessageProcessor) -> None:
        first_message = True
        if self.read_allowed:
            raise RuntimeError("Read operation already in progress.")
        if self.serial_connection is None or not self.serial_connection.is_open:
            raise RuntimeError("Serial connection is not established. Call connect() first.")

        message_buffer = bytearray()
        self.read_allowed = True

        while self.read_allowed:
            data = self.serial_connection.read(self.serial_connection.in_waiting or 1)
            if data:
                message_buffer.extend(data)

            while b'\x04' in message_buffer:  # EOT is 0x04
                eot_index = message_buffer.index(b'\x04')
                message = message_buffer[:eot_index]
                message_buffer = message_buffer[eot_index + 1:]

                if first_message:
                    # the first message is always missing this data for some reason
                    message = b"00\x17" + message
                    first_message = False
                    continue

                if not message:
                    continue  # Skip empty messages

                # Process the message
                processor.process_message(message)

            time.sleep(self.read_interval)

    def close(self) -> None:
        self.read_allowed = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None
