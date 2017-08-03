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

    # pylint: disable=too-many-instance-attributes

    def __init__(self):

        # Initializing window
        self.__root = Tk()
        self.__root.title("Simulator Envelope")
        self.__root.resizable(width=False, height=False)

        # datapoints (plot lines) are stored in lists
        self.__maxdatapoints = 3000
        self.__plot1_lines = []
        self.__plot2_lines = []
        self.__stop = False

        # initializing all window elements
        self.__init_titles()
        self.__init_logframe()
        self.__init_plotframe()
        self.__init_plotframe2()
        self.__init_aoaframe()
        self.__init_loadframe()
        self.__init_inclframe()
        self.__init_widgets()

        # previous values of some data are kept track of
        self.__oldroll = None
        self.__oldvelocity = None
        self.__oldload = None
        self.__oldaoa = None

        # initializing input with 0 being TCP packets, 1 being UDP packets
        # and 2 being pre-recorded data
        data_input = 0
        if data_input == 0:
            self.__hdr = HexDumpReader()
            self.__root.after(100, self.read_hexdump)
        elif data_input == 1:
            self.__rx = UDPReceiver()
            self.__root.after(100, self.listen_udp)
        elif data_input == 2:
            self.__rx = UDPReceiver()
            self.__log = open("capture4.txt", "r")
            self.__root.after(100, self.read_log)

        self.__t0 = float(time.time())

        # fire up the rootwindow
        self.__root.mainloop()

        return

    def __init_titles(self):
        """init_titles() is a method that creates titles
        and some strucural elements on the root window"""

        # titles
        Label(self.__root, text="Value log")\
            .grid(row=1, column=1, columnspan=4)
        Label(self.__root, text="AOA bar", justify="left") \
            .grid(row=4, column=4, sticky="w")
        Label(self.__root, text="Load bar", justify="right") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__root, text="Roll-Angle of Attack plot", justify="right") \
            .grid(row=1, column=5, columnspan=5, sticky="s")
        Label(self.__root, text="Airspeed-Load plot", justify="right") \
            .grid(row=1, column=11, sticky="s")
        Label(self.__root, text="Load bar", justify="right") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__root, text="Absolute inclination")\
            .grid(row=6, column=1, columnspan=4)
        # empty labels as structural dividers
        Label(self.__root, height=0).grid(row=3, column=1, columnspan=4)
        Label(self.__root, height=0).grid(row=5, column=1, columnspan=4)
        return

    def __init_logframe(self):
        """init_logframe() is a method that creates
        a frame for showing flight data values"""

        # init the frame
        self.__logframe = Frame(self.__root, borderwidth=4, relief="sunken")
        self.__logframe.grid(row=2, column=1, columnspan=4, sticky="n")
        self.__logframe.grid_propagate(0)
        self.__logframe_contents = dict()
        # headers for values
        self.__logframe_contents["headers"] \
            = Label(self.__logframe,
                    text="ROLL:\t\nPITCH:\t\nHDG:\t\nAOA:\t\n"
                         "SIDESLP:\t\nLOAD:\t\nAIRSPD:\t\nFLAPS:\t",
                    justify="left", bg='white')
        self.__logframe_contents["headers"].pack(side="left")
        # default values before receiving data are "n/a"
        self.__logframe_contents["values"] \
            = Label(self.__logframe,
                    text="n/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a",
                    justify="right", bg='white')
        self.__logframe_contents["values"].pack(side="right")
        return

    def __init_plotframe(self):
        """init_plotframe() is a method that creates
        a frame for plotting the AOA-ROLL -graph"""

        # init the frame
        self.__plotframe = Canvas(self.__root, height=600, width=600,
                                  borderwidth=4, relief="sunken", bg="#0f228b")
        # nice little fade to black on the background
        self.img = PhotoImage(file="images/graphbg.gif")
        self.__plotframe.create_image(0, 0, image=self.img, anchor="nw")
        self.__plotframe.grid(row=2, rowspan=6, column=5, columnspan=5,
                              sticky="n")
        self.__plotframe.grid_propagate(0)
        # plot axis
        self.__plotframe.create_line(300, 0, 300, 605, fill="white")
        self.__plotframe.create_line(0, 500, 605, 500, fill="white")
        # origin dot
        self.__plotframe.create_oval(298, 498, 302, 502, fill="white",
                                     tags="origin")
        # moving target dot
        self.__plotframe.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                     tags="dot")
        # axis legend
        self.__plotframe.create_text(10, 498, text="Roll (degrees)",
                                     anchor="sw", fill="white")
        self.__plotframe.create_text(305, 595,
                                     text="Angle of attack (degrees)",
                                     anchor="sw", fill="white")
        # init the target dot to origin
        self.__plotframe.move("dot", 295, 495)
        return

    def __init_plotframe2(self):
        """init_plotframe2() is a method that creates
        a frame for plotting the AIRSPEED-LOAD -graph"""

        # scales
        aspscale = 1.8333
        vmo = 259
        vmm = 181
        nss = 85
        loascale = 100  # 100 px/g --> 4 g/positive halfplot
        gmp = 3.10
        gmn = 1.24
        offset = (50, 400)  # centerpoint offset

        # init the frame
        self.__plotframe2 = Canvas(self.__root, height=600, width=600,
                                   borderwidth=4, relief="sunken",
                                   bg="#0f228b")
        # nice little fade to black on the background
        self.__plotframe2.create_image(0, 0, image=self.img, anchor="nw")
        self.__plotframe2.grid(row=2, rowspan=6, column=11, sticky="n")
        # plot axis
        self.__plotframe2.create_line(0, offset[1], 605, offset[1],
                                      fill="white")
        self.__plotframe2.create_line(offset[0], 0, offset[0], 605,
                                      fill="white")

        # limit lines
        # max operating speed
        self.__plotframe2.create_line(offset[0] + vmo*aspscale, 0,
                                      offset[0] + vmo*aspscale, 605,
                                      fill="red")
        self.__plotframe2.create_text(offset[0] + vmo*aspscale + 5, 595,
                                      text="Max\noperating\nspeed",
                                      anchor="sw", fill="red")
        # normal stall speed
        self.__plotframe2.create_line(offset[0] + nss * aspscale, 0,
                                      offset[0] + nss * aspscale, 605,
                                      fill="red")
        self.__plotframe2.create_text(offset[0] + nss * aspscale + 5, 595,
                                      text="Normal stall speed",
                                      anchor="sw", fill="red")
        # max maneuver speed
        self.__plotframe2.create_line(offset[0] + vmm*aspscale, 0,
                                      offset[0] + vmm*aspscale, 605,
                                      fill="green", dash=4)
        self.__plotframe2.create_text(offset[0] + vmm*aspscale + 5, 595,
                                      text="Maneuvering speed",
                                      anchor="sw", fill="green")
        # max positive load
        self.__plotframe2.create_line(0, offset[1] - gmp*loascale, 605,
                                      offset[1] - gmp * loascale,
                                      fill="red")
        self.__plotframe2.create_text(595, offset[1] - gmp*loascale - 2,
                                      text="Max + load",
                                      anchor="se", fill="red")
        # max negative load
        self.__plotframe2.create_line(0, offset[1] + gmn*loascale, 605,
                                      offset[1] + gmn * loascale,
                                      fill="red")
        self.__plotframe2.create_text(595, offset[1] + gmn*loascale - 2,
                                      text="Max - load",
                                      anchor="se", fill="red")
        old_y = 0
        x = 0
        while x < 501:
            y = 0.001661882*(x**2) + 0.3827509917*x
            self.__plotframe2.create_line(offset[0]+x-10, offset[1]-old_y,
                                          offset[0]+x, offset[1]-y, fill="red")
            old_y = y
            x += 10

        self.__plotframe2.create_line(0, offset[1] - 1*loascale, 605,
                                      offset[1] - 1*loascale,
                                      fill="green", dash=4)

        # origin dot
        self.__plotframe2.create_oval(offset[0]-2, offset[1]-2,
                                      offset[0]+2, offset[1]+2, fill="white",
                                      tags="origin")
        # moving target dot
        self.__plotframe2.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                      tags="dot")
        # axis legend
        self.__plotframe2.create_text(595, offset[1]-2,
                                      text="Air velocity (knots)",
                                      anchor="se", fill="white")
        self.__plotframe2.create_text(offset[0]+5, 595,
                                      text="G load (g)",
                                      anchor="sw", fill="white")
        # init the target dot to origin
        self.__plotframe2.move("dot", offset[0]-5, offset[1]-5)
        return

    def __init_aoaframe(self):
        """init_aoaframe() is a method that creates
        a frame and a bar for displaying the ANGLE OF ATTACK"""

        # init the frame
        self.__aoaframe = Canvas(self.__root, width=25, height=300,
                                 borderwidth=4,
                                 relief="sunken", bg="white")
        self.__aoaframe.grid(row=4, column=3, sticky="nw")
        # create a zero-level line
        self.__aoaframe.create_line(0, 150, 30, 150, fill="black")
        # create the bar as a stretching polygon
        self.__aoaframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                       fill="#005a08", tags="aoabar")
        return

    def __init_loadframe(self):
        """init_aoaframe() is a method that creates
        a frame and a bar for displaying the LOAD"""

        # init the frame
        self.__loadframe = Canvas(self.__root, width=25, height=300,
                                  borderwidth=4,
                                  relief="sunken", bg="white")
        self.__loadframe.grid(row=4, column=2, sticky="ne")
        # create a zero-level line
        self.__loadframe.create_line(0, 150, 30, 150, fill="black")
        # create the bar as a stretching polygon
        self.__loadframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                        fill="#005a08", tags="loadbar")
        return

    def __init_inclframe(self):
        """init_inclframe() is a method that creates a frame and a visual
        horizon for displaying the absolute inclination of the aeroplane"""

        # init the frame
        self.__inclframe = Canvas(self.__root, width=200, height=200,
                                  borderwidth=4,
                                  relief="sunken", bg="#9ea9fe")
        self.__inclframe.grid(row=7, rowspan=3,
                              column=1, columnspan=4, sticky="n")
        # create the crossbar
        self.__inclframe.create_line(30, 100, 90, 100, fill="black", width=2)
        self.__inclframe.create_line(90, 100, 90, 110, fill="black", width=2)
        self.__inclframe.create_line(110, 100, 110, 110, fill="black", width=2)
        self.__inclframe.create_line(170, 100, 110, 100, fill="black", width=2)
        self.__inclframe.create_oval(99, 99, 101, 101)
        # create a tuple list for ground sprite coordinates
        self.__gndxy = [(-100, 100), (300, 100), (300, 300), (-100, 300)]
        # create ground/horizon as a polygon
        self.__gnd = self.__inclframe \
            .create_polygon(self.__gndxy, fill="#8c603d", tags="gnd")
        # make sure ground is behind crossbar
        self.__inclframe.lower("gnd")
        return

    def __init_widgets(self):
        """init_widgets() is a method that creates all utility widgets,
        such as buttons and entry boxes"""

        # create a stop button and assign command
        self.__stopbutton = Button(self.__root, text="Stop",
                                   command=self.__toggle_stop,
                                   activebackground="red")
        self.__stopbutton.grid(row=8, column=5)

        # create a clear button and assign command
        self.__clearbutton = Button(self.__root, text="Clear",
                                    command=self.clear_plots,
                                    activebackground="blue")
        self.__clearbutton.grid(row=9, column=5)

        # create a text label describing the purpose of the entry box
        Label(self.__root, text="Limit data points to last:") \
            .grid(row=8, rowspan=2, column=6, sticky="e")
        # bind the variable vcmd to a method call for validation
        vcmd = self.__root.register(self.validate_entry)
        # create an entrybox for changing the maximum datapoint limit
        self.__datapt_entry \
            = Entry(self.__root, validate='key', validatecommand=(vcmd, '%S'),
                    justify="right", width=7)
        # default value for entrybox is 3000
        self.__datapt_entry.insert(-1, self.__maxdatapoints)
        self.__datapt_entry.grid(row=8, column=7, rowspan=2)

        # create a set button for the datapoint limit and assign command
        self.__setbutton = Button(self.__root, text="Set",
                                  command=self.set_datapoint_limit)
        self.__setbutton.grid(row=8, column=8, rowspan=2, sticky="w")
        return

    def clear_plots(self):
        """clear_plots is a method that deletes
        the stored datapoints and lines from the window"""

        try:
            # keep deleting datapoint until they run out, throwing IndexError
            while True:
                self.__plotframe.delete(self.__plot1_lines[0])
                self.__plotframe2.delete(self.__plot2_lines[0])
                self.__plot1_lines.pop(0)
                self.__plot2_lines.pop(0)
        except IndexError:
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
            # configure the color of the button
            self.__stopbutton.configure(text="Stop", activebackground="red")
        else:
            self.__stop = True
            # configure the color of the button
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

        # fetch a line from the file
        data = self.__log.readline()
        # when running out of linces, start over
        if data == '':
            self.__log.close()
            self.__log = open("capture4.txt", "r")
        else:
            # strip extra characters away from the line
            data = str(data)
            data = data.strip("b'\\n")
            data = data.split(",")
            # use UDP reader's formatter for packaging
            packet = self.__rx.formatter(data)
            # and if the package is not null, display the data
            if packet:
                self.display_data(packet)
        # read again soon
        self.__root.after(30, self.read_log)
        return

    def read_hexdump(self):
        """read_hexdump is a method that calls
        the slave HexDumpReader object's reading method"""

        # get the package from HexDumpReader
        try:
            packet = self.__hdr.read_hexdump()
            if packet:
                self.display_data(packet)
        except TimeoutError:
            print("timeout yay!")
        # and if the package is not null, display the data
        # read again soon
        self.__root.after(200, self.read_hexdump)
        return

    def display_data(self, packet):
        """display_data() is a method that calls all methods
        that update EnvelopeWindow's UI"""

        # update values only if the stop flag is not raised
        if not self.__stop:
            self.update_logframe(packet)
            # print(packet["LON"])
            self.update_plotframe(packet)
            self.update_aoaframe(packet)
            self.update_inclframe(packet)
            self.update_loadframe(packet)
            self.update_plotframe2(packet)
            self.__oldroll = packet["ROL"]
            self.__oldaoa = packet["AOA"]

            print("dT of window update:", float(time.time()) - self.__t0)
            self.__t0 = float(time.time())
        return

    def update_logframe(self, packet):
        """update_logframe is a method that updates
        the logframe's numerical contents"""

        # use package data to update contents
        self.__logframe_contents["values"] \
            .configure(text="%.2f° \n%.2f° \n%.2f° \n"
                            "%.2f° \n%.2f° \n%.2fg \n"
                            "%.2fkt\n%.2f° "
                       % (packet["ROL"], packet["PTC"], packet["HDG"],
                          packet["AOA"], packet["SDS"], packet["LOA"],
                          packet["ASP"], packet["FLP"],),
                       justify="right", bg='white')
        return

    def update_plotframe(self, packet):
        """update_plotframe is a method that updates
        the contents of the AOA-ROLL -graph"""

        aoascale = 15  # 15 px/degree --> 33 degrees/positive halfplot
        rollscale = 5  # 5 px/degree --> 60 degrees/positive halfplot
        offset = (300, 500)  # centerpoint offset
        try:
            # create a line from old datapoint to new one
            self.__plot1_lines\
                .append(self.__plotframe
                        .create_line(self.__oldroll * rollscale + offset[0],
                                     self.__oldaoa * -aoascale + offset[1],
                                     packet["ROL"] * rollscale + offset[0],
                                     packet["AOA"] * -aoascale + offset[1],
                                     fill="white"))
        # first attempt throws a TypeError, oldvalues being None
        except TypeError:
            pass

        # calculate new coordinates for the target dot
        newxy = [offset[0] - 5 + packet["ROL"] * rollscale,
                 offset[1] - 5 + -packet["AOA"] * aoascale,
                 offset[0] + 5 + packet["ROL"] * rollscale,
                 offset[1] + 5 + -packet["AOA"] * aoascale]
        # move the target dot
        self.__plotframe.coords("dot", *newxy)
        self.__plotframe.lift("dot")

        # check if the amount of datapoints is over the limit
        diff = len(self.__plot1_lines) - self.__maxdatapoints
        if diff > 0:
            # in that case, delete datapoints until difference is 0
            for _ in range(0, diff):
                self.__plotframe.delete(self.__plot1_lines[0])
                self.__plot1_lines.pop(0)
        return

    def update_plotframe2(self, packet):
        """update_plotframe2 is a method that updates
        the contents of the AIRSPD-LOAD -graph"""

        aspscale = 1.8333  # 1.83 px/kt --> 300 kts/positive halfplot
        loascale = 100  # 100 px/g --> 4 g/positive halfplot
        offset = (50, 400)  # centerpoint offset
        try:
            # create a line from old datapoint to new one
            self.__plot2_lines\
                .append(self.__plotframe2
                        .create_line(self.__oldvelocity * aspscale + offset[0],
                                     self.__oldload * -loascale + offset[1],
                                     packet["ASP"] * aspscale + offset[0],
                                     packet["LOA"] * -loascale + offset[1],
                                     fill="white"))
        # first attempt throws a TypeError, oldvalues being None
        except TypeError:
            pass
        self.__oldvelocity = packet["ASP"]
        self.__oldload = packet["LOA"]

        # calculate new coordinates for the target dot
        newxy = [offset[0]-5 + packet["ASP"] * aspscale,
                 offset[1]-5 + -packet["LOA"] * loascale,
                 offset[0]+5 + packet["ASP"] * aspscale,
                 offset[1]+5 + -packet["LOA"] * loascale]
        # move the target dot
        self.__plotframe2.coords("dot", *newxy)
        self.__plotframe2.lift("dot")

        # check if the amount of datapoints is over the limit
        diff = len(self.__plot2_lines) - self.__maxdatapoints
        if diff > 0:
            # in that case, delete datapoints until difference is 0
            for _ in range(0, diff):
                self.__plotframe2.delete(self.__plot2_lines[0])
                self.__plot2_lines.pop(0)
        return

    def update_aoaframe(self, packet):
        """update_aoaframe is a method that updates
        the visual bar graph displaying AOA"""

        scale = 5  # 5 px/degree --> 30 deg == full bar
        # calculate new coordinates for the corners of the bar
        self.__aoaframe.coords("aoabar",
                               [0, 150, 30, 150,
                                30, 150-(scale*packet["AOA"]),
                                0, 150 - (scale*packet["AOA"])])
        # values greater than 30 degrees make the bar bright red
        if abs(packet["AOA"]) > 30:
            self.__aoaframe.itemconfig("aoabar", fill="#800000")
            return
        # values lesser than 30 degrees are a percentage of 30 degrees
        # --> apply that percentage in reverse to amount of green in RGB color
        color = hex(abs(int(abs(packet["AOA"]) / 30*255) - 0xff)).lstrip('0')
        color = color.lstrip('x')
        if len(color) == 1:
            color = '0'+color
        self.__aoaframe.itemconfig("aoabar", fill="#80{}00".format(color))
        # make sure the bar does not overlap the zero-level line
        self.__aoaframe.lower("aoabar")
        return

    def update_loadframe(self, packet):
        """update_loadframe is a method that updates
        the visual bar graph displaying load on wings"""

        scale = 50  # 50 px/g --> 3g == full bar
        # calculate new coordinates for the corners of the bar
        self.__loadframe.coords("loadbar",
                                [0, 150, 30, 150,
                                 30, 150-(scale*packet["LOA"]),
                                 0, 150 - (scale*packet["LOA"])])
        # values greater than 3 g make the bar bright red
        if abs(packet["LOA"]) > 3:
            self.__loadframe.itemconfig("loadbar", fill="#800000")
            return
        # values lesser than 3 g are a percentage of 3 g
        # --> apply that percentage in reverse to amount of green in RGB color
        color = hex(abs(int(abs(packet["LOA"]) / 3*255) - 0xff)).lstrip('0')
        color = color.lstrip('x')
        if len(color) == 1:
            color = '0'+color
        self.__loadframe.itemconfig("loadbar", fill="#80{}00".format(color))
        # make sure the bar does not overlap the zero-level line
        self.__loadframe.lower("loadbar")
        return

    def update_inclframe(self, packet):
        """update_inclframe is a method that updates
        the visual absolute inclination display contents"""

        scale = 2.2222  # 2.22 px/degree --> 90 FOV
        # calculate new cordinates for ground sprite
        # first apply PITCH to a sprite with 0 ROLL
        y_offset = packet["PTC"] * scale
        newxy = [-100, int(100+y_offset), 300, int(100+y_offset),
                 300, 300, -100, 300]

        # get the radian value of ROLL
        deg = packet["ROL"]
        rad = (math.pi / 180) * deg

        for i in range(0, 4):
            x_coord = newxy[i*2]
            y_coord = newxy[i*2+1]
            # x_and_y is a complex number containing
            # the x value in the real part and the y value in the img part
            x_and_y = complex(x_coord, y_coord)
            offset = complex(100, 100)  # center offset packaged into complex
            # comp_angle is the radian ROLL packaged into a complex number
            # with the absolute value being 1
            comp_angle = complex(math.cos(-rad), math.sin(-rad))
            # Multiplying the offsetted coordinates with the angle does not
            # move them further from the centerpoint because the absolute value
            # of the angle is 1. The coordinates are merely rotated around it.
            v_comp = comp_angle * (x_and_y - offset) + offset
            # every even index is an x value
            newxy[i*2] = v_comp.real
            # every odd index is a y value
            newxy[i*2+1] = v_comp.imag
        # apply the newly calculated coordinates
        self.__inclframe.coords("gnd", *newxy)
        return

if __name__ == '__main__':
    EnvelopeWindow()
