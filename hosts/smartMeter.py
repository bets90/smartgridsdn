#!/usr/bin/python
import json
import random
import socket
import sys
import threading
import time

PORT = 8080
BUFFER_SIZE = 1024
flag = False


# abstraction of a meter reading
# has attributes to set and get a reading
class Reading:
    """Reading object with all the necessary data"""
    meterID = None
    currentReading = 0.0
    __alive = True
    interval = 3

    def __init__(self,params):
        """ Constructor """
        self.meterID = params
        self.currentReading = 0
        self.lastReadingTime = None
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def getLatestReading(self):
        """ Returns latest reading and registers last timeStamp """
        if self.currentReading >= 0.0:
            self.lastReadingTime = time.time()
            print str(self.lastReadingTime) + ":" + str(self.currentReading) + "Wh\n"
            return self.meterID, self.lastReadingTime, self.currentReading
        else:
            return False

    def __setlastReading(self, value, timeStamp):
        self.currentReading = value

    def run(self):
        """ Logic that simulates constant meter usage """
        while self.__alive:
            increment = random.uniform(0.0, 0.1) * self.interval
            increment = random.randint(0,1) * increment
            # print "increment is : %f" % (increment)
            # increment = float ("{0:.2f}".format(increment))
            self.currentReading += increment;
            if self.currentReading == 32454:
                self.currentReading = 0.0
            # print "Current Reading is: %f " % (self.currentReading)
            time.sleep(self.interval)

    def shutDownMeter(self):
        self.__alive = False
        self.thread.join()


# Serialize reading
def formatReading (r):
    # Need to serializre before sending
    jsonRead = { "id" : r[0], "ts": r[1], "reading" : r[2]}
    jsonString = json.dumps(jsonRead)
    return jsonString


def sendReading(rj):
    """ Send reading over the network. """
    # send reading over TCP socket
    s = socket.socket()
    host = socket.gethostname()
    s.connect((host, PORT))
    s.send(rj)
    ack = s.recv(BUFFER_SIZE)
    s.close()
    print "Received:", ack
    return ack


def Regular (r, interval):
    """ Send Reading regularly within given interval."""
    print "Sending regularly"
    while sendFlag:
        sampleReading = r.getLatestReading()
        if not sampleReading:
            print "corrupted reading"
            continue
        sendReading(formatReading(sampleReading))
        time.sleep(interval)
    print "stopped sending at an interval of %d seconds" % interval
    return


def Once(r):
    """ Send Reading once via user input."""
    print "Sending once"
    sampleReading = r.getLatestReading()
    if not sampleReading:
        print "corrupted reading"
        return
    print sendReading(formatReading(sampleReading))
    return

if __name__ == "__main__":
    sendFlag = False
    if len(sys.argv) < 2:
        meterID = 1
    else:
        meterID = sys.argv[1]
    reading = Reading(meterID)
    # #print 'meterID is: ', sys.argv[1]
    thread1 = threading.Thread(target=Regular, args=(reading,5))
    # thread1.daemon = True
    print """Welcome to smart meter Daemon. \nPress S to start sending readings at regular intervals \npress R to send the current reading rightaway.
    Press Q to stop sending regularly."""
    while True:
        choice = raw_input('> ')
        # regular readings
        if choice == 'S' or choice == 's':
            sendFlag = True
            if not thread1.is_alive():
                thread1.start()
                # continue
        # stop regular
        elif choice == 'Q' or choice == 'q':
            sendFlag = False
            if thread1.is_alive():
                thread1.join()
        # # send reading once
        elif choice == 'R' or choice == 'r':
            Once(reading)
        elif choice == 'X' or choice == 'x':
            sendFlag = False
            if thread1.is_alive():
                thread1.join()
            reading.shutDownMeter()
            print "Goodbye"
            quit()
        else:
            continue
