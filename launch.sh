#!/bin/sh
clear
echo "Looking for a FIFO-pipe..."
if [ ! -p packet_fifo ]
then
    echo Making a FIFO pipe...
    mkfifo packet_fifo
    echo Done!
fi
echo Launching visual interface...
python3 visual_interface.py &
echo Done!
echo Launching TCP-packet capturing...
tshark -i eno1 -Y "ip.src == 192.9.200.155 and tcp.len == 1024 and (data.data[2] == 11)" -Eheader=n -Tfields -e data.data > packet_fifo
echo Exiting...
