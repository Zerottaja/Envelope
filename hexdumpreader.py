"""This module contains a class that reads hexdumps from a FIFO-pipe"""

import struct


class HexDumpReader:
    """HexDumpReader is a class that reads a line from a FIFO-pipe and
    transfroms the data into a more easily readable dict-package"""

    def __init__(self):
        try:
            self.__file = open("packet_fifo")
        except FileNotFoundError as err:
            print(err)
        return

    def read_hexdump(self):
        """read_hexdump() method fetches a new line from the pipe,
        strips away the delimiters and assigns
        predefined slots of data to variables"""
        data = self.__file.readline()
        if data != "":
            data = data.replace(':', '')
        else:
            return
        packet = dict()
        try:
            for header, arg, subdata in (("ROL", '!f', data[48:56]),
                                         ("PTC", '!f', data[72:80]),
                                         ("HDG", '!f', data[96:104]),
                                         ("AOA", '!f', data[120:128]),
                                         ("ASP", '!f', data[144:152]),
                                         ("LOA", '!f', data[168:176]),
                                         ("LAT", '>d', data[184:200]),
                                         ("LON", '>d', data[208:224]),
                                         ("ALT", '!f', data[240:248])):
                packet[header] = struct.unpack(arg, bytes.fromhex(subdata))[0]

        except struct.error:
            pass
        return packet


###############################################################################
# sudo tshark -Y "ip.src == 192.9.200.155 and tcp.len == 1024
# and data.data[2] == 21" -Eheader=n -Tfields -e data.data
# > /home/samu/PycharmProjects/Envelope/packet_fifo
###############################################################################
if __name__ == '__main__':
    HDR = HexDumpReader()
    while True:
        read_data = HDR.read_hexdump()
        print(read_data)
