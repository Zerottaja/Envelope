import socket

UDP_IP = "10.41.3.87"
UDP_PORT = 4444

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    data = str(data)
    data = data.strip("b'\\n")
    print(data)
