"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

from tkinter import Tk, Label
from udp_receiver import UDPReceiver


class EnvelopeWindow:
    """DOCSTRING"""  # TODO Docstring

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Envelope")
        self.__root.resizable(width=False, height=False)
        # self.__root.geometry('{}x{}'.format(1600, 800))

        self.__rollLabel = Label(self.__root)

        self.__rx = UDPReceiver()
        self.__root.after(100, self.listen_udp)

        self.__root.mainloop()

        return

    def listen_udp(self):
        """DOCSTRING"""  # TODO Docstring
        packet = self.__rx.listen_to_port()
        self.display_data(packet)
        self.__root.after(10, self.listen_udp)
        return

    def display_data(self, packet):
        self.__rollLabel.configure(text=
                                   "LON:\t%.2f\nLAT:\t%.2f\nALT:\t%.2f\nROLL:"
                                   "\t%.2f\nPITCH:\t%.2f\nHDG:\t%.2f"
                                   % (packet["LON"],
                                      packet["LAT"],
                                      packet["ALT"],
                                      packet["ROL"],
                                      packet["PTC"],
                                      packet["HDG"]), justify="left")
        self.__rollLabel.pack(side="left")

if __name__ == '__main__':
    EW = EnvelopeWindow()
