"""This module contains the UDP listening class UDPReceiver"""

import socket


class UDPReceiver:
    """UDPReceiver is a class that listens to the specified UDP-port and sends
    the data onwards to it's master class"""

    def __init__(self):

        def read_config():
            """read_config() attempts to read the config.txt file and changes
            some program parameters if the user so wishes"""
            # open the config file
            try:
                fileobject = open("config.txt", 'r')
            except FileNotFoundError:
                fileobject = open("config.txt", 'w')
                fileobject.write("""

ENVELOPE CONFIGURATION:

CONNECTION SETTINGS:
UDP-IP = localhost # default localhost
UDP-port = 4444 # default 4444""")
                fileobject.close()
                return

            while True:
                # read while not at the end of file
                line = fileobject.readline()
                if line == '':
                    break
                # strip away newlines and split with spaces
                line = line.strip("\n ")
                line = line.split('#')[0]
                line = line.replace(" ", "")
                try:
                    if '=' in line:
                        line = line.split("=")
                        if line[0] == "UDP-IP":
                            self.__udp_ip = line[1]
                        elif line[0] == "UDP-port":
                            self.__udp_port = int(line[1])

                # if something's wrong with the config-file, defaults remain
                except (IndexError, ValueError) as conf_err:
                    print(conf_err, "in config.txt line {}".format(line))
                    continue
            fileobject.close()
            return

        # default values
        self.__udp_ip = "localhost"
        self.__udp_port = 4444
        # read config to possibly change defaults
        read_config()

        self.__sock = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)
        self.__sock.settimeout(1)
        try:
            self.__sock.bind((self.__udp_ip, self.__udp_port))
        except OSError as err:
            print("{}. Check connection.".format(err))
        # after setup, these vars are not needed anymore
        del self.__udp_ip, self.__udp_port

        self.__timer = 0

        return

    def listen_to_port(self):
        """listen_to_port() listens to the specified port and sends it
        to the formatter method"""

        import time

        try:
            data = self.__sock.recvfrom(1024)[0]
        except socket.timeout:
            return None
        data = str(data)
        data = data.strip("b'\\n")
        data = data.split(",")
        packet = self.formatter(data)
        # print("dT between packages:", float(time.time()) - self.__timer)
        self.__timer = time.time()
        return packet

    @staticmethod
    def formatter(data):
        """DOCSTRING"""  # TODO Docstring
        packet = dict()
        i = 0
        for header in ("LON", "LAT", "ALT", "ROL", "PTC", "HDG", "AOA"):
            try:
                packet[header] = float(data[i])
            except ValueError:
                print(data[i])
            i += 1
        return packet

if __name__ == '__main__':
    RX = UDPReceiver()
    while True:
        rx_data = RX.listen_to_port()
        print(rx_data)
