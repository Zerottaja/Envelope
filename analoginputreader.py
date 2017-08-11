"""This module contains a class AnalogInputReader that reads
aircraft control values from a RPi analog shield and returns them."""

from gpiozero import MCP3008


class AnalogInputReader:
    """AnalogInputReader reads the voltages of a RPi analog shield inputs and
    transforms the voltages into control data."""

    def __init__(self):
            self.ele = MCP3008(channel=1)
            self.ail = MCP3008(channel=2)
            self.rud = MCP3008(channel=3)

    def read_analog(self):
        """read_analog() gets the values of the input pins
        and packs them in a dictionary."""
        packet = dict()
        packet["ELE"] = self.ele._read()
        packet["AIL"] = self.ail._read()
        packet["RUD"] = self.rud._read()
        return packet


if __name__ == '__main__':
    AIR = AnalogInputReader()
    while True:
        AIR_DATA = AIR.read_analog()
        if AIR_DATA:
            print(AIR_DATA)
