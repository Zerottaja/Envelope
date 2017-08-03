"""This module contains a class that reads hexdumps from a FIFO-pipe"""

import struct

from timeout import timeout


class HexDumpReader:
    """HexDumpReader is a class that reads a line from a FIFO-pipe and
    transfroms the data into a more easily readable dict-package"""

    def __init__(self):
        try:
            print("opening")
            self.__file = open("packet_fifo",)
            print("opened")
        except FileNotFoundError as err:
            print(err)
        return

    @timeout()
    def read_hexdump(self):
        """read_hexdump() method fetches a new line from the pipe, strips away
        the delimiters and assigns predefined slots of data to variables"""
        data = self.__file.readline()
        if data != "" and data[-1] == "\n" and len(data) == 3072:
            data = data.replace(':', '')
        else:
            return
        packet = dict()
        try:
            for header, subdata in (("ROL", data[1560:1568]),
                                    ("PTC", data[1584:1592]),
                                    ("HDG", data[1608:1616]),
                                    ("AOA", data[1632:1640]),
                                    ("SDS", data[1656:1664]),
                                    ("ASP", data[1680:1688]),
                                    ("LOA", data[1704:1712]),
                                    ("FLP", data[1728:1736])):
                packet[header] = struct.unpack('!f', bytes.fromhex(subdata))[0]
        except struct.error:
            pass
        packet = self.formatter(packet)
        return packet

    @staticmethod
    def formatter(packet):
        """formatter is a method that transforms some units to SI"""
        # LOAD from ft/s^2 to g
        packet["LOA"] = -packet["LOA"] / 3.2808399 / 9.80665
        return packet


###############################################################################
# sudo tshark -Y "ip.src == 192.9.200.155 and tcp.len == 1024
# and data.data[2] == 21" -Eheader=n -Tfields -e data.data
# > packet_fifo
###############################################################################
# ip.src == 192.9.200.155 and tcp.len == 1024 and (data.data[2] == 11)
###############################################################################
if __name__ == '__main__':
    HDR = HexDumpReader()
    while True:
        try:
            DATA = HDR.read_hexdump()
            if DATA is not None:
                print(DATA)
        except TimeoutError:
            continue
