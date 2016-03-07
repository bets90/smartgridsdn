#!/usr/bin/python           # This is client.py file
import socket,time,random
import sys
import threading
import pickle, json
from datetime import timedelta

PORT = 8080
BUFFER_SIZE = 1024
#abstraction of a meter reading
#has attributes to set and get a reading
class Reading:
    'Reading object with all the necessary data'
    meterID = None
    currentReading = 0.0
    # lastReadingTime = time.time()
    interval = 3
    def __init__(self,params):
        """ Constructor """
        self.meterID =  params
        self.currentReading = 0;
        self.lastReadingTime = None

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def getLatestReading(self):
        """ Returns latest reading and registers last timeStamp """
        if self.currentReading >= 0.0:
            self.lastReadingTime = time.time()
            print str(self.lastReadingTime) + ":" + str(self.currentReading) + "Wh\n"
            return (self.lastReadingTime, self.currentReading)
        else:
            return False

    def __setlastReading(value,timeStamp):
        self.currentReading = value
    def run(self):
        """ Logic that simulates constant meter usage """
        while True:
            increment = random.uniform(0.0, 0.1) * self.interval
            increment = random.randint(0,1) * random.randint(0,1) * increment
            #print "increment is : %f" % (increment)
            # increment = float ("{0:.2f}".format(increment))
            self.currentReading += increment;
            if self.currentReading == 32454:
                self.currentReading = 0.0
            #print "Current Reading is: %f " % (self.currentReading)
            time.sleep(self.interval)


# def emulateReading(lastReadingTime):
#     time.sleep(10)
#     currentReadingTime = time.time()
#     interval = int(currentReadingTime - lastReadingTime)
#     print "Interval is: %f \n current time is: %f \n last readingTimeis: %f " % (interval, currentReadingTime, lastReadingTime)
#     print random.uniform(0.0,0.1) * interval
#     return (interval,currentReadingTime)

def sendReadingOnce(r):
    sampleReading = r.getLatestReading()
    if sampleReading == False:
        print "corrupt reading"
        return
    # Need to serializre before sending
    jsonRead = { "id" : r.meterID, "reading" : sampleReading[1], "timeStamp": sampleReading[0]}
    readingString = json.dumps(jsonRead)
    print readingString
    #send reading over TCP socket
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    s.connect((host, PORT))
    s.send(readingString)
    print "Received:", s.recv(BUFFER_SIZE)
    s.close()

def regularReading():
    print "placeholder"

if __name__=='__main__':
    if len(sys.argv) < 2 :
        meterID = 1
    else:
        meterID = sys.argv[1]
    #print 'meterID is: ', sys.argv[1]
    reading = Reading(meterID)

    print 'Welcome to smart meter Daemon Press S to start sending readings at intervals of 60 seconds press R to send the current reading rightaway.'
    choice = raw_input('> ')
    if choice == 'S' or choice == 's':
        # sendReadings()
        print "coming soon"
    elif choice == 'R' or choice == 'r':
        sendReadingOnce(reading)
