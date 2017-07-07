"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

from tkinter import Tk, Label, Frame, Canvas, PhotoImage
from udp_receiver import UDPReceiver


class EnvelopeWindow:
    """DOCSTRING"""  # TODO Docstring

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Envelope")
        self.__root.resizable(width=False, height=False)
        # self.__root.geometry('{}x{}'.format(1600, 800))

        self.__logframe = Frame(self.__root, borderwidth=2, relief="sunken")
        self.__logframe.grid(row=1, column=1, sticky="nw")
        self.__logframe.grid_propagate(0)
        self.__logframe_contents = dict()
        self.__logframe_contents["headers"] \
            = Label(self.__logframe,
                    text="LON:\t\nLAT:\t\nALT:\t\nROLL:\t\nPITCH:\t"
                         "\nHDG:\t\nAOA:\t",
                    justify="left", bg='white')
        self.__logframe_contents["headers"].pack(side="left")
        self.__logframe_contents["values"] \
            = Label(self.__logframe, text="n/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a",
                    justify="right", bg='white')
        self.__logframe_contents["values"].pack(side="right")

        self.__plotframe = Canvas(self.__root, height=900, width=900,
                                  borderwidth=2, relief="sunken", bg="white")
        skybox = PhotoImage(file="images/skybox.gif")
        self.__plotframe.create_image(3, 1, image=skybox, anchor="nw")
        self.__plotframe.grid(row=1, rowspan=15, column=2, sticky="nw")
        self.__plotframe.grid_propagate(0)
        self.__plotframe.create_line(450, 0, 450, 905)
        self.__plotframe.create_line(0, 450, 905, 450)
        self.__plotframe.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                     tags="dot")
        self.__plotframe.create_oval(448, 448, 452, 452, fill="black",
                                     tags="origin")
        self.__plotframe.move("dot", 445, 445)
        self.__oldpitch = 0
        self.__oldroll = 0
        self.__oldaoa = 0

        self.__aoaframe = Canvas(self.__root, width=75, height=300,
                                 borderwidth=2,
                                 relief="raised", bg="white")
        self.__aoaframe.grid(row=2, column=1, sticky="n")
        aoabar = PhotoImage(file="images/aoa.gif")
        self.__aoaframe.create_image(40, 150, image=aoabar, tags="bar")
        self.__aoaframe.create_line(0, 150, 78, 150, fill="white")

        self.__rx = UDPReceiver()
        self.__log = open("log.txt", "r")
        self.__root.after(100, self.read_log)
        # self.__root.after(100, self.listen_udp)

        self.__root.mainloop()

        return

    def listen_udp(self):
        """DOCSTRING"""  # TODO Docstring
        packet = self.__rx.listen_to_port()
        print(packet)
        if packet is not None:
            self.display_data(packet)
        self.__root.after(30, self.listen_udp)
        return

    def read_log(self):
        data = self.__log.readline()
        if data == '':
            self.__log.close()
            self.__log = open("log.txt", "r")
            print("loop")
        else:
            data = str(data)
            data = data.strip("b'\\n")
            data = data.split(",")
            packet = self.__rx.formatter(data)
            self.display_data(packet)
        self.__root.after(30, self.read_log)
        return

    def display_data(self, packet):
        """DOCSTRING"""  # TODO Docstring
        self.update_logframe(packet)
        self.update_plotframe(packet)
        self.update_aoaframe(packet)
        return

    def update_logframe(self, packet):
        """DOCSTRING"""  # TODO Docstring

        self.__logframe_contents["values"] \
            .configure(text="%.4f° \n%.4f° \n%.4fft\n%.4f° \n%.4f° "
                            "\n%.4f° \n%.4f° "
                            % (packet["LON"], packet["LAT"],
                               packet["ALT"], packet["ROL"],
                               packet["PTC"], packet["HDG"], packet["AOA"]),
                       justify="right", bg='white')
        return

    def update_plotframe(self, packet):
        self.__plotframe.create_line(self.__oldroll*5+450,
                                     self.__oldpitch*-5+450,
                                     packet["ROL"]*5+450,
                                     packet["PTC"]*-5+450)
        dp = (packet["PTC"] - self.__oldpitch) * -5
        self.__oldpitch = packet["PTC"]
        dr = (packet["ROL"] - self.__oldroll) * 5
        self.__oldroll = packet["ROL"]
        self.__plotframe.move("dot", dr, dp)

        return

    def update_aoaframe(self, packet):
        dy = (packet["PTC"] - self.__oldaoa) * 6
        self.__oldaoa = packet["PTC"]
        self.__aoaframe.move("bar", 0, dy)

if __name__ == '__main__':
    EW = EnvelopeWindow()
