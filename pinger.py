#Finished

from socket import *
import os
import sys
import struct
import time
import select
import binascii
from statistics import stdev
# Should use stdev

ICMP_ECHO_REQUEST = 8
pktRTT = []
pktSent = 0
pktRec = 0

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    global pktRec, pktRTT
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start

        header = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", header)
        if packetID == ID:
          x = struct.calcsize('d')
          data = struct.unpack('d', recPacket[28:28 + x])[0]
          pktRec += 1
          return timeReceived - data

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."
            

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    global pktSent

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    pktSent += 1

    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    pktRTT.append(delay)
    return delay


def ping(host, timeout=1):
    
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    
   
    # Calculate vars values and return them
    #packet_min = min(pktRTT)
    #print(pktRTT)
    #packet_avg = sum(pktRTT)/len(pktRTT)
    #packet_max = max(pktRTT)
    stdev_var = 1
    #vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2))]
    # Send ping requests to a server separated by approximately one second
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)  # one second
    
    #for x in range(len(pktRTT)):
     #   print("----------")
      #  print(pktRTT[x])
    #print("\n\n\n ------- \n\n\n")

    packet_min = min(pktRTT) * 1000
    #print(packet_min)
    packet_avg = sum(pktRTT)/len(pktRTT) * 1000
    #print(packet_avg)
    packet_max = max(pktRTT) * 1000
    #print(packet_max)
    stdev_var = stdev(pktRTT) * 1000
    #print(stdev_var)
    vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)), str(round(stdev_var,2))]

    return vars

if __name__ == '__main__':
    ping("google.co.il")