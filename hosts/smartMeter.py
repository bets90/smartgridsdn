#!/usr/bin/python           # This is client.py file
import socket,time,random
from datetime import timedelta

PORT = 8080
BUFFER_SIZE = 1024

class Reading:
    'Reading object with all the necessary data'
    currentReading = 0.0
    lastReadingTime = time.time()
    def __init__(self):
        self.currentReading = 0;
        self.lastReadingTime = time.time()
    def getLatestReading():
        print self.lastReasingTime + ":" + self.currentReading
        return self.lastReadingTime + ":" + self.currentReading
    def setlastReading(value,timeStamp):
        self.currentReading = value

def emulateReading(lastReadingTime):
    time.sleep(10)
    currentReadingTime = time.time()
    interval = int(currentReadingTime - lastReadingTime)
    print "Interval is: %f \n current time is: %f \n last readingTimeis: %f " % (interval, currentReadingTime, lastReadingTime)
    print random.uniform(0.0,0.1) * interval
    return (interval,currentReadingTime)

def sendReadings():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    s.connect((host, PORT))
    s.send("test")
    print "Received:", s.recv(BUFFER_SIZE)
    s.close

if __name__=='__main__':
    reading = Reading()
    emulateReading(reading.lastReadingTime)
    sendReadings()
