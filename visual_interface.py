"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

from tkinter import Tk, Label, Frame, Canvas
from udp_receiver import UDPReceiver


class EnvelopeWindow:
    """DOCSTRING"""  # TODO Docstring

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Envelope")
        self.__root.resizable(width=False, height=False)
        # self.__root.geometry('{}x{}'.format(1600, 800))

        self.__logframe = Frame(self.__root, padx=1, pady=1, bg="black")
        self.__logframe.grid(row=1, column=1, sticky="nw")
        self.__logframe.grid_propagate(0)
        self.__logframe_contents = dict()
        self.__logframe_contents["headers"] = Label(self.__logframe)
        self.__logframe_contents["values"] = Label(self.__logframe)

        self.__plotframe = Canvas(self.__root, bg="black",
                                  height=900, width=900)
        self.__plotframe.grid(row=1, rowspan=2, column=2, sticky="nw")
        self.__plotframe.grid_propagate(0)
        self.__plotframe.create_rectangle(1, 1, 900, 900, fill="white")

        self.__rx = UDPReceiver()
        self.__root.after(100, self.listen_udp)

        self.__root.mainloop()

        return

    def listen_udp(self):
        """DOCSTRING"""  # TODO Docstring
        packet = self.__rx.listen_to_port()
        self.display_data(packet)
        self.__root.after(250, self.listen_udp)
        return

    def display_data(self, packet):
        """DOCSTRING"""  # TODO Docstring
        self.update_logframe(packet)
        return

    def update_logframe(self, packet):
        """DOCSTRING"""  # TODO Docstring
        self.__logframe_contents["headers"] \
            .configure(text="LON:\t\nLAT:\t\nALT:\t\n"
                            "ROLL:\t\nPITCH:\t\nHDG:\t\nAOA\t",
                       justify="left", bg='white')
        self.__logframe_contents["headers"].pack(side="left")

        self.__logframe_contents["values"] \
            .configure(text="%.4f° \n%.4f° \n%.4fft\n%.4f° \n%.4f° "
                            "\n%.4f° \n%.4f° "
                       % (packet["LON"], packet["LAT"],
                          packet["ALT"], packet["ROL"],
                          packet["PTC"], packet["HDG"], packet["AOA"]),
                       justify="right", bg='white')
        self.__logframe_contents["values"].pack(side="right")
        return

if __name__ == '__main__':
    EW = EnvelopeWindow()
