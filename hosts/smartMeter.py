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

    def __init__(self, params):
        """ Constructor """
        self.meterID = params
        self.currentReading = 0
        self.lastReadingTime = None
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()

    def get_latest_reading(self):
        """ Returns latest reading and registers last timeStamp """
        if self.currentReading >= 0.0:
            self.lastReadingTime = time.time()
            print str(self.lastReadingTime) + ":" + str(self.currentReading) + "Wh\n"
            return self.meterID, self.lastReadingTime, self.currentReading
        else:
            return False

    def __set_last_reading(self, value, time_stamp):
        self.currentReading = value

    def run(self):
        """ Logic that simulates constant meter usage """
        while self.__alive:
            increment = random.uniform(0.0, 0.1) * self.interval
            increment = random.randint(0, 1) * increment

            self.currentReading += increment;
            if self.currentReading == 32454:
                self.currentReading = 0.0

            time.sleep(self.interval)

    def shut_down_meter(self):
        self.__alive = False
        self.thread.join()


# Serialize reading
def format_reading(r):
    # Need to serialize before sending
    json_read = {"id": r[0], "ts": r[1], "reading": r[2]}
    json_string = json.dumps(json_read)
    return json_string


def send_reading(json_reading):
    """ Send reading over the network. """
    try:
        # send reading over TCP socket
        s = socket.socket()
        s.connect((CONCENTRATOR_HOST, PORT))
        s.send(json_reading)
        ack = s.recv(BUFFER_SIZE)
        s.close()
        print "Received:", ack
    except socket.error as err_msg:
        print "Concentrator device (%s) is not responding. Data not sent." % CONCENTRATOR_HOST
        print "Network Error %s" % err_msg
        return False
    return True


def regular(r, interval):
    """ Send reading regularly within given interval."""
    print "Sending regularly"
    while sendFlag:
        sample_reading = r.get_latest_reading()
        if not sample_reading:
            print "corrupted reading"
            continue
        send_reading(format_reading(sample_reading))
        time.sleep(interval)
    print "stopped sending at an interval of %d seconds" % interval
    return


def once(r):
    """ Send Reading once via user input."""
    print "Sending once"
    sample_reading = r.get_latest_reading()
    if not sample_reading:
        print "corrupted reading"
        return
    print send_reading(format_reading(sample_reading))
    return

if __name__ == "__main__":
    sendFlag = False

    if len(sys.argv) < 2:
        meterID = 1
        CONCENTRATOR_HOST = "127.0.0.1"
    elif len(sys.argv) is 2:
        meterID = sys.argv[1]
        CONCENTRATOR_HOST = "127.0.0.1"
    elif len(sys.argv) is 3:
        meterID = sys.argv[1]
        CONCENTRATOR_HOST = sys.argv[2]
    reading = Reading(meterID)

    thread1 = threading.Thread(target=regular, args=(reading, 5))
    # thread1.daemon = True
    print """Welcome to smart meter Daemon. \nPress S to start sending readings at regular intervals
    \npress R to send the current reading right away.
    Press Q to stop sending regularly."""
    while True:
        choice = raw_input('> ')
        # regular readings
         choice == 'S' or choice == 's':
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
            once(reading)
        elif choice == 'X' or choice == 'x':
            sendFlag = False
            if thread1.is_alive():
                thread1.join()
            reading.shut_down_meter()
            print "Goodbye"
            quit()
        else:
            continue
