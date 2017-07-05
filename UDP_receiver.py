

import socket


class UDPReceiver:

    def __init__(self):

        # read_config() attempts to read the config.txt file and changes
        # some program parameters if the user so wishes
        def read_config():
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
                except (IndexError, ValueError) as e:
                    print(e, "in config.txt line {}".format(line))
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
        self.__sock.bind((self.__udp_ip, self.__udp_port))
        # after setup, these vars are not needed anymore
        del self.__udp_ip, self.__udp_port
        return

    def listen_to_port(self):
        while True:
            data, addr = self.__sock.recvfrom(1024)
            data = str(data)
            data = data.strip("b'\\n")
            print(data)


if __name__ == '__main__':
    rx = UDPReceiver()
    rx.listen_to_port()
