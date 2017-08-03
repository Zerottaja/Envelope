"""Docstring"""

from hexdumpreader import HexDumpReader
from analoginputreader import AnalogInputReader


class RelayNode:
    """Docstring"""

    def __init__(self):
        self.HDR = HexDumpReader()
        self.AIR = AnalogInputReader()
        return

    def gather_data(self):
        """Docstring"""
        return


if __name__ == '__main__':
    RN = RelayNode()
