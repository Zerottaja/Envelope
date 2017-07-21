
import struct

file = open("myfifo")
while True:
    line = file.readline()
    if line != "":
        line = line.replace(':', '')
        print(struct.unpack('>d', bytes.fromhex(line[208:224]))[0])
        print(line, end='')


###############################################################################
# sudo tshark -Y "ip.src == 192.9.200.155 and tcp.len == 1024 and data.data[2] == 21" -Eheader=n -Tfields -e data.data > /home/samu/PycharmProjects/helloworld/myfifo
###############################################################################
