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

        Label(self.__root, text="Value log").grid(row=1, column=1,
                                                  columnspan=4)
        Label(self.__root, text="AOA bar", justify="left").grid(row=4,
                                                                column=4,
                                                                sticky="w")
        Label(self.__root, text="Load bar", justify="right").grid(row=4,
                                                                column=1,
                                                                sticky="e")
        Label(self.__root, text="Envelope plot", justify="right")\
            .grid(row=1, column=5, sticky="s")
        Label(self.__root, text="Load plot", justify="right") \
            .grid(row=1, column=6, sticky="s")
        Label(self.__root, text="Load bar", justify="right").grid(row=4,
                                                                  column=1,
                                                                  sticky="e")
        Label(self.__root, height=0).grid(row=3, column=1, columnspan=4)
        Label(self.__root, height=0).grid(row=5, column=1, columnspan=4)
        Label(self.__root, text="Visual inclination").grid(row=6, column=1,
                                                           columnspan=4)

        self.__logframe = Frame(self.__root, borderwidth=4, relief="sunken")
        self.__logframe.grid(row=2, column=1, columnspan=4, sticky="n")
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

        self.__plotframe = Canvas(self.__root, height=600, width=600,
                                  borderwidth=4, relief="sunken", bg="white")
        self.__plotframe.grid(row=2, rowspan=6, column=5, sticky="n")
        self.__plotframe.grid_propagate(0)
        self.__plotframe.create_line(300, 0, 300, 605)
        self.__plotframe.create_line(0, 300, 605, 300)
        self.__plotframe.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                     tags="dot")
        self.__plotframe.create_oval(298, 298, 302, 302, fill="black",
                                     tags="origin")
        self.__plotframe.move("dot", 295, 295)

        self.__plotframe2 = Canvas(self.__root, height=600, width=600,
                                   borderwidth=4, relief="sunken", bg="white")
        self.__plotframe2.grid(row=2, rowspan=6, column=6, sticky="n")

        self.__datapoints = []

        self.__oldpitch = None
        self.__oldroll = None
        self.__oldaoa = None
        self.__oldinclcoords = [0, 0, 0, 0, 0, 0, 0, 0]

        self.__aoaframe = Canvas(self.__root, width=25, height=300,
                                 borderwidth=4,
                                 relief="sunken", bg="white")
        self.__aoaframe.grid(row=4, column=3, sticky="nw")
        aoabar = PhotoImage(file="images/aoa.gif")
        self.__aoaframe.create_image(40, 150, image=aoabar, tags="bar")
        self.__aoaframe.create_line(0, 150, 78, 150, fill="white")

        self.__loadframe = Canvas(self.__root, width=25, height=300,
                                 borderwidth=4,
                                 relief="sunken", bg="white")
        self.__loadframe.grid(row=4, column=2, sticky="ne")

        # skybox = PhotoImage("images/skybox.gif")
        self.__inclframe = Canvas(self.__root, width=200, height=200,
                                  borderwidth=4,
                                  relief="sunken", bg="#9ea9fe")
        self.__inclframe.grid(row=7, column=1, columnspan=4, sticky="n")
        # self.__inclframe.create_image(40, 150, image=skybox, tags="box")
        self.__inclframe.create_line(30, 100, 90, 100, fill="black", width=2)
        self.__inclframe.create_line(90, 100, 90, 110, fill="black", width=2)
        self.__inclframe.create_line(110, 100, 110, 110, fill="black", width=2)
        self.__inclframe.create_line(170, 100, 110, 100, fill="black", width=2)
        self.__gndxy = [(-100, 100), (300, 100), (300, 300), (-100, 300)]
        self.__gnd = self.__inclframe\
            .create_polygon(self.__gndxy, fill="#8c603d", tags="gnd")
        self.__inclframe.lower("gnd")
        self.__inclframe.create_oval(99, 99, 101, 101)

        self.__rx = UDPReceiver()
        self.__log = open("capture2.txt", "r")
        # self.__root.after(100, self.read_log)
        self.__root.after(100, self.listen_udp)

        self.__root.mainloop()

        return

    def listen_udp(self):
        """DOCSTRING"""  # TODO Docstring
        packet = self.__rx.listen_to_port()
        if packet is not None:
            self.display_data(packet)
        self.__root.after(30, self.listen_udp)
        return

    def read_log(self):
        """DOCSTRING"""  # TODO Docstring
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
        import time
        t1 = float(time.time())
        self.update_logframe(packet)
        self.update_plotframe(packet)
        self.update_aoaframe(packet)
        self.update_inclframe(packet)
        self.__oldpitch = packet["PTC"]
        self.__oldroll = packet["ROL"]
        print(float(time.time()) - t1)
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
        """DOCSTRING"""  # TODO Docstring
        scale = 5
        try:
            self.__datapoints \
                .append(self.__plotframe.create_line(self.__oldroll*scale+300,
                                                     self.__oldpitch*-scale+300,
                                                     packet["ROL"]*scale+300,
                                                     packet["PTC"]*-scale+300))
            dp = (packet["PTC"] - self.__oldpitch) * -scale
            dr = (packet["ROL"] - self.__oldroll) * scale
        except TypeError:
            dp = packet["PTC"] * -scale
            dr = packet["ROL"] * scale
        self.__plotframe.move("dot", dr, dp)
        if len(self.__datapoints) > 5000:
            self.__plotframe.delete(self.__datapoints[0])
            self.__datapoints.pop(0)
        return

    def update_aoaframe(self, packet):
        """DOCSTRING"""  # TODO Docstring
        try:
            dy = (packet["PTC"] - self.__oldaoa) * 6
        except TypeError:
            dy = packet["PTC"] * 6
        self.__oldaoa = packet["PTC"]
        self.__aoaframe.move("bar", 0, dy)

    def update_inclframe(self, packet):
        """DOCSTRING"""  # TODO Docstring
        try:
            dy = (packet["PTC"] - self.__oldpitch) * 3
        except TypeError:
            dy = packet["PTC"] * 3
        newxy = []
        i = 0
        for x, y in self.__gndxy:
            newxy.append(x)
            newxy.append(y+dy)
            self.__gndxy[i] = (x, y+dy)
            i += 1
        self.__inclframe.coords(self.__inclframe.find_withtag("gnd"), *newxy)

        import math
        deg = packet["ROL"]
        rad = (math.pi / 180) * deg
        newxy = []
        for x, y in self.__gndxy:
            v = complex(math.cos(-rad), math.sin(-rad)) * \
                (complex(x, y) - complex(100, 100)) + complex(100, 100)
            newxy.append(v.real)
            newxy.append(v.imag)
        self.__inclframe.coords(self.__inclframe.find_withtag("gnd"), *newxy)

if __name__ == '__main__':
    EW = EnvelopeWindow()
