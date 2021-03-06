"""This module contains the visul interface window that displays
all the gathered and plotted data from the simulator"""

import math

from tkinter import Tk, Label, Frame, Canvas, PhotoImage, Button  # , Entry
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
        self.__root.geometry("1366x748")
        self.__root.config(background="#242424")
        self.__baseframe = Frame(self.__root, bg="#242424")
        self.__baseframe.pack()

        # datapoints (plot lines) are stored in lists
        self.__maxdatapoints = 3000
        self.__plot1_lines = []
        self.__plot2_lines = []
        self.__controlplot_lines = []
        self.__stop = False

        # plot confidence elements
        self.__plot1_fullflaps_confidence_lines = []
        self.__plot1_fullflaps_confidence_texts = []
        self.__plot1_apprflaps_confidence_lines = []
        self.__plot1_apprflaps_confidence_texts = []
        self.__plot1_noflaps_confidence_lines = []
        self.__plot1_noflaps_confidence_texts = []

        # plot2 no flaps elements
        self.__plot2_no_flap_lines = []
        self.__plot2_no_flap_texts = []

        # plot2 approach flaps elements
        self.__plot2_appr_flap_lines = []
        self.__plot2_appr_flap_texts = []

        # plot2 full flaps elements
        self.__plot2_full_flap_lines = []
        self.__plot2_full_flap_texts = []

        # initializing all window elements
        self.__init_titles()
        self.__init_logframe()
        self.__init_plotframe()
        self.__init_plotframe2()
        self.__init_aoaframe()
        self.__init_loadframe()
        self.__init_inclframe()
        self.__init_controlframes()
        self.__init_widgets()

        # previous values of some data are kept track of
        self.__oldvelocity = None
        self.__oldload = None
        self.__oldaoa = None
        self.__oldsds = None
        self.__oldele = None
        self.__oldail = None
        self.__old_tcp_packet = {"ROL": 0.0, "PTC": 0.0, "HDG": 0.0,
                                 "AOA": 0.0, "SDS": 0.0, "LOA": 0.0,
                                 "ASP": 0.0, "FLP": 0.0}
        self.__old_analog_packets = []
        for _ in range(0, 8):
            self.__old_analog_packets\
                .append({"ELE": 0.0, "AIL": 0.0, "RUD": 0.0})

        # initializing input with 0 being TCP packets, 1 being UDP packets
        # and 2 being pre-recorded data
        data_input = 0
        if data_input == 0:
            self.__hdr = HexDumpReader()
            self.__baseframe.after(100, self.gather_data)
            self.__rx = UDPReceiver()
        elif data_input == 1:
            self.__rx = UDPReceiver()
            self.__log = open("testi2.log", "r")
            self.__baseframe.after(100, self.read_log)

        # self.__t0 = float(time.time())

        # fire up the rootwindow
        self.__baseframe.mainloop()

        return

    def __init_titles(self):
        """init_titles() is a method that creates titles
        and some strucural elements on the root window"""

        # titles
        Label(self.__baseframe, text="Value log", bg="#242424", fg="white")\
            .grid(row=1, column=1, columnspan=4)
        Label(self.__baseframe, text="AOA bar", justify="left",
              bg="#242424", fg="white") \
            .grid(row=4, column=4, sticky="w")
        Label(self.__baseframe, text="Load bar", justify="right",
              bg="#242424", fg="white") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__baseframe, text="Sideslip-Angle of Attack plot",
              justify="right", bg="#242424", fg="white")\
            .grid(row=1, column=5, columnspan=5, sticky="s")
        Label(self.__baseframe, text="Airspeed-Load plot", justify="right",
              bg="#242424", fg="white") \
            .grid(row=1, column=10, columnspan=2, sticky="s")
        Label(self.__baseframe, text="Load bar", justify="right",
              bg="#242424", fg="white") \
            .grid(row=4, column=1, sticky="e")
        Label(self.__baseframe, text="Absolute inclination",
              bg="#242424", fg="white")\
            .grid(row=6, column=1, columnspan=4)
        Label(self.__baseframe, text="Elevator and\nAileron position",
              justify="left", bg="#242424", fg="white")\
            .grid(row=7, rowspan=4, column=11, sticky="w")
        Label(self.__baseframe, text="Rudder position",
              bg="#242424", fg="white") \
            .grid(row=11, rowspan=1, column=11, sticky="w")
        # empty labels as structural dividers
        Label(self.__baseframe, height=0, bg="#242424", fg="white")\
            .grid(row=3, column=1, columnspan=4)
        Label(self.__baseframe, height=0, bg="#242424", fg="white")\
            .grid(row=5, column=1, columnspan=4)
        return

    def __init_logframe(self):
        """init_logframe() is a method that creates
        a frame for showing flight data values"""

        # init the frame
        self.__logframe \
            = Frame(self.__baseframe, borderwidth=4, relief="sunken",
                    bg="#242424")
        self.__logframe.grid(row=2, column=1, columnspan=4, sticky="n")
        self.__logframe.grid_propagate(0)
        self.__logframe_contents = dict()
        # headers for values
        self.__logframe_contents["headers"] \
            = Label(self.__logframe,
                    text="ROLL:\t\nPITCH:\t\nHDG:\t\nAOA:\t\n"
                         "SIDESLP:\t\nLOAD:\t\nAIRSPD:\t\nFLAPS:\t",
                    justify="left", bg='grey', fg="white")
        self.__logframe_contents["headers"].pack(side="left")
        # default values before receiving data are "n/a"
        self.__logframe_contents["values"] \
            = Label(self.__logframe,
                    text="n/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a\nn/a",
                    justify="right", bg='grey', fg="white")
        self.__logframe_contents["values"].pack(side="right")
        return

    def __init_plotframe(self):
        """init_plotframe() is a method that creates
        a frame for plotting the AOA-ROLL -graph"""

        offset = (250, 350)
        aoascale = 11.67  # 11.67 px/degree --> 30 degrees/positive halfplot
        sdsscale = 16.67  # 16.67 px/degree --> 15 degrees/positive halfplot
        aoa_mp = 20  # max positive aoa
        aoa_mn = 12  # max negative aoa

        # init the frame
        self.__plotframe = Canvas(self.__baseframe, height=500, width=500,
                                  borderwidth=4, relief="sunken", bg="#0f228b")
        self.__plotframe.grid(row=2, rowspan=5, column=5, columnspan=5,
                              sticky="n")
        # nice little fade to black on the background
        self.img = PhotoImage(file="images/graphbg.gif")
        self.__plotframe.create_image(0, 0, image=self.img, anchor="nw")
        self.__plotframe.grid_propagate(0)
        # unit markers
        for deg in range(-4, 6):
            deg *= 5
            self.__plotframe.create_line(0, offset[1] - deg * aoascale, 505,
                                         offset[1] - deg * aoascale, dash=4)
            self.__plotframe.create_text(40, offset[1] - deg * aoascale - 2,
                                         text="{}".format(deg), anchor="se")
        for deg in range(-2, 3):
            deg *= 5
            self.__plotframe.create_line(offset[0] + deg * sdsscale, 0,
                                         offset[0] + deg * sdsscale, 605,
                                         dash=4)
            self.__plotframe.create_text(offset[0] + deg * sdsscale + 5, 465,
                                         text="{}".format(deg), anchor="sw")
        # plot axis
        self.__plotframe.create_line(offset[0], 0, offset[0], 505,
                                     fill="white")
        self.__plotframe.create_line(0, offset[1], 505, offset[1],
                                     fill="white")
        # origin dot
        self.__plotframe.create_oval(offset[0]-2, offset[1]-2,
                                     offset[0]+2, offset[1]+2, fill="white",
                                     tags="origin")
        # moving target dot
        self.__plotframe.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                     tags="dot")
        # axis legend
        self.__plotframe.create_text(500, offset[1]+20,
                                     text="Sideslip (degrees)",
                                     anchor="se", fill="white")
        self.__plotframe.create_text(offset[0]+5, 15,
                                     text="Angle of attack (degrees)",
                                     anchor="nw", fill="white")
        # limit lines
        # max positive aoa
        self.__plotframe.create_line(0, offset[1] - aoa_mp * aoascale, 505,
                                     offset[1] - aoa_mp * aoascale,
                                     fill="red", width=2)
        self.__plotframe.create_text(140, offset[1] - aoa_mp * aoascale - 2,
                                     text="Max (+) AOA",
                                     anchor="se", fill="red")
        # max negative aoa
        self.__plotframe.create_line(0, offset[1] + aoa_mn * aoascale, 505,
                                     offset[1] + aoa_mn * aoascale,
                                     fill="red", width=2)
        self.__plotframe.create_text(140, offset[1] + aoa_mn * aoascale - 2,
                                     text="Max (-) AOA",
                                     anchor="se", fill="red")
        # confidence lines
        sds_aoa_pair1 = ((0, -1.9), (1.1, -1.9), (6.2, 0.1), (9.8, 2.3),
                         (8.4, 4.1), (7.5, 7), (6.1, 8.8), (4.8, 9.2),
                         (4.8, 13.5), (4.5, 13.9), (0, 13.9))
        sds_aoa_pair2 = ((0, -4), (10, -4), (10, 12),
                         (7, 12), (7, 15), (0, 15))
        sds_aoa_pair3 = ((0, -12), (4, -12), (4, -4),
                         (4, 15), (4, 20), (0, 20))
        for polarity in (1, -1):
            for pairnmbr in range(0, 10):
                self.__plot1_fullflaps_confidence_lines.append(
                    self.__plotframe
                        .create_line(offset[0] + polarity
                                     * sds_aoa_pair1[pairnmbr][0] * sdsscale,
                                     offset[1] + sds_aoa_pair1[pairnmbr][1]
                                     * -aoascale,
                                     offset[0] + polarity
                                     * sds_aoa_pair1[pairnmbr+1][0] * sdsscale,
                                     offset[1] + sds_aoa_pair1[pairnmbr+1][1]
                                     * -aoascale,
                                     fill="green", width=2))
            for pairnmbr in range(0, 5):
                self.__plot1_fullflaps_confidence_lines.append(
                    self.__plotframe
                        .create_line(offset[0] + polarity
                                     * sds_aoa_pair2[pairnmbr][0] * sdsscale,
                                     offset[1] + sds_aoa_pair2[pairnmbr][1]
                                     * -aoascale,
                                     offset[0] + polarity
                                     * sds_aoa_pair2[pairnmbr+1][0] * sdsscale,
                                     offset[1] + sds_aoa_pair2[pairnmbr+1][1]
                                     * -aoascale,
                                     fill="yellow", width=2))
                if pairnmbr == 2:
                    continue
                self.__plot1_fullflaps_confidence_lines.append(
                    self.__plotframe
                        .create_line(offset[0] + polarity
                                     * sds_aoa_pair3[pairnmbr][0] * sdsscale,
                                     offset[1] + sds_aoa_pair3[pairnmbr][1]
                                     * -aoascale,
                                     offset[0] + polarity
                                     * sds_aoa_pair3[pairnmbr+1][0] * sdsscale,
                                     offset[1] + sds_aoa_pair3[pairnmbr+1][1]
                                     * -aoascale,
                                     fill="yellow", width=2, dash=8))
        # confidence line legend
        self.__plot1_fullflaps_confidence_texts \
            .append(self.__plotframe
                    .create_text(500, offset[1]-45,
                                 text="High confidence",
                                 anchor="se", fill="green"))
        self.__plot1_fullflaps_confidence_texts \
            .append(self.__plotframe
                    .create_text(502, offset[1]-143,
                                 text="Medium confidence",
                                 anchor="se", fill="yellow"))
        self.__plot1_fullflaps_confidence_texts \
            .append(self.__plotframe
                    .create_text(500, offset[1]-235,
                                 text="Extended medium confidence",
                                 anchor="se", fill="yellow"))
        # init the target dot to origin
        self.__plotframe.move("dot", offset[0]-5, offset[1]-5)
        return

    def __init_plotframe2(self):
        """init_plotframe2() is a method that creates
        a frame for plotting the AIRSPEED-LOAD -graph"""

        # scales
        aspscale = 1.5  # 1.5 px/kt --> 300 kts/positive halfplot
        vmo = 259  # max operating speed
        vmfd = 157  # max flaps down speed
        vmaf = 200  # max appr flaps speed
        vmm = 181  # design maneuvering speed
        nss = 99  # normal stall speed
        afss = 89  # approach flaps stall speed
        fdss = 82  # flaps down stall speed
        loascale = 87.5  # 87.5 px/g --> 4 g/positive halfplot
        gmp = 3.10  # max positive load
        gmn = 1.24  # max negative load
        offset = (50, 350)  # centerpoint offset

        # init the frame
        self.__plotframe2 = Canvas(self.__baseframe, height=500, width=500,
                                   borderwidth=4, relief="sunken",
                                   bg="#0f228b")
        self.__plotframe2.grid(row=2, rowspan=5, column=10, columnspan=2,
                               sticky="nw")
        # nice little fade to black on the background
        self.__plotframe2.create_image(0, 0, image=self.img, anchor="nw")
        # unit markers
        for loa in range(-2, 5):
            self.__plotframe2.create_line(0, offset[1] - loa * loascale, 505,
                                          offset[1] - loa * loascale, dash=4)
            self.__plotframe2.create_text(40, offset[1] - loa * loascale - 2,
                                          text="{}".format(loa), anchor="se")
        for spd in range(0, 6):
            spd *= 50
            self.__plotframe2.create_line(offset[0] + spd * aspscale, 0,
                                          offset[0] + spd * aspscale, 605,
                                          dash=4)
            self.__plotframe2.create_text(offset[0] + spd * aspscale + 5, 437,
                                          text="{}".format(spd), anchor="sw")
        # plot axis
        self.__plotframe2.create_line(0, offset[1], 605, offset[1],
                                      fill="white")
        self.__plotframe2.create_line(offset[0], 0, offset[0], 605,
                                      fill="white")

        # limit lines
        # max operating speed
        self.__plot2_no_flap_lines\
            .append(self.__plotframe2
                    .create_line(offset[0] + vmo*aspscale, 65,
                                 offset[0] + vmo*aspscale, 605,
                                 fill="red", width=2))
        self.__plot2_no_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + vmo*aspscale - 5, 500,
                                 text="Max operating\nspeed (no flaps)",
                                 anchor="se", fill="red", justify="right"))
        self.__plot2_full_flap_lines\
            .append(self.__plotframe2
                    .create_line(offset[0] + vmfd*aspscale, 65,
                                 offset[0] + vmfd*aspscale, 605,
                                 fill="red", width=2, state="hidden"))
        self.__plot2_full_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + vmfd*aspscale + 5, 500,
                                 text="Max operating\nspeed (full flaps)",
                                 anchor="sw", fill="red", justify="left",
                                 state="hidden"))
        self.__plot2_appr_flap_lines\
            .append(self.__plotframe2
                    .create_line(offset[0] + vmaf*aspscale, 65,
                                 offset[0] + vmaf*aspscale, 605,
                                 fill="red", width=2, state="hidden"))
        self.__plot2_appr_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + vmaf*aspscale - 5, 500,
                                 text="Max operating\nspeed (appr flaps)",
                                 anchor="se", fill="red", justify="right",
                                 state="hidden"))
        # stall speed
        self.__plot2_no_flap_lines \
            .append(self.__plotframe2
                    .create_line(offset[0] + nss * aspscale, 240,
                                 offset[0] + nss * aspscale, 605,
                                 fill="red", width=2))
        self.__plot2_no_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + nss * aspscale - 5, 500,
                                 text="Normal stall speed\n(no flaps)",
                                 anchor="se", fill="red", justify="right"))
        self.__plot2_appr_flap_lines \
            .append(self.__plotframe2
                    .create_line(offset[0] + afss * aspscale, 240,
                                 offset[0] + afss * aspscale, 605,
                                 fill="red", width=2, state="hidden"))
        self.__plot2_appr_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + afss * aspscale - 5, 500,
                                 text="Normal stall speed\n(appr flaps)",
                                 anchor="se", fill="red", justify="right",
                                 state="hidden"))
        self.__plot2_full_flap_lines \
            .append(self.__plotframe2
                    .create_line(offset[0] + fdss * aspscale, 240,
                                 offset[0] + fdss * aspscale, 605,
                                 fill="red", width=2, state="hidden"))
        self.__plot2_full_flap_texts \
            .append(self.__plotframe2
                    .create_text(offset[0] + fdss * aspscale - 5, 500,
                                 text="Normal stall speed\n(full flaps)",
                                 anchor="se", fill="red", justify="right",
                                 state="hidden"))
        # max maneuver speed
        self.__plotframe2.create_line(offset[0] + vmm*aspscale, 0,
                                      offset[0] + vmm*aspscale, 605,
                                      fill="green", dash=4)
        self.__plotframe2.create_text(offset[0] + vmm*aspscale - 5, 45,
                                      text="Maneuvering\nspeed",
                                      anchor="se", fill="green",
                                      justify="right")

        # max positive load
        self.__plotframe2.create_line(200, offset[1] - gmp*loascale, 605,
                                      offset[1] - gmp * loascale,
                                      fill="red", width=2)
        self.__plotframe2.create_text(500, offset[1] - gmp*loascale - 2,
                                      text="Max\n(+) load",
                                      anchor="se", fill="red", justify="right")
        # max negative load
        self.__plotframe2.create_line(160, offset[1] + gmn*loascale, 605,
                                      offset[1] + gmn * loascale,
                                      fill="red", width=2)
        self.__plotframe2.create_text(500, offset[1] + gmn*loascale - 2,
                                      text="Max\n(-) load",
                                      anchor="se", fill="red", justify="right")
        old_y = 80
        x = 150
        while x < 281:  # no flaps
            y = 0.00333214*(x**2) + 0.0944*x
            self.__plot2_no_flap_lines \
                .append(self.__plotframe2
                        .create_line(offset[0]+x-10, offset[1]-old_y,
                                     offset[0]+x, offset[1]-y,
                                     fill="red", width=2))
            old_y = y
            x += 10
        old_y = 75
        x = 125
        while x < 281:  # approach flaps
            y = 0.00249*(x**2) + 0.322988*x
            self.__plot2_appr_flap_lines \
                .append(self.__plotframe2
                        .create_line(offset[0]+x-5, offset[1]-old_y,
                                     offset[0]+x, offset[1]-y,
                                     fill="red", width=2, state="hidden"))
            old_y = y
            x += 5
        old_y = 70
        x = 112
        while x < 251:  # full flaps
            y = 0.00391*(x**2) + 0.22985*x
            self.__plot2_full_flap_lines \
                .append(self.__plotframe2
                        .create_line(offset[0]+x-5, offset[1]-old_y,
                                     offset[0]+x, offset[1]-y,
                                     fill="red", width=2, state="hidden"))
            old_y = y
            x += 5

        # origin dot
        self.__plotframe2.create_oval(offset[0]-2, offset[1]-2,
                                      offset[0]+2, offset[1]+2, fill="white",
                                      tags="origin")
        # moving target dot
        self.__plotframe2.create_oval(0, 0, 10, 10, fill="red", outline="red",
                                      tags="dot")
        # axis legend
        self.__plotframe2.create_text(500, offset[1]-2,
                                      text="Airspeed\n(knots)",
                                      anchor="se", fill="white")
        self.__plotframe2.create_text(offset[0]+5, 15,
                                      text="G load (g)",
                                      anchor="nw", fill="white")
        # init the target dot to origin
        self.__plotframe2.move("dot", offset[0]-5, offset[1]-5)
        return

    def __init_aoaframe(self):
        """init_aoaframe() is a method that creates
        a frame and a bar for displaying the ANGLE OF ATTACK"""

        # init the frame
        self.__aoaframe = Canvas(self.__baseframe, width=25, height=300,
                                 borderwidth=4,
                                 relief="sunken", bg="grey")
        self.__aoaframe.grid(row=4, column=3, sticky="nw")
        # create a zero-level line
        self.__aoaframe.create_line(0, 150, 30, 150, fill="#242424")
        # create the bar as a stretching polygon
        self.__aoaframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                       fill="#005a08", tags="aoabar")
        return

    def __init_loadframe(self):
        """init_aoaframe() is a method that creates
        a frame and a bar for displaying the LOAD"""

        # init the frame
        self.__loadframe = Canvas(self.__baseframe, width=25, height=300,
                                  borderwidth=4,
                                  relief="sunken", bg="grey")
        self.__loadframe.grid(row=4, column=2, sticky="ne")
        # create a zero-level line
        self.__loadframe.create_line(0, 150, 30, 150, fill="#242424")
        # create the bar as a stretching polygon
        self.__loadframe.create_polygon(0, 150, 30, 150, 30, 150, 0, 150,
                                        fill="#005a08", tags="loadbar")
        return

    def __init_inclframe(self):
        """init_inclframe() is a method that creates a frame and a visual
        horizon for displaying the absolute inclination of the aeroplane"""

        # init the frame
        self.__inclframe = Canvas(self.__baseframe, width=200, height=200,
                                  borderwidth=4,
                                  relief="sunken", bg="#9ea9fe")
        self.__inclframe.grid(row=7, rowspan=6,
                              column=1, columnspan=4, sticky="n")
        # create the crossbar
        self.__inclframe.create_line(30, 100, 90, 100,
                                     fill="#242424", width=2)
        self.__inclframe.create_line(90, 100, 90, 110,
                                     fill="#242424", width=2)
        self.__inclframe.create_line(110, 100, 110, 110,
                                     fill="#242424", width=2)
        self.__inclframe.create_line(170, 100, 110, 100,
                                     fill="#242424", width=2)
        self.__inclframe.create_oval(99, 99, 101, 101)
        # create a tuple list for ground sprite coordinates
        self.__gndxy = [(-100, 100), (300, 100), (300, 300), (-100, 300)]
        # create ground/horizon as a polygon
        self.__gnd = self.__inclframe \
            .create_polygon(self.__gndxy, fill="#8c603d", tags="gnd")
        # make sure ground is behind crossbar
        self.__inclframe.lower("gnd")
        return

    def __init_controlframes(self):
        """init_controlframe is a method that creates two frames
        that indicate current controls position."""

        offset1 = (200, 50)
        offset2 = (200, 14)

        # init the 1st frame
        self.__controlframe1 = Canvas(self.__baseframe, width=400, height=150,
                                      borderwidth=4,
                                      relief="sunken", bg="#0f228b")
        self.__controlframe1.grid(row=7, rowspan=4, column=10, stick="w")
        # nice little fade to black on the background
        self.img2 = PhotoImage(file="images/graphbg_c.gif")
        self.__controlframe1.create_image(0, 0, image=self.img2, anchor="nw")

        # axis
        self.__controlframe1.create_line(0, offset1[1], 405, offset1[1],
                                         fill="white")
        self.__controlframe1.create_line(200, 0, 200, 155, fill="white")
        # axis legend
        self.__controlframe1.create_text(400, offset1[1] - 2,
                                         text="RT", anchor="se", fill="white")
        self.__controlframe1.create_text(offset1[0] + 5, 8,
                                         text="DN", anchor="nw", fill="white")
        self.__controlframe1.create_text(10, offset1[1] - 2,
                                         text="LT", anchor="sw", fill="white")
        self.__controlframe1.create_text(offset1[0] + 5, 150,
                                         text="UP", anchor="sw", fill="white")

        # origin dot
        self.__controlframe1.create_oval(offset1[0] - 2, offset1[1] - 2,
                                         offset1[0] + 2, offset1[1] + 2,
                                         fill="white",
                                         tags="origin")
        # moving target dot
        self.__controlframe1.create_oval(offset1[0] - 5, offset1[1] - 5,
                                         offset1[0] + 5, offset1[1] + 5,
                                         fill="red", outline="red", tags="dot")

        # init the 2nd frame
        self.__controlframe2 = Canvas(self.__baseframe, width=400, height=20,
                                      borderwidth=4,
                                      relief="sunken", bg="#0f228b")
        self.__controlframe2.grid(row=11, column=10, stick="w")
        # axis
        self.__controlframe2.create_line(200, 0, 200, 25, fill="white")
        # axis legend
        self.__controlframe2.create_text(400, offset2[1],
                                         text="RT", anchor="e", fill="white")
        self.__controlframe2.create_text(10, offset2[1],
                                         text="LT", anchor="w", fill="white")
        # moving target dot
        self.__controlframe2\
            .create_polygon(offset2[0]-8, offset2[1], offset2[0], offset2[1]-8,
                            offset2[0]+8, offset2[1], offset2[0], offset2[1]+8,
                            fill="red", outline="red", tags="diamond")

        return

    def __init_sdslpframe(self):
        """init_sdslpframe is a method that creates
        a frame to indicate ship's sideslip."""

        offset = (200, 14)
        scale = 13.3333  # 13.33 px/degree --> 15 degrees/positive halfplot

        # init the frame
        self.__sdslpframe = Canvas(self.__baseframe, width=400, height=20,
                                   borderwidth=4,
                                   relief="sunken", bg="#0f228b")
        self.__sdslpframe.grid(row=9, column=5, columnspan=5)
        # unit markers
        for deg in range(-4, 5):
            deg *= 5
            self.__sdslpframe.create_line(offset[0] + deg * scale, 0,
                                          offset[0] + deg * scale, 30, dash=4)
            self.__sdslpframe.create_text(offset[0] + deg * scale + 5, 14,
                                          text="{}".format(deg), anchor="w")
        # axis
        self.__sdslpframe.create_line(200, 0, 200, 25, fill="white")

        # moving target dot
        self.__sdslpframe\
            .create_polygon(offset[0]-8, offset[1], offset[0], offset[1]-8,
                            offset[0]+8, offset[1], offset[0], offset[1]+8,
                            fill="red", outline="red", tags="diamond")
        return

    def __init_widgets(self):
        """init_widgets() is a method that creates all utility widgets,
        such as buttons and entry boxes"""

        # create a stop button and assign command
        self.__stopbutton = Button(self.__baseframe, text="Stop",
                                   command=self.__toggle_stop,
                                   height=4, width=10,
                                   activebackground="red", bg="grey")
        self.__stopbutton.grid(row=9, column=5)

        # create a clear button and assign command
        self.__clearbutton = Button(self.__baseframe, text="Clear",
                                    command=self.clear_plots,
                                    height=4, width=10,
                                    activebackground="blue", bg="grey")
        self.__clearbutton.grid(row=9, column=9)

        # # create a text label describing the purpose of the entry box
        # Label(self.__root, text="Limit data points to last:") \
        #     .grid(row=10, rowspan=2, column=6, sticky="e")
        # # bind the variable vcmd to a method call for validation
        # vcmd = self.__root.register(self.validate_entry)
        # # create an entrybox for changing the maximum datapoint limit
        # self.__datapt_entry \
        #     = Entry(self.__root, validate='key',validatecommand=(vcmd, '%S'),
        #             justify="right", width=7)
        # # default value for entrybox is 3000
        # self.__datapt_entry.insert(-1, self.__maxdatapoints)
        # self.__datapt_entry.grid(row=10, column=7, rowspan=2)
        #
        # # create a set button for the datapoint limit and assign command
        # self.__setbutton = Button(self.__root, text="Set",
        #                           command=self.set_datapoint_limit)
        # self.__setbutton.grid(row=10, column=8, rowspan=2, sticky="w")
        return

    def clear_plots(self):
        """clear_plots is a method that deletes
        the stored datapoints and lines from the window"""

        try:
            # keep deleting datapoint until they run out, throwing IndexError
            while True:
                self.__plotframe.delete(self.__plot1_lines[0])
                self.__plotframe2.delete(self.__plot2_lines[0])
                self.__controlframe1.delete(self.__controlplot_lines[0])
                self.__plot1_lines.pop(0)
                self.__plot2_lines.pop(0)
                self.__controlplot_lines.pop(0)
        except IndexError:
            return

    # def set_datapoint_limit(self):
    #     """set_datapoint_limit is a method that fetches an integer from
    #     the entry line and sets it to be the current datapoint limit"""
    #
    #     try:
    #         # if the entry contains a sensible integer, set limit
    #         self.__maxdatapoints = int(self.__datapt_entry.get())
    #         self.__setbutton.configure(text="Limit set!", state="disabled")
    #     except ValueError:
    #         # if the entry contains nothing or a weird value, no limit
    #         self.__setbutton.configure(text="No limit", state="disabled")
    #         self.__maxdatapoints = 100000
    #     return

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

    # def validate_entry(self, text):
    #     """validate_entry is a method that checks every char that is added
    #     or removed from the entry line and decides if said character is OK"""
    #
    #     try:
    #         # value change in entry box toggles button disable off
    #         self.__setbutton.configure(text="Set", state="normal")
    #     except AttributeError:
    #         pass
    #     # checking every character in proposed entry if they are ok
    #     for char in text:
    #         if char in '0123456789':
    #             continue
    #         else:
    #             return False
    #     try:
    #         # finally checking if the characters are ok as a whole
    #         int(text)
    #         return True
    #     except ValueError:
    #         return False

    def listen_udp(self):
        """listen_udp() is a method that calls UDPReceiver's method
        to receive packets through UDP"""

        packet = self.__rx.listen_to_port()
        if packet is not None:
            # display updated values
            self.display_data(packet)
        # read again soon
        self.__baseframe.after(30, self.listen_udp)
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
            print("Timeout!")
        # and if the package is not null, display the data
        # read again soon
        self.__baseframe.after(200, self.read_hexdump)
        return

    def gather_data(self):
        """gather_data() is a method that unites data from two sources."""

        def running_average():
            """running_average() constantly calculates the running average
            of 8 subsequent analog packets to combat
            the analog input's electric noise."""

            aver_packet = {"ELE": 0.0, "AIL": 0.0, "RUD": 0.0}
            for header in ["ELE", "AIL", "RUD"]:
                for i in range(0, 8):
                    aver_packet[header] += self.__old_analog_packets[i][header]
                aver_packet[header] /= 8
            return aver_packet

        # get the analog packet from UDPReceiver
        analog_packet = self.__rx.listen_to_port()
        if analog_packet is None:
            # print("UDP timeout, keeping old analog-packet!")
            analog_packet = self.__old_analog_packets[4]
        else:
            self.__old_analog_packets.append(analog_packet)
            self.__old_analog_packets.pop(0)
            analog_packet = running_average()
        # get the  tcp-packet from HexDumpReader
        try:
            tcp_packet = self.__hdr.read_hexdump()
            if tcp_packet is not None:
                self.__old_tcp_packet = tcp_packet
            else:
                tcp_packet = self.__old_tcp_packet
        except TimeoutError:
            # print("TCP timeout, keeping old tcp-packet!")
            tcp_packet = self.__old_tcp_packet
        # unite the packages
        packet = {**analog_packet, **tcp_packet}

        # display the data
        self.display_data(packet)

        # read again soon
        self.__baseframe.after(100, self.gather_data)
        return

    def read_log(self):
        """read_log() is a method that reads prerecorded packets from a
        text file and sends them onwards, emulating actual traffic"""

        # fetch a line from the file
        data = self.__log.readline()
        # when running out of linces, start over
        if data == '':
            self.__log.close()
            self.__log = open("testi1.log", "r")
        else:
            # strip extra characters away from the line
            data = str(data)
            data = data.strip("b'\\n")
            data = data.split(",")
            # use UDP reader's formatter for packaging
            packet = dict()
            i = 0
            for header in ("FLP", "LOA", "PTC", "AOA", "SDS", "RUD",
                           "ELE", "AIL", "ASP", "HDG", "ROL"):
                try:
                    packet[header] = float(data[i])
                except (ValueError, IndexError):
                    packet[header] = 0.0
                i += 1
            # and if the package is not null, display the data
            if packet:
                self.display_data(packet)
        # read again soon
        self.__baseframe.after(30, self.read_log)
        return

    def display_data(self, packet):
        """display_data() is a method that calls all methods
        that update EnvelopeWindow's UI"""

        # update values only if the stop flag is not raised
        if not self.__stop:
            self.update_logframe(packet)
            self.update_plotframe(packet)
            self.update_aoaframe(packet)
            self.update_inclframe(packet)
            self.update_loadframe(packet)
            self.update_plotframe2(packet)
            self.update_controlframes(packet)
            self.__oldsds = packet["SDS"]
            self.__oldaoa = packet["AOA"]
            self.__oldvelocity = packet["ASP"]
            self.__oldload = packet["LOA"]
            self.__oldele = packet["ELE"]
            self.__oldail = packet["AIL"]

            self.update_limits(packet["FLP"])

        return

    def update_limits(self, flaps):
        """update_limits updates limit lines in plots 1 and 2
        according to the planes flaps position"""

        if flaps < 10:  # no flaps
            for line in self.__plot2_no_flap_lines:
                self.__plotframe2.itemconfig(line, state="normal")
            for text in self.__plot2_no_flap_texts:
                self.__plotframe2.itemconfig(text, state="normal")
            for line in self.__plot2_appr_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_appr_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot2_full_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_full_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot1_noflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="normal")
            for text in self.__plot1_noflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="normal")
            for line in self.__plot1_apprflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_apprflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
            for line in self.__plot1_fullflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_fullflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
        elif flaps < 30:  # approach flaps
            for line in self.__plot2_no_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_no_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot2_appr_flap_lines:
                self.__plotframe2.itemconfig(line, state="normal")
            for text in self.__plot2_appr_flap_texts:
                self.__plotframe2.itemconfig(text, state="normal")
            for line in self.__plot2_full_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_full_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot1_noflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_noflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
            for line in self.__plot1_apprflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="normal")
            for text in self.__plot1_apprflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="normal")
            for line in self.__plot1_fullflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_fullflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
        else:  # full flaps
            for line in self.__plot2_no_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_no_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot2_appr_flap_lines:
                self.__plotframe2.itemconfig(line, state="hidden")
            for text in self.__plot2_appr_flap_texts:
                self.__plotframe2.itemconfig(text, state="hidden")
            for line in self.__plot2_full_flap_lines:
                self.__plotframe2.itemconfig(line, state="normal")
            for text in self.__plot2_full_flap_texts:
                self.__plotframe2.itemconfig(text, state="normal")
            for line in self.__plot1_noflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_noflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
            for line in self.__plot1_apprflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="hidden")
            for text in self.__plot1_apprflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="hidden")
            for line in self.__plot1_fullflaps_confidence_lines:
                self.__plotframe.itemconfig(line, state="normal")
            for text in self.__plot1_fullflaps_confidence_texts:
                self.__plotframe.itemconfig(text, state="normal")

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
                       justify="right", bg='grey')
        return

    def update_plotframe(self, packet):
        """update_plotframe is a method that updates
        the contents of the AOA-ROLL -graph"""

        aoascale = 11.67  # 14 px/degree --> 28.6 degrees/positive halfplot
        sdsscale = 16.67  # 16.67 px/degree --> 15 degrees/positive halfplot
        offset = (250, 350)  # centerpoint offset
        try:
            # create a line from old datapoint to new one
            self.__plot1_lines\
                .append(self.__plotframe
                        .create_line(self.__oldsds * sdsscale + offset[0],
                                     self.__oldaoa * -aoascale + offset[1],
                                     packet["SDS"] * sdsscale + offset[0],
                                     packet["AOA"] * -aoascale + offset[1],
                                     fill="white"))
        # first attempt throws a TypeError, oldvalues being None
        except TypeError:
            pass

        # calculate new coordinates for the target dot
        newxy = [offset[0] - 5 + packet["SDS"] * sdsscale,
                 offset[1] - 5 + -packet["AOA"] * aoascale,
                 offset[0] + 5 + packet["SDS"] * sdsscale,
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

        aspscale = 1.5  # 1.5 px/kt --> 300 kts/positive halfplot
        loascale = 87.5  # 100 px/g --> 4 g/positive halfplot
        offset = (50, 350)  # centerpoint offset
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

        scale = 6  # 6 px/degree --> 25 deg == full bar
        # calculate new coordinates for the corners of the bar
        self.__aoaframe.coords("aoabar",
                               [0, 150, 30, 150,
                                30, 150-(scale*packet["AOA"]),
                                0, 150 - (scale*packet["AOA"])])
        # values greater than 20 degrees make the bar bright red
        if abs(packet["AOA"]) > 20:
            self.__aoaframe.itemconfig("aoabar", fill="#800000")
            return
        # values lesser than 20 degrees are a percentage of 20 degrees
        # --> apply that percentage in reverse to amount of green in RGB color
        color = hex(abs(int(abs(packet["AOA"]) / 20*255) - 0xff)).lstrip('0')
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

    def update_controlframes(self, packet):
        """update_controlrames() is a method thar moves
        the ele-ail target dot and rudder diamond in the control frames."""

        offset1 = (200, 50)
        offset2 = (200, 14)
        ailoffset = 520
        ailscale = 0.4768
        elescale = 0.1960
        eleoffset = 365
        rudscale = 0.55
        rudoffset = 513

        try:
            # create a line from old datapoint to new one
            self.__controlplot_lines\
                .append(self.__controlframe1
                        .create_line(self.__oldail * ailscale - 55,
                                     self.__oldele * elescale - 25,
                                     packet["AIL"] * ailscale - 55,
                                     packet["ELE"] * elescale - 25,
                                     fill="white"))
        # first attempt throws a TypeError, oldvalues being None
        except TypeError:
            pass

        # calculate new coordinates for target dot
        newxy = [offset1[0]-5 + (packet["AIL"] - ailoffset) * ailscale,
                 offset1[1]-5 + (packet["ELE"] - eleoffset) * elescale,
                 offset1[0]+5 + (packet["AIL"] - ailoffset) * ailscale,
                 offset1[1]+5 + (packet["ELE"] - eleoffset) * elescale]
        # move the target dot
        self.__controlframe1.coords("dot", *newxy)
        self.__controlframe1.lift("dot")

        # calculate new coordinates for the rudder diamond
        newxy = [offset2[0] - 8 + (packet["RUD"] - rudoffset)
                 * rudscale, offset2[1],
                 offset2[0] + (packet["RUD"] - rudoffset)
                 * rudscale, offset2[1] - 8,
                 offset2[0] + 8 + (packet["RUD"] - rudoffset)
                 * rudscale, offset2[1],
                 offset2[0] + (packet["RUD"] - rudoffset)
                 * rudscale, offset2[1] + 8]
        # move the rudder diamond
        self.__controlframe2.coords("diamond", *newxy)
        self.__controlframe2.lift("diamond")

        # check if the amount of datapoints is over the limit
        diff = len(self.__controlplot_lines) - self.__maxdatapoints
        if diff > 0:
            # in that case, delete datapoints until difference is 0
            for _ in range(0, diff):
                self.__controlframe1.delete(self.__controlplot_lines[0])
                self.__controlplot_lines.pop(0)
        return

    def update_sdslpframe(self, packet):
        """update_sdslpframe() is a method that moves the diamond
        indicating the ship's sideslip."""

        offset = (200, 14)
        scale = 13.3333  # 13.33 px/degree --> 15 degrees/positive halfplot

        # calculate new coordinates for the target diamond
        newxy = [offset[0]-8 + packet["SDS"]*scale, offset[1],
                 offset[0] + packet["SDS"]*scale, offset[1]-8,
                 offset[0]+8 + packet["SDS"]*scale, offset[1],
                 offset[0] + packet["SDS"]*scale, offset[1]+8]
        # move the target diamond
        self.__sdslpframe.coords("diamond", *newxy)
        self.__sdslpframe.lift("diamond")
        return

if __name__ == '__main__':
    EnvelopeWindow()
