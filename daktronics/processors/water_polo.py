from typing import Literal

from .base import MessageProcessor

__all__ = ("WaterPoloProcessor",)


class WaterPoloProcessor(MessageProcessor):
    def process_message(self, message: bytes) -> None:
        message_id, unknown_digits, message_type, data = self.decode_message(message)
        match message_type:
            case "0042100000":
                if data.strip() == "":
                    data = "0:00"
                if ":" not in data:
                    data = "0:" + data
                minutes, seconds = map(int, data.split(':'))
                total_seconds = minutes * 60 + seconds
                self.game_time(total_seconds)
            case "0042100005":
                seconds = int(data) if data.strip() else None
                self.shot_time(seconds)
            case "0042100010":
                if data.strip() == "":
                    data = "0:00"
                if ":" not in data:
                    data = "0:" + data
                minutes, seconds = map(int, data.split(':'))
                total_seconds = minutes * 60 + seconds
                self.timeout_timer(total_seconds)
            case "0042100015":
                home_score, away_score = data[0:2].strip(), data[2:4].strip()
                self.score(int(home_score), int(away_score))
            case "0042100019":
                if len(data) >= 2:
                    home_timeouts, away_timeouts = data[0], data[1]
                    home_partial, away_partial = data[2], data[3]
                    self.timeouts_left(int(home_timeouts), int(away_timeouts), int(home_partial), int(away_partial))
            case "0042100023":
                self.period(int(data) if data != "R" else "R")
            case "0042100024":  # Can be multiple
                while data:
                    cap = data[:2].strip()
                    time = data[2:7].strip()
                    data = data[7:]
                    if not time:
                        continue
                    self.home_penalty_timer(int(cap) if cap else None, int(time))
            case "0042100045":
                while data:
                    cap = data[:2].strip()
                    time = data[2:7].strip()
                    data = data[7:]
                    if not time:
                        continue
                    self.home_penalty_timer(int(cap) if cap else None, int(time))
            case "0042100066":
                counts = {}
                while data:
                    cap = data[:2].strip()
                    count = data[2:3].strip()
                    data = data[3:]
                    counts[cap] = count
                self.home_penalties({int(k): int(v) for k, v in counts.items()})
            case "0042100141":
                counts = {}
                while data:
                    cap = data[:2].strip()
                    count = data[2:3].strip()
                    data = data[3:]
                    counts[cap] = count
                self.away_penalties({int(k): int(v) for k, v in counts.items()})
            case _:
                self.unknown_message(message_type, data)

    def game_time(self, seconds: int) -> None:
        """
        Handle game time update.

        :param seconds: Total game time in seconds.
        :return: None
        """
        pass

    def shot_time(self, seconds: int | None) -> None:
        """
        Handle shot time update. None indicates the shot clock should be turned off.

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

    def period(self, period: int | Literal["R"]) -> None:
        """
        Handle period update. R indicates rest period.

        :param period: The current period of the game.
        :return: None
        """
        pass

    def home_penalty_timer(self, cap: int | None, seconds: int) -> None:
        """
        Handle home penalty timer update. None indicates that the player number has not been entered into the console.

        :param cap: The cap number of the player with the penalty.
        :param seconds: The remaining penalty time in seconds.
        :return:
        """
        pass

    def away_penalty_timer(self, cap: int | None, seconds: int) -> None:
        """
        Handle away penalty timer update. None indicates that the player number has not been entered into the console.

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


# Ejection end -> sends ejection list
# no horn
