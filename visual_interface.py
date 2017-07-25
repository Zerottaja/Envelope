"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

import math
import time

from tkinter import Tk, Label, Frame, Canvas, PhotoImage, Button, Entry
from udp_receiver import UDPReceiver
from hexdumpreader import HexDumpReader


class EnvelopeWindow:
    """EnvelopeWindow is a class that generates a visual presentation of
    a simulator's positional and reactional values"""

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Simulator Envelope")
        self.__root.resizable(width=False, height=False)
        # self.__root.geometry('{}x{}'.format(1600, 800))

        Label(self.__root, text="Value log").grid(row=1, column=1,
                                                  columnspan=4)
        Label(self.__root, text="AOA bar", justify="left") \
            .grid(row=4, column=4, sticky="w")
        Label(self.__root, text="Load bar", justify="right") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__root, text="Envelope plot", justify="right") \
            .grid(row=1, column=5, columnspan=5, sticky="s")
        Label(self.__root, text="Load plot", justify="right") \
            .grid(row=1, column=11, sticky="s")
        Label(self.__root, text="Load bar", justify="right") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__root, height=0).grid(row=3, column=1, columnspan=4)
        Label(self.__root, height=0).grid(row=5, column=1, columnspan=4)
        Label(self.__root, text="Absolute inclination").grid(row=6, column=1,
                                                             columnspan=4)

        self.__logframe = Frame(self.__root, borderwidth=4, relief="sunken")
        self.__logframe.grid(row=2, column=1, columnspan=4, sticky="n")
        self.__logframe.grid_propagate(0)
        self.__logframe_contents = dict()
        self.__logframe_contents["headers"] \
            = Label(self.__logframe,
                    text="LON:\t\nLAT:\t\nALT:\t\nROLL:\t\nPITCH:\t"
                         "\nHDG:\t\nAOA:\t\nLOAD:\t\nAIRSPD:\t",
                    justify="left", bg='white')
        self.__logframe_contents["headers"].pack(side="left")
        self.__logframe_contents["values"] \
            = Label(self.__logframe,
                    text="n/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a",
                    justify="right", bg='white')
        self.__logframe_contents["values"].pack(side="right")

        self.__plotframe = Canvas(self.__root, height=600, width=600,
                                  borderwidth=4, relief="sunken", bg="#0f228b")
        img = PhotoImage(file="images/graphbg.gif")
        self.__plotframe.create_image(0, 0, image=img, anchor="nw")
        self.__plotframe.grid(row=2, rowspan=6, column=5, columnspan=5,
                              sticky="n")
        self.__plotframe.grid_propagate(0)
        self.__plotframe.create_line(300, 0, 300, 605, fill="white")
        self.__plotframe.create_line(0, 500, 605, 500, fill="white")
        self.__plotframe.create_oval(298, 498, 302, 502, fill="white",
                                     tags="origin")
        self.__plotframe.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                     tags="dot")
        self.__plotframe.create_text(10, 498, text="Roll (degrees)",
                                     anchor="sw", fill="white")
        self.__plotframe.create_text(305, 595,
                                     text="Angle of attack (degrees)",
                                     anchor="sw", fill="white")
        self.__plotframe.move("dot", 295, 495)

        self.__plotframe2 = Canvas(self.__root, height=600, width=600,
                                   borderwidth=4, relief="sunken",
                                   bg="#0f228b")
        self.__plotframe2.create_image(0, 0, image=img, anchor="nw")
        self.__plotframe2.grid(row=2, rowspan=6, column=11, sticky="n")
        self.__plotframe2.create_line(0, 400, 605, 400, fill="white")
        self.__plotframe2.create_line(50, 0, 50, 605, fill="white")
        self.__plotframe2.create_oval(48, 398, 52, 402, fill="white",
                                      tags="origin")
        self.__plotframe2.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                      tags="dot")
        self.__plotframe2.move("dot", 45, 395)
        self.__plotframe2.create_text(595, 398, text="Air velocity (knots)",
                                      anchor="se", fill="white")
        self.__plotframe2.create_text(55, 595,
                                      text="G Load (g)",
                                      anchor="sw", fill="white")

        self.__plot1_lines = []
        self.__plot2_lines = []

        self.__oldpitch = None
        self.__oldroll = None

        self.__oldvelocity = None
        self.__oldload = None
        self.__oldaoa = None

        self.__aoaframe = Canvas(self.__root, width=25, height=300,
                                 borderwidth=4,
                                 relief="sunken", bg="white")
        self.__aoaframe.grid(row=4, column=3, sticky="nw")
        self.__aoaframe.create_line(0, 150, 30, 150, fill="black")
        self.__aoaframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                       fill="#005a08", tags="aoabar")

        self.__loadframe = Canvas(self.__root, width=25, height=300,
                                  borderwidth=4,
                                  relief="sunken", bg="white")
        self.__loadframe.grid(row=4, column=2, sticky="ne")
        self.__loadframe.create_line(0, 150, 30, 150, fill="black")
        self.__loadframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                        fill="#005a08", tags="loadbar")

        self.__inclframe = Canvas(self.__root, width=200, height=200,
                                  borderwidth=4,
                                  relief="sunken", bg="#9ea9fe")
        self.__inclframe.grid(row=7, rowspan=2,
                              column=1, columnspan=4, sticky="n")
        self.__inclframe.create_line(30, 100, 90, 100, fill="black", width=2)
        self.__inclframe.create_line(90, 100, 90, 110, fill="black", width=2)
        self.__inclframe.create_line(110, 100, 110, 110, fill="black", width=2)
        self.__inclframe.create_line(170, 100, 110, 100, fill="black", width=2)
        self.__gndxy = [(-100, 100), (300, 100), (300, 300), (-100, 300)]
        self.__gnd = self.__inclframe \
            .create_polygon(self.__gndxy, fill="#8c603d", tags="gnd")
        self.__inclframe.lower("gnd")
        self.__inclframe.create_oval(99, 99, 101, 101)

        self.__stopbutton = Button(self.__root, text="Stop",
                                   command=self.__toggle_stop,
                                   activebackground="red")
        self.__stopbutton.grid(row=8, column=5)
        self.__stop = False

        Label(self.__root, text="Limit data points to last:")\
            .grid(row=8, column=6, sticky="e")
        vcmd = self.__root.register(self.validate_entry)
        self.__maxdatapoints = 3000
        self.__datapt_entry = Entry(self.__root, validate='key',
                                    validatecommand=(vcmd, '%S'),
                                    justify="right", width=7)
        self.__datapt_entry.insert(-1, self.__maxdatapoints)
        self.__datapt_entry.grid(row=8, column=7)

        self.__setbutton = Button(self.__root, text="Set",
                                  command=self.set_datapoint_limit)
        self.__setbutton.grid(row=8, column=8, sticky="w")

        self.__rx = UDPReceiver()
        self.__hdr = HexDumpReader()
        self.__log = open("capture4.txt", "r")
        # self.__root.after(100, self.read_log)
        # self.__root.after(100, self.listen_udp)
        self.__root.after(100, self.read_hexdump)

        self.__t0 = float(time.time())

        self.__root.mainloop()

        return

    def set_datapoint_limit(self):
        """set_datapoint_limit is a method that fetches an integer from
        the entry line and sets it to be the current datapoint limit"""
        try:
            # if the entry contains a sensible integer, set limit
            self.__maxdatapoints = int(self.__datapt_entry.get())
            self.__setbutton.configure(text="Limit set!", state="disabled")
        except ValueError:
            # if the entry contains nothing or a weird value, no limit
            self.__setbutton.configure(text="No limit", state="disabled")
            self.__maxdatapoints = 100000
        return

    def __toggle_stop(self):
        """toggle_stop is a method that raises and lowers
        the stop-flag that halts plotting datapoints"""
        if self.__stop is True:
            self.__stop = False
            self.__stopbutton.configure(text="Stop", activebackground="red")
        else:
            self.__stop = True
            self.__stopbutton.configure(text="Start", activebackground="green")
        return

    def validate_entry(self, text):
        """validate_entry is a method that checks every character that is added
        or removed from the entry line and decides if said character is OK"""
        try:
            # value change in entry box toggles button disable off
            self.__setbutton.configure(text="Set", state="normal")
        except AttributeError:
            pass
        # checking every character in proposed entry if they are ok
        for char in text:
            if char in '0123456789':
                continue
            else:
                return False
        try:
            # finally checking if the characters are ok as a whole
            int(text)
            return True
        except ValueError:
            return False

    def listen_udp(self):
        """listen_udp() is a method that calls UDPReceiver's method
        to receive packets through UDP"""

        packet = self.__rx.listen_to_port()
        if packet is not None:
            # display updated values
            self.display_data(packet)
        # read again soon
        self.__root.after(30, self.listen_udp)
        return

    def read_log(self):
        """read_log() is a method that reads prerecorded packets from a
        text file and sends them onwards, emulating actual traffic"""

        data = self.__log.readline()
        if data == '':
            self.__log.close()
            self.__log = open("capture4.txt", "r")
            print("loop")
        else:
            data = str(data)
            data = data.strip("b'\\n")
            data = data.split(",")
            packet = self.__rx.formatter(data)
            self.display_data(packet)
        self.__root.after(30, self.read_log)
        return

    def read_hexdump(self):
        """read_hexdump is a method that calls
        the slave HexDumpReader object's reading method."""
        packet = self.__hdr.read_hexdump()
        if packet:
            self.display_data(packet)
        self.__root.after(100, self.read_hexdump)
        return

    def display_data(self, packet):
        """display_data() is a method that calls all methods
        that update EnvelopeWindow's UI"""
        if not self.__stop:
            self.update_logframe(packet)
            # print(packet["LON"])
            self.update_plotframe(packet)
            self.update_aoaframe(packet)
            self.update_inclframe(packet)
            self.update_loadframe(packet)
            self.update_plotframe2(packet)
            self.__oldpitch = packet["PTC"]
            self.__oldroll = packet["ROL"]
            print("dT of window update:", float(time.time()) - self.__t0)
            self.__t0 = float(time.time())

        return

    def update_logframe(self, packet):
        """update_logframe is a method that updates
        the logframe's numerical contents"""

        self.__logframe_contents["values"] \
            .configure(text="%.4f° \n%.4f° \n%.4fft\n%.4f° \n%.4f° "
                       "\n%.4f° \n%.4f° \n%.4fg \n%.4fkt "
                       % (packet['LON'], packet["LAT"],
                          packet["ALT"], packet["ROL"],
                          packet["PTC"], packet["HDG"],
                          packet["AOA"], packet["LOA"],
                          packet["ASP"]),
                       justify="right", bg='white')
        return

    def update_plotframe(self, packet):
        """update_plotframe is a method that updates
        the contents of the AOA-ROLL -graph"""
        scale = 5
        offset = (300, 500)
        try:
            self.__plot1_lines\
                .append(self.__plotframe
                        .create_line(self.__oldroll * scale + offset[0],
                                     self.__oldaoa * -scale + offset[1],
                                     packet["ROL"] * scale + offset[0],
                                     packet["AOA"] * -scale + offset[1],
                                     fill="white"))
        except TypeError:
            pass

        newxy = [offset[0] - 5 + packet["ROL"] * scale,
                 offset[1] - 5 + -packet["AOA"] * scale,
                 offset[0] + 5 + packet["ROL"] * scale,
                 offset[1] + 5 + -packet["AOA"] * scale]
        self.__plotframe.coords("dot", *newxy)

        diff = len(self.__plot1_lines) - self.__maxdatapoints
        if diff > 0:
            for _ in range(0, diff):
                self.__plotframe.delete(self.__plot1_lines[0])
                self.__plot1_lines.pop(0)
        return

    def update_plotframe2(self, packet):
        """update_plotframe2 is a method that updates
        the contents of the AIRSPD-LOAD -graph"""
        aspscale = 1.2222
        loascale = 10
        offset = (50, 400)
        try:
            self.__plot2_lines\
                .append(self.__plotframe2
                        .create_line(self.__oldvelocity * aspscale + offset[0],
                                     self.__oldload * -loascale + offset[1],
                                     packet["ASP"] * aspscale + offset[0],
                                     packet["LOA"] * -loascale + offset[1],
                                     fill="white"))
        except TypeError:
            pass
        self.__oldvelocity = packet["ASP"]
        self.__oldload = packet["LOA"]

        newxy = [offset[0]-5 + packet["ASP"] * aspscale,
                 offset[1]-5 + -packet["LOA"] * loascale,
                 offset[0]+5 + packet["ASP"] * aspscale,
                 offset[1]+5 + -packet["LOA"] * loascale]
        self.__plotframe2.coords("dot", *newxy)

        diff = len(self.__plot2_lines) - self.__maxdatapoints
        if diff > 0:
            for _ in range(0, diff):
                self.__plotframe2.delete(self.__plot2_lines[0])
                self.__plot2_lines.pop(0)
        return

    def update_aoaframe(self, packet):
        """update_aoaframe is a method that updates
        the visual bar graph displaying AOA"""
        scale = 5  # 5 px/degree --> 30 deg == full bar
        self.__aoaframe.coords("aoabar",
                               [0, 150, 30, 150, 30, 150-(scale*packet["AOA"]),
                                0, 150-(scale*packet["AOA"])])
        if abs(packet["AOA"]) > 30:
            self.__aoaframe.itemconfig("aoabar", fill="#800000")
            return
        color = hex(abs(int(abs(packet["AOA"]) / 30*255) - 0xff)).lstrip('0')
        color = color.lstrip('x')
        if len(color) == 1:
            color = '0'+color
        self.__aoaframe.itemconfig("aoabar", fill="#80{}00".format(color))
        self.__aoaframe.lower("aoabar")
        return

    def update_loadframe(self, packet):
        """update_loadframe is a method that updates
        the visual bar graph displaying load on wings"""
        scale = 50  # 50 px/g --> 3g == full bar
        self.__loadframe.coords("loadbar",
                                [0, 150, 30, 150, 30,
                                 150-(scale*packet["LOA"]),
                                 0, 150-(scale*packet["LOA"])])
        if abs(packet["LOA"]) > 3:
            self.__loadframe.itemconfig("loadbar", fill="#800000")
            return
        color = hex(abs(int(abs(packet["LOA"]) / 3*255) - 0xff)).lstrip('0')
        color = color.lstrip('x')
        if len(color) == 1:
            color = '0'+color
        self.__loadframe.itemconfig("loadbar", fill="#80{}00".format(color))
        self.__loadframe.lower("loadbar")
        return

    def update_inclframe(self, packet):
        """update_inclframe is a method that updates
        the visual absolute inclination display contents"""
        scale = 2
        y_offset = packet["PTC"] * scale
        newxy = [-100, int(100+y_offset), 300, int(100+y_offset),
                 300, 300, -100, 300]
        deg = packet["ROL"]
        rad = (math.pi / 180) * deg
        for i in range(0, 4):
            x = newxy[i*2]
            y = newxy[i*2+1]
            offset = complex(100, 100)
            v = complex(math.cos(-rad), math.sin(-rad)) * \
                (complex(x, y) - offset) + offset
            newxy[i*2] = v.real
            newxy[i*2+1] = v.imag
        self.__inclframe.coords("gnd", *newxy)
        return

if __name__ == '__main__':
    EnvelopeWindow()
