#!/bin/sh
clear
if [ ! -p /home/samu/PycharmProjects/Envelope/packet_fifo ]
then
    echo Making a FIFO pipe...
    mkfifo packet_fifo
    echo Done!
fi
echo Launching visual interface...
python3 visual_interface.py &
ping localhost -c 2 > /dev/null
echo Done!
echo Launching TCP-packet capturing...
tshark -i enp0s25 -Y "ip.src == 192.9.200.155 and tcp.len == 1024 and (tcp.segment_data[2] == 21 or data.data[2] == 21)" -Eheader=n -Tfields -e data.data > /home/samu/PycharmProjects/Envelope/packet_fifo
echo Exiting...
