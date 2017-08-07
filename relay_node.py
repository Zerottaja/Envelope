"""This module contains a class that gathers data from different sources
and packs it into a csv string."""

from time import sleep
from hexdumpreader import HexDumpReader
from analoginputreader import AnalogInputReader


class RelayNode:
    """RelayNode is a class containing TCP and analog reader objects,
    which are read regularly."""

    def __init__(self):
        self.HDR = HexDumpReader()
        self.AIR = AnalogInputReader()
        self.__old_packet = {"ROL": 0.0, "PTC": 0.0, "HDG": 0.0, "AOA": 0.0,
                             "SDS": 0.0, "LOA": 0.0, "ASP": 0.0, "FLP": 0.0}
        return

    def gather_data(self):
        """gather_data() calls reader objects' reading methods
        and packs their data together."""

        try:
            tcp_packet = self.HDR.read_hexdump()
            self.__old_packet = tcp_packet
        except TimeoutError:
            tcp_packet = self.__old_packet
        analog_packet = self.AIR.read_analog()
        for header in tcp_packet:
            analog_packet[header] = tcp_packet[header]
        # packet = {**tcp_packet, **analog_packet}
        csv_string = self.formatter(analog_packet)

        return csv_string

    @staticmethod
    def formatter(packet):
        """formatter() transforms dict packets
        into csv strings in a predefined order."""

        csv_string = ""
        for header in ("ROL", "PTC", "HDG", "AOA", "SDS", "ASP",
                       "LOA", "ELE", "AIL", "RUD", "FLP"):
            csv_string += str(packet[header])

        return csv_string


if __name__ == '__main__':
    RN = RelayNode()
    while True:
        DATA = RN.gather_data()
        print(DATA)
        sleep(0.03)
