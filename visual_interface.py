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

        self.__logframe = Frame(self.__root, borderwidth=4, relief="sunken")
        self.__logframe.grid(row=1, column=1, sticky="n")
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
                                  borderwidth=4, relief="sunken", bg="white")
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
                                 borderwidth=4,
                                 relief="sunken", bg="white")
        self.__aoaframe.grid(row=2, column=1, sticky="n")
        aoabar = PhotoImage(file="images/aoa.gif")
        self.__aoaframe.create_image(40, 150, image=aoabar, tags="bar")
        self.__aoaframe.create_line(0, 150, 78, 150, fill="white")

        # skybox = PhotoImage("images/skybox.gif")
        self.__inclframe = Canvas(self.__root, width=200, height=200,
                                  borderwidth=4,
                                  relief="sunken", bg="#9ea9fe")
        self.__inclframe.grid(row=3, column=1, sticky="n")
        # self.__inclframe.create_image(40, 150, image=skybox, tags="box")
        self.__inclframe.create_line(30, 100, 90, 100, fill="black", width=2)
        self.__inclframe.create_line(90, 100, 90, 110, fill="black", width=2)
        self.__inclframe.create_line(110, 100, 110, 110, fill="black", width=2)
        self.__inclframe.create_line(170, 100, 110, 100, fill="black", width=2)
        self.__gndxy = [(-10, 10), (30, 10), (30, 30), (-10, 30)]
        self.__gnd = self.__inclframe.create_polygon(self.__gndxy,
                                                     fill="#8c603d", tags="gnd")
        self.__inclframe.lower("gnd")
        self.__inclframe.create_oval(99, 99, 101, 101)
        newxy = []
        for x, y in self.__gndxy:
            v = 1 * (complex(x, y) - 0) + 0
            newxy.append(v.real)
            newxy.append(v.imag)
        print(newxy)
        self.__inclframe.coords(self.__inclframe.find_withtag("gnd"), *newxy)

        self.__rx = UDPReceiver()
        self.__log = open("capture2.txt", "r")
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
            self.__log = open("capture2.txt", "r")
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
        scale = 20
        self.__plotframe.create_line(self.__oldroll*scale+450,
                                     self.__oldpitch*-scale+450,
                                     packet["ROL"]*scale+450,
                                     packet["PTC"]*-scale+450)
        dp = (packet["PTC"] - self.__oldpitch) * -scale
        self.__oldpitch = packet["PTC"]
        dr = (packet["ROL"] - self.__oldroll) * scale
        self.__oldroll = packet["ROL"]
        self.__plotframe.move("dot", dr, dp)

        return

    def update_aoaframe(self, packet):
        dy = (packet["PTC"] - self.__oldaoa) * 6
        self.__oldaoa = packet["PTC"]
        self.__aoaframe.move("bar", 0, dy)

if __name__ == '__main__':
    EW = EnvelopeWindow()
