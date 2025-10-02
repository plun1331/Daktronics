from .base import MessageProcessor
import re

__all__ = ("WaterPoloProcessor",)

class WaterPoloProcessor(MessageProcessor):
    @staticmethod
    def decode_message(message: bytes) -> tuple[str, str, str, str, str]:
        """
        Decode a water polo message into its components.

        :param message: The raw message bytes.
        :return: A tuple containing (message_id, unknown_digits, message_type, data).
        """
        match = re.search(
            rb'(.{2})'  # 2 characters (Message ID?)
            rb'\x17'    # ETB
            rb'\x16'    # SYN
            rb'([0-9]{8})?' # 8 Digits
            rb'\x01'    # SOH
            rb'([0-9]{10})' # 10 Digits (Message Type)
            rb'\x02'    # STX
            rb'(.*)',     # Data (arbitrary length)
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

    def process_message(self, message: bytes) -> None:
        message_id, unknown_digits, message_type, data = self.decode_message(message)
        if message_type == "0042100000":
            minutes, seconds = map(int, data.split(':'))
            total_seconds = minutes * 60 + seconds
            self.game_time(total_seconds)
            print(f"  Game Time: {data} ({total_seconds} seconds)")
        elif message_type == "0042100005":
            seconds = int(data)
            self.shot_time(seconds)
            print(f"  Shot Time: {data} ({seconds} seconds)")
        elif message_type == "0042100010":
            minutes, seconds = map(int, data.split(':'))
            total_seconds = minutes * 60 + seconds
            self.timeout_timer(total_seconds)
            print(f"  Timeout Timer: {data} ({total_seconds} seconds)")
        elif message_type == "0042100015":
            home_score, away_score = data[0:2].strip(), data[2:4].strip()
            self.score(int(home_score), int(away_score))
            print(f"  Score: Home - {home_score}, Away - {away_score}")
        elif message_type == "0042100019":
            if len(data) >= 2:
                home_timeouts, away_timeouts = data[0], data[1]
                home_partial, away_partial = data[2], data[3]
                self.timeouts_left(int(home_timeouts), int(away_timeouts), int(home_partial), int(away_partial))
                print(f"  Timeouts Left: Home - {home_timeouts}/{home_partial}, Away - {away_timeouts}/{away_partial}")
            else:
                print(f"  Warning: Incomplete Timeouts Data: {data}")
        elif message_type == "0042100023":
            self.period(int(data))
            print(f"  Period: {data}")
        elif message_type == "0042100024":  # Can be multiple
            while data:
                cap = data[:2].strip()
                time = data[2:7].strip()
                data = data[7:]
                self.home_penalty_timer(int(cap), int(time))
                print(f"  Home Penalty Timer: Cap {cap} - {time}")
        elif message_type == "0042100045":
            while data:
                cap = data[:2].strip()
                time = data[2:7].strip()
                data = data[7:]
                self.away_penalty_timer(int(cap), int(time))
                print(f"  Away Penalty Timer: Cap {cap} - {time}")
        elif message_type == "0042100066":
            counts = {}
            while data:
                cap = data[:2].strip()
                count = data[2:3].strip()
                data = data[3:]
                counts[cap] = count
            self.home_penalties({int(k): int(v) for k, v in counts.items()})
            print("  Home Penalties: " + ", ".join([f"{k}: {v}" for k, v in counts.items()]))
        elif message_type == "0042100141":
            counts = {}
            while data:
                cap = data[:2].strip()
                count = data[2:3].strip()
                data = data[3:]
                counts[cap] = count
            self.away_penalties({int(k): int(v) for k, v in counts.items()})
            print("  Away Penalties: " + ", ".join([f"{k}: {v}" for k, v in counts.items()]))
        else:
            self.unknown_message(message_type, data)
            print(f"  Unknown Message Type: {message_type}, Data: {data}")

    def game_time(self, seconds: int) -> None:
        """
        Handle game time update.

        :param seconds: Total game time in seconds.
        :return: None
        """
        pass

    def shot_time(self, seconds: int) -> None:
        """
        Handle shot time update.

        :param seconds: Total game time in seconds.
        :return: None
        """
        pass

    def timeout_timer(self, seconds: int) -> None:
        """
        Handle timeout timer update.

        :param seconds: Total timeout time in seconds.
        :return: None
        """
        pass

    def score(self, home_score: int, away_score: int) -> None:
        """
        Handle score update.

        :param home_score: The score for the home team.
        :param away_score: The score for the away team.
        :return: None
        """
        pass

    def timeouts_left(self, home_timeouts: int, away_timeouts: int, home_partial: int, away_partial: int) -> None:
        """
        Handle timeouts left update.

        :param home_timeouts: The number of timeouts left for the home team.
        :param away_timeouts: The number of timeouts left for the away team.
        :param home_partial:  The number of partial timeouts left for the home team.
        :param away_partial: The number of partial timeouts left for the away team.
        :return:
        """
        pass

    def period(self, period: int) -> None:
        """
        Handle period update.

        :param period: The current period of the game.
        :return: None
        """
        pass

    def home_penalty_timer(self, cap: int, seconds: int) -> None:
        """
        Handle home penalty timer update.

        :param cap: The cap number of the player with the penalty.
        :param seconds: The remaining penalty time in seconds.
        :return:
        """
        pass

    def away_penalty_timer(self, cap: int, seconds: int) -> None:
        """
        Handle away penalty timer update.

        :param cap: The cap number of the player with the penalty.
        :param seconds: The remaining penalty time in seconds.
        :return:
        """
        pass

    def home_penalties(self, penalties: dict[int, int]) -> None:
        """
        Handle home penalties update.

        :param penalties: A dictionary mapping cap numbers to their penalty counts.
        :return: None
        """
        pass

    def away_penalties(self, penalties: dict[int, int]) -> None:
        """
        Handle away penalties update.

        :param penalties: A dictionary mapping cap numbers to their penalty counts.
        :return: None
        """
        pass

    def unknown_message(self, message_type: str, data: str) -> None:
        """
        Handle unknown message types.

        :param message_type: The type of the unknown message.
        :param data: The data associated with the unknown message.
        :return: None
        """
        pass
