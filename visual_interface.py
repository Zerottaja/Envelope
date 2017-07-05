"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

from tkinter import Tk
from udp_receiver import UDPReceiver


class EnvelopeWindow:
    """DOCSTRING"""  # TODO Docstring

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Envelope")
        self.__root.resizable(width=False, height=False)
        self.__root.geometry('{}x{}'.format(1600, 800))

        self.__rx = UDPReceiver()
        self.__root.after(100, self.listen_udp)

        self.__root.mainloop()

        return

    def listen_udp(self):
        """DOCSTRING"""  # TODO Docstring
        packet = self.__rx.listen_to_port()
        print(packet)
        self.__root.after(10, self.listen_udp)
        return

if __name__ == '__main__':
    EW = EnvelopeWindow()
