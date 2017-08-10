"""This module contains a class that gathers data from different sources
and packs it into a csv string."""

from time import sleep
from analoginputreader import AnalogInputReader


class RelayNode:
    """RelayNode is a class containing TCP and analog reader objects,
    which are read regularly."""

    def __init__(self):
        self.AIR = AnalogInputReader()
        return

    def gather_data(self):
        """gather_data() calls reader objects' reading methods
        and packs their data together."""

        analog_packet = self.AIR.read_analog()

        csv_string = self.formatter(analog_packet)

        return csv_string

    @staticmethod
    def formatter(packet):
        """formatter() transforms dict packets
        into csv strings in a predefined order."""

        csv_string = ""
        for header in ("ELE", "AIL", "RUD"):
            csv_string += str(packet[header]) + ","
        csv_string = csv_string[:-1]

        return csv_string


if __name__ == '__main__':
    RN = RelayNode()
    while True:
        DATA = RN.gather_data()
        print(DATA)
        sleep(0.03)
